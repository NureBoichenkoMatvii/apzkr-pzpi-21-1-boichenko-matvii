from fastapi_babel.core import _


class MachineMessages:
    @property
    def MACHINE_HAS_ZERO_FREE_SLOTS(self):
        return _("Machine doesn't have free slots")

    @property
    def MACHINE_HAS_SUCH_MEDICINE_SLOT(self):
        return _("Machine already has a slot with such a medicine")

    @property
    def MACHINE_HAS_SUCH_PICKUP_POINT(self):
        return _("Machine already has such a pickup point in its route")

    @property
    def MACHINE_SLOT_IS_OCCUPIED(self):
        return _("Such machine's slot is already occupied")

    @property
    def MACHINE_NOT_FOUND(self):
        return _("Machine not found")

    @property
    def MACHINE_SLOT_NOT_FOUND(self):
        return _("Machine's slot not found")

    @property
    def MACHINE_STATISTIC_NOT_FOUND(self):
        return _("Machine's statistic not found")

    @property
    def MACHINE_SCHEDULE_NOT_FOUND(self):
        return _("Machine's schedule not found")

    @property
    def MACHINE_PICKUP_POINT_NOT_FOUND(self):
        return _("Machine's pickup point not found")


class AuthMessages:
    @property
    def NOT_AUTHORIZED(self):
        return _("Request wasn't authorized")

    @property
    def INVALID_API_KEY(self):
        return _("Invalid API key")


class GeneralMessages:
    @property
    def GENERAL_LOCALISATION_NOT_FOUND(self):
        return _("We didn't find such general localisation")


class OrderMessages:
    @property
    def ORDER_NOT_FOUND(self):
        return _("Such order doesn't exist")

    @property
    def ORDER_MEDICINE_NOT_FOUND(self):
        return _("Such order has no such medicine")

    @property
    def ORDER_HAS_SUCH_MEDICINE(self):
        return _("Order already has a slot with such medicine")


class PickupPointMessages:
    @property
    def PICKUP_POINT_NOT_FOUND(self):
        return _("Such pickup point doesn't exist")


class MedicineMessages:
    @property
    def MEDICINE_NOT_FOUND(self):
        return _("Such medicine doesn't exist")


class ErrorMessages:
    Machine = MachineMessages()
    Auth = AuthMessages()
    General = GeneralMessages()
    order = OrderMessages()
    pickup_point = PickupPointMessages()
    medicine = MedicineMessages()
