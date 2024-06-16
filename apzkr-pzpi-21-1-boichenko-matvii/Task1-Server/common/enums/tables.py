from enum import StrEnum


class PostgresTables(StrEnum):
    USER = "user"
    MEDICINE = "medicine"
    ORDER = "order"
    ORDER_MEDICINE = "order_medicine"
    MACHINE = "machine"
    MACHINE_MEDICINE_SLOT = "machine_medicine_slot"
    MACHINE_SCHEDULE = "machine_schedule"
    MACHINE_STATISTIC = "machine_statistic"
    MACHINE_PICKUP_POINT = "machine_pickup_point"
    # MACHINE_INGREDIENT = "machine_ingredient"
    PICKUP_POINT = "pickup_point"
    # PAYMENT = "payment"
    # MAINTENANCE = "maintenance"
    # PROMOTION = "promotion"
    # USER_PROMOTION = "user_promotion"

