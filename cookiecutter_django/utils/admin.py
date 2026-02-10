from django.contrib.postgres.fields import ArrayField
from django.db import models

from unfold.admin import ModelAdmin as _ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget


class ModelAdmin(_ModelAdmin):
    # Display fields in changeform in compressed mode
    compressed_fields = False  # Default: False
    # Preprocess content of readonly fields before render
    readonly_preprocess_fields = {
        "model_field_name": "html.unescape",
        "other_field_name": lambda content: content.strip(),
    }
    list_filter = [
        "id",
        "created_at",
        "updated_at",
    ]
    search_fields = ["id"]
    # Display submit button in filters
    list_filter_submit = True

    # Display changelist in fullwidth
    list_fullwidth = False

    # Position horizontal scrollbar in changelist at the top
    list_horizontal_scrollbar_top = True

    # Custom actions
    # actions_list = []  # Displayed above the results list
    # actions_row = []  # Displayed in a table row in results list
    # actions_detail = []  # Displayed at the top of for in object detail
    # actions_submit_line = []  # Displayed near save in object detail

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        },
        ArrayField: {
            "widget": ArrayWidget,
        },
    }
