import logging
import uuid
from datetime import datetime
from datetime import timezone
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

from fastapi import Depends
from fastapi import HTTPException
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from common.error_messages import ErrorMessages
from database import db
from database.models import Machine
from database.models import MachinePickupPoint
from database.models import PickupPoint


class RoutePickupPoint(BaseModel):
    id: uuid.UUID
    travel_time: int  # time_from_previous_point_minutes
    travel_distance: int  # distance_from_previous_pickup_point_meters


class RouteOptimizationResult(BaseModel):
    machine_id: uuid.UUID
    route: list[RoutePickupPoint]
    total_distance: float
    total_time: float
    created_at: datetime


class RouteOptimizationRequest(BaseModel):
    machine_id: uuid.UUID
    start: datetime
    end: datetime


class DistanceTimeResponse(BaseModel):
    distance: float
    time_hours: float


class CalculateDistanceRequest(BaseModel):
    pickup_point1_id: uuid.UUID
    pickup_point2_id: uuid.UUID


class MetricsService:
    def __init__(self, db_session: AsyncSession):
        self.db: AsyncSession = db_session

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    def get_distance_matrix(self, pickup_points: list[PickupPoint]):
        size = len(pickup_points)
        distance_matrix = [[0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if i != j:
                    distance_matrix[i][j] = (
                            abs(pickup_points[i].location['latitude'] - pickup_points[j].location['latitude']) +
                            abs(pickup_points[i].location['longitude'] - pickup_points[j].location['longitude']))
        return distance_matrix

    async def optimize_route(self, request: RouteOptimizationRequest) -> RouteOptimizationResult:
        """
        Based on the Traveling saleman problem solution
        :param request:
        :return:
        """
        machine = (await self.db.execute(select(Machine).filter(Machine.id == request.machine_id))).scalar_one_or_none()
        if not machine:
            raise Exception("Machine not found")

        machine_pickup_points = (await self.db.scalars(
            select(MachinePickupPoint)
            .options(joinedload(MachinePickupPoint.pickup_point))
            .filter(
                MachinePickupPoint.machine_id == request.machine_id,
                MachinePickupPoint.departure_at >= request.start,
                MachinePickupPoint.arrival_at <= request.end
            )
        )).all()

        if not machine_pickup_points:
            raise Exception("No pickup points found for the machine in the specified time range")

        pickup_points = [mpp.pickup_point for mpp in machine_pickup_points]
        distance_matrix = self.get_distance_matrix(pickup_points)
        average_speed_kmh = 60
        average_speed_m_per_s = average_speed_kmh * 1000 / 3600

        manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        time = 'time'
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            int(1e9),  # maximum travel time in seconds (effectively no limit)
            True,  # start cumul to zero
            time)

        time_dimension = routing.GetDimensionOrDie(time)
        for location_idx, machine_pickup_point in enumerate(machine_pickup_points):
            index = manager.NodeToIndex(location_idx)
            stop_time_seconds = max((machine_pickup_point.departure_at - machine_pickup_point.arrival_at).total_seconds(), 1800)  # minimum 30 minutes stop
            arrival_at_timestamp = int(machine_pickup_point.arrival_at.timestamp())
            departure_at_timestamp = int(machine_pickup_point.arrival_at.timestamp()) + int(stop_time_seconds)

            # Logging timestamps for debugging
            logging.info(f"Location Index: {location_idx}")
            logging.info(f"Arrival At: {machine_pickup_point.arrival_at} -> {arrival_at_timestamp}")
            logging.info(f"Departure At: {machine_pickup_point.departure_at} -> {departure_at_timestamp}")
            logging.info(f"Stop Time Seconds: {stop_time_seconds}")

            time_dimension.CumulVar(index).SetRange(
                arrival_at_timestamp,
                departure_at_timestamp
            )

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        assignment = routing.SolveWithParameters(search_parameters)
        if not assignment:
            raise Exception("No solution found")

        route = []
        total_distance = 0
        total_time = 0
        index = routing.Start(0)
        previous_index = None
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            if previous_index is not None:
                distance_from_previous = distance_matrix[manager.IndexToNode(previous_index)][node_index]
                travel_time_from_previous = distance_from_previous / average_speed_m_per_s
            else:
                distance_from_previous = 0
                travel_time_from_previous = 0

            route.append(RoutePickupPoint(
                id=machine_pickup_points[node_index].pickup_point_id,
                travel_time_from_previous_point_minutes=int(travel_time_from_previous / 60),
                distance_from_previous_pickup_point_meters=int(distance_from_previous)
            ))

            previous_index = index
            total_distance += distance_from_previous
            total_time += travel_time_from_previous
            index = assignment.Value(routing.NextVar(index))

        result = RouteOptimizationResult(
            machine_id=machine.id,
            route=route,
            total_distance=total_distance,
            total_time=total_time / 3600,  # convert seconds to hours
            created_at=datetime.now(timezone.utc)
        )

        return result

    async def calculate_distance(self, request: CalculateDistanceRequest):
        """
        Розрахунок відстані в метрах між двома географічними координатами за формулою Гарвіна (Haversine formula)
        :param request:
        :return:
        """
        pickup_point1 = (await self.db.execute(
            select(PickupPoint).filter(PickupPoint.id == request.pickup_point1_id))).scalar_one_or_none()
        pickup_point2 = (await self.db.execute(
            select(PickupPoint).filter(PickupPoint.id == request.pickup_point2_id))).scalar_one_or_none()

        if not pickup_point1 or not pickup_point2:
            raise HTTPException(status_code=404, detail=ErrorMessages.pickup_point.PICKUP_POINT_NOT_FOUND)

        # Extracting the coordinates
        lat1, lon1 = pickup_point1.location['latitude'], pickup_point1.location['longitude']
        lat2, lon2 = pickup_point2.location['latitude'], pickup_point2.location['longitude']

        # Converting latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula to calculate the distance
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        radius_of_earth_km = 6371  # Radius of Earth in kilometers
        distance_km = radius_of_earth_km * c
        distance_meters = distance_km * 1000  # Convert distance to meters

        speed_kmh = 45
        time_hours = distance_km / speed_kmh

        return DistanceTimeResponse(distance=distance_km, time_hours=time_hours)
