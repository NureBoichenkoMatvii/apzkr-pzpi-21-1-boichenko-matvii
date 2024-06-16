import sqlalchemy
from sqladmin import BaseView
from sqladmin import ModelView
from sqladmin import expose
from sqlalchemy import sql
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.requests import Request

from database import db
from database.models import Machine
from database.models import MachineMedicineSlot
from database.models import MachinePickupPoint
from database.models import MachineStatistic
from database.models import Medicine
from database.models import Order
from database.models import OrderMedicine
from database.models import PickupPoint
from database.models import User
from sqladmin.authentication import login_required


class UserView(ModelView, model=User):
    column_list = [User.id, User.email, User.birthdate, User.first_name, User.last_name]
    column_searchable_list = [User.id, User.email, User.first_name, User.last_name]
    column_sortable_list = [User.id, User.email, User.birthdate]


class MachineView(ModelView, model=Machine):
    column_list = [Machine.id, Machine.name, Machine.mac, Machine.location, Machine.admin_user_id,
                   Machine.is_online, Machine.status, Machine.last_maintenance_date]
    column_searchable_list = [Machine.id, Machine.name, Machine.mac]
    column_sortable_list = [Machine.id, Machine.name, Machine.status]


class MachineMedicineSlotView(ModelView, model=MachineMedicineSlot):
    column_list = [MachineMedicineSlot.machine_id, MachineMedicineSlot.medicine_id, MachineMedicineSlot.created_at,
                   MachineMedicineSlot.updated_at, MachineMedicineSlot.total_count, MachineMedicineSlot.reserved_count]
    column_searchable_list = [MachineMedicineSlot.machine_id, MachineMedicineSlot.medicine_id]
    column_sortable_list = [MachineMedicineSlot.machine_id, MachineMedicineSlot.created_at,
                            MachineMedicineSlot.updated_at]


class MachineStatisticView(ModelView, model=MachineStatistic):
    column_list = [MachineStatistic.machine_id, MachineStatistic.created_at, MachineStatistic.updated_at,
                   MachineStatistic.info]
    column_searchable_list = [MachineStatistic.machine_id]
    column_sortable_list = [MachineStatistic.machine_id, MachineStatistic.created_at, MachineStatistic.updated_at]


class MachinePickupPointView(ModelView, model=MachinePickupPoint):
    column_list = [*MachinePickupPoint.__table__.columns]
    column_searchable_list = [MachinePickupPoint.id, MachinePickupPoint.machine_id, MachinePickupPoint.pickup_point]
    column_sortable_list = [MachinePickupPoint.id, MachinePickupPoint.created_at, MachinePickupPoint.updated_at]


class OrderView(ModelView, model=Order):
    machine_mac = sql.select(Machine.mac).where(Machine.id == Order.machine_id).label('machine_name')
    column_list = [Order.id, Order.user_id, Order.machine_id, Order.pickup_point_id, Order.status,
                   Order.payment_amount, Order.payment_currency, Order.payment_date,
                   Order.created_at, Order.updated_at, machine_mac]
    column_searchable_list = [Order.id, Order.user_id]
    column_sortable_list = [Order.id, Order.payment_amount, Order.created_at, Order.updated_at,
                            Order.payment_date]


class OrderMedicineView(ModelView, model=OrderMedicine):
    column_list = [*OrderMedicine.__table__.columns]
    column_searchable_list = [OrderMedicine.order_id, OrderMedicine.medicine_id]
    column_sortable_list = [OrderMedicine.order_id, OrderMedicine.created_at, OrderMedicine.updated_at]


class PickupPointView(ModelView, model=PickupPoint):
    column_list = [*PickupPoint.__table__.columns]
    column_searchable_list = [PickupPoint.id, PickupPoint.location]
    column_sortable_list = [PickupPoint.id, PickupPoint.created_at, PickupPoint.updated_at]


class MedicineView(ModelView, model=Medicine):
    column_list = [Medicine.id, Medicine.name, Medicine.description, Medicine.price, Medicine.currency,
                   Medicine.is_available]
    column_searchable_list = [Medicine.id, Medicine.name]
    column_sortable_list = [Medicine.id, Medicine.name, Medicine.price, Medicine.is_available]


class StatisticsAdmin(BaseView):
    name = "Statistics"
    icon = "fa-solid fa-chart-line"

    async def fetch_data(self, session: Session, query_type: str):
        query: str = None

        if query_type == "NumberOfAppointmentsPerClinic":
            query = """
            SELECT clinic.id AS ClinicId, clinic.name AS ClinicName, COUNT(appointment.id) as AppointmentCount
            FROM appointment
            JOIN doctor ON appointment.doctor_id = doctor.id
            JOIN clinic ON doctor.clinic_id = clinic.id
            GROUP BY clinic.name, clinic.id;
            """
        elif query_type == "NumberOfDoctorsByClinic":
            query = """
            SELECT * FROM dbo.GetNumberOfDoctorsPerClinic();
            """
        elif query_type == "PatientDistributionByClinic":
            query = """
            SELECT c.id AS ClinicId, c.name AS ClinicName, COUNT(p.id) AS NumberOfPatients
            FROM clinic c
            JOIN patient p ON c.id = p.clinic_id
            GROUP BY c.name, c.id;
            """
        elif query_type == "DoctorsSpecializationCount":
            query = """
            SELECT d.specialization AS Specialization, COUNT(d.id) AS NumberOfDoctors
            FROM doctor d
            GROUP BY d.specialization;
            """
        elif query_type == "AppointmentsCountPerMonth":
            query = """
            SELECT YEAR(date_of_appointment) AS Year, MONTH(date_of_appointment) AS Month, COUNT(*) AS AppointmentCount
            FROM appointment
            GROUP BY YEAR(date_of_appointment), MONTH(date_of_appointment)
            ORDER BY year, month;
            """
        elif query_type == "ErrorExample":
            query = "SELECT * FROasd"

        if not query:
            return []

        res = session.execute(text(query)).all()
        results = [row._mapping for row in res]
        return results

    @expose("/statistics", methods=["GET"])
    async def stats_page(self, request: Request):
        try:
            query_type = request.query_params.get('query_type')

            with db.create_session() as session:
                data = await self.fetch_data(session, query_type)

            return await self.templates.TemplateResponse(
                request, "statistics.html",
                {"request": request, "data": data, "statistic_type": query_type})

        except sqlalchemy.exc.ProgrammingError as e:
            print('DB Exception', e)

            return await self.templates.TemplateResponse(
                request, "statistics.html",
                {"request": request, "data": [], "error": {"message": "Error during access to database" + str(e)}})
        except Exception as e:
            print('Exception', e)

            return await self.templates.TemplateResponse(
                request, "statistics.html",
                {"request": request, "data": [], "error": {"message": str(e)}})
