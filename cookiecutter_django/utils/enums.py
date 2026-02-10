from typing import TypedDict

from django.db.models import TextChoices


class ModeratorRoles(TextChoices):
    SUPER = ("super", "super")
    COMPLIANCE = ("compliance", "compliance")
    CONTENT = ("content", "content")
    COMMUNITY = ("community", "community")
    REPORTS = ("reports", "reports")


class CommentReportReason(TextChoices):
    SPAMMING = ("spamming", "spamming")
    HARM_TO_SELF_OR_OTHERS = ("harm_to_self_or_others", "harm_to_self_or_others")
    HARASSMENT = ("harassment", "harassment")
    INAPPROPRIATE_CONTENT = ("inappropriate_content", "inappropriate_content")
    OTHER = ("other", "other")

class CommunityReportReason(TextChoices):
    ...
