import json
import random
from os import getenv

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.backend.projects.models import Project
from core.backend.payments.models import Subscription
from core.backend.users.models import User


def projects():
    return Project.objects.all()


def users():
    return User.objects.all()


def subscriptions():
    return Subscription.objects.all()


def dashboard_callback(request, context: dict):
    """
    Callback to prepare custom variables for index template which is used as dashboard
    template. It can be overridden in application by creating custom admin/index.html.
    """

    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    currency = "₦"
    view = request.GET.get("view", "projects")
    context.update(
        {
            "currency": currency,
            "navigation": [
                {
                    "title": _("Projects"),
                    "link": f'{reverse_lazy("admin:index")}?view=projects',
                    "active": True if view == "projects" else False,
                },
                {
                    "title": _("Users"),
                    "link": f'{reverse_lazy("admin:index")}?view=users',
                    "active": True if view == "users" else False,
                },
                {
                    "title": _("Subscriptions"),
                    "link": f'{reverse_lazy("admin:index")}?view=subscriptions',
                    "active": True if view == "subscriptions" else False,
                },
            ],
            "filters": [
                {"title": _("All"), "link": "#", "active": True},
                {
                    "title": _("Year"),
                    "link": "#",
                },
            ],
            "progress": [
                {
                    "title": "Social marketing e-book",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Freelancing tasks",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Development coaching",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Product consulting",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Other income",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
            ],
            "performance": [
                {
                    "title": _("Last week revenue"),
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                    "chart": json.dumps(
                        {
                            "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                            "datasets": [
                                {"data": performance_positive, "borderColor": "#9333ea"}
                            ],
                        }
                    ),
                },
                {
                    "title": _("Last week expenses"),
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                    "chart": json.dumps(
                        {
                            "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                            "datasets": [
                                {"data": performance_negative, "borderColor": "#f43f5e"}
                            ],
                        }
                    ),
                },
            ],
        }
    )
    match view:
        case "projects":
            projects = Project.objects.all()
            context.update(
                {
                    "projects": projects,
                    # "chart": json.dumps(
                    #     {
                    #         "labels": [month for month in month_abbv_dict.values()],
                    #         "datasets": [
                    #             {
                    #                 "label": spec.full_name,
                    #                 "data": spec.orders.monthly_order_history_list(),
                    #                 "backgroundColor": f"#{random.randint(0, 0xFFFFFF):06x}",
                    #                 "borderColor": f"#{random.randint(0, 0xFFFFFF):06x}",
                    #             }
                    #             for spec in specifications
                    #         ],
                    #     }
                    # ),
                }
            )
        case "users":
            users = User.objects.all()
            context.update({"users": users})
        case "subscriptions":
            subscriptions = Subscription.objects.all()
            context.update({"subscriptions": subscriptions})
    return context


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return [
        getenv("DJANGO_SETTINGS_MODULE", "Development").split(".")[-1],
        "success",
    ]  # info, danger, warning, success


def order_badge_callback(request):
    from core.backend.discos.models import Order

    return Order.objects.filter(new=True).count()


def new_disco_activation_request_callback(request):
    from core.backend.discos.models import Disco

    return Disco.objects.filter(active=False).count()


def permission_callback(request):
    return request.user.is_superuser
