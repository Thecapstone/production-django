from typing import TypedDict

from django.db.models import TextChoices


class SubscriptionType(TextChoices):
    MONTHLY = ("MONTHLY", "Monthly")
    YEARLY = ("YEARLY", "Yearly")


class UserTypes(TextChoices):
    CONSUMER = ("CONSUMER", "CONSUMER")
    DISCO = ("DISCO", "DISCO")
    STAFF = ("STAFF", "STAFF")


class NotificationType(TextChoices):
    ALERT = ("ALERT", "ALERT")
    INFO = ("INFO", "INFO")
    WARNING = ("WARNING", "WARNING")
    SUCCESS = ("SUCCESS", "SUCCESS")


class NotificationSubType(TextChoices):
    FAULT = ("FAULT", "FAULT")
    LOW_CREDIT = ("LOW_CREDIT", "Low Credit")
    OTHERS = ("OTHERS", "OTHERS")


class NotificationActionSchema(TypedDict):
    title: str
    uri: str


class NotificationData(TypedDict):
    title: str
    message: str


class PaymentStatus(TextChoices):
    SUCCESS = ("successful", "successful")
    FAILED = ("failed", "failed")
    CANCELLED = ("cancel", "cancel")


class PaymentEvent(TextChoices):
    CHARGE_SUCCESS = ("charge.completed", "charge.completed")
    FAILED = ("failed", "failed")
    CANCELLED = ("subscription.cancelled", "subscription.cancelled")
