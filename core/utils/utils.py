import json
import logging
from os import getenv
import re
import secrets
import urllib.parse
from collections import OrderedDict
from collections.abc import Callable
from operator import itemgetter
from typing import Any, Literal
from unittest.mock import MagicMock
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.db.models import Q, QuerySet, Subquery
from django.http import HttpRequest, QueryDict
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.serializers import JSONField, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from core.utils.custom_exceptions import CustomError
from core.utils.interface import BaseTypeModel


def is_setting_config(settings: Literal["local", "production", "test"]) -> bool:
    config = getenv("DJANGO_SETTINGS_MODULE", "config.settings.local").split(".")[-1]
    return settings == config


def get_user_uuid_token(user):
    from djoser import utils

    context = {}
    context["uid"] = utils.encode_uid(user.pk)
    context["token"] = default_token_generator.make_token(user)
    return context


def float_to_timedelta(float_days):
    # Extract the integer part (days) and fractional part (hours)
    days = int(float_days)
    hours_fraction = (float_days - days) * 24

    # Convert to timedelta
    duration = timezone.timedelta(days=days, hours=hours_fraction)

    return duration


def get_user_refresh_access_token(user):
    refresh = RefreshToken.for_user(user)
    data = {}
    data["refresh"] = str(refresh)
    data["access"] = str(refresh.access_token)
    return data


def get_file_path(instance, filename):
    import os
    import uuid

    filename = uuid.uuid4().hex[:8] + os.path.splitext(filename)[1]
    path = f"{instance.owner.id}/{instance.mimetype}/{filename}"
    return path


def convert_and_compress_error(
    value: Any,
    converter: callable = str,
    allowed_values: list[Any] = [],
    raise_exception: bool = False,
    *args,
    **kwargs,
) -> Any | None:
    """function is used to convert from one datatype to the other without
    throwing an error if type is not convertible

    Args:
        value (Any): _description_
        converter (callable, optional): _description_. Defaults to str.
        allowed_values (List[Any]): _description_. Defaults to list
        raise_exception (bool, optional): _description_. Defaults to False.

    Returns:
        Union[Any,None]: _description_
    """
    if value is None or (allowed_values and value not in allowed_values):
        return
    if raise_exception:
        return converter(value)

    try:
        return converter(value)
    except ValueError:
        ...


def get_image_path(instance, filename):
    return get_file_path(instance, filename)


def get_post_video_path(instance, filename):
    return get_file_path(instance, filename)


def get_doc_path(instance, filename):
    return get_file_path(instance, filename)


def get_random_models(n: int, model: str, app_label: str = "users") -> list[int]:
    """
    Returns a list of random interests ids
    """
    from django.apps import apps

    model = apps.get_model(app_label, model)

    return [
        obj
        for obj in model.objects.all()
        .order_by("?")
        .values_list("id", flat=True)
        .distinct()[:n]
    ]


def is_video(filename: str) -> bool:
    """
    Returns True if the file is a video
    """
    import mimetypes

    return mimetypes.guess_type(filename)[0].startswith("video")


def is_image(filename: str) -> bool:
    import mimetypes

    return mimetypes.guess_type(filename)[0].startswith("image")


def is_document(filename: str) -> bool:
    import mimetypes

    return mimetypes.guess_type(filename)[0].startswith("text") or mimetypes.guess_type(
        filename
    )[0].startswith("application")


def calculate_age(born):
    from datetime import date

    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def validate_age(date_of_birth):
    from django.utils.translation import gettext_lazy as _

    if calculate_age(date_of_birth) < 13:
        raise CustomError.BadRequest(
            _("You must be at least 13 years old."),
        )


def generate_referal_code(length: int = 5, name: str | None = ""):
    return name + uuid4().hex.upper()[:length]


def generate_barcode():
    return secrets.token_hex(15)


def generate_ref(length: int | None = None):
    return secrets.token_urlsafe(length).replace("_", "").replace("-", "")[:length]


def generate_id(length: int = 10):
    """generate id for all the models

    Args:
        length (int, optional): _description_. Defaults to 10.

    Returns:
        _type_: _description_
    """
    return uuid4().hex[:length]


def generate_api_key():
    """generate id for all the models

    Args:
        length (int, optional): _description_. Defaults to 10.

    Returns:
        _type_: _description_
    """
    return f"api_key_{secrets.token_urlsafe()}"


def payment_ref_generator(prefix: str = "PAY", length: int = 10):
    """generate reference for payment transactin

    Args:
        prefix (str, optional): _description_. Defaults to None.
        length (int, optional): _description_. Defaults to 10.
    """

    def wrapper():
        return f"{prefix}-{uuid4().hex[:length]}"

    return wrapper


def get_user_models_tagged_in_content(content: str) -> QuerySet:
    """function extract all the user tagged in a string

    Args:
        content (str): _description_

    Returns:
        QuerySet: _description_
    """
    User = get_user_model()
    regex = r"@(\w+)"
    matches = re.findall(regex, content, re.MULTILINE)
    return User.objects.filter(username__in=matches)


def get_hashtag_from_tagged_content(content: str) -> QuerySet:
    """function extract all the hastags models  in a string

    Args:
        content (str): _description_

    Returns:
        QuerySet: _description_
    """
    regex = r"#(\w+)"
    return re.findall(regex, content, re.MULTILINE)


def generate_room_uid():
    return generate_id(length=20)


def log(msg, *args, instance: object = None, method: callable = None):
    """logger

    Args:
        msg (_type_): _description_
        instance (object, optional): _description_. Defaults to None.
        method (callable, optional): _description_. Defaults to None.
    """
    # generate debug info

    classname = instance.__class__.__name__ if instance else ""
    method_name = method.__name__ if method else ""

    if method_name:
        method_name = f".{method_name}()"

    if classname:
        classname = f"[{classname}]"


def transform_event_data(event_data={}, *args):
    """_summary_

    Args:
        event_data (dict, optional): _description_. Defaults to {}.

    Returns:
        Dict: {
            "method_name":str,
            "event":str,
            "body":dict,
            "params":dict
        }
    """
    method_name = event_data.get("type", "")

    event = (method_name[3:] if method_name.startswith("on_") else method_name).replace(
        "_", "."
    )

    body = event_data.get("data", {})
    exclude_channels = event_data.get("exclude_channels", [])
    params = event_data.get("params", {})
    result = {
        "method_name": method_name,
        "event": event,
        "body": body,
        "params": params,
        "exclude_channels": exclude_channels,
    }
    if not args:
        return result

    return itemgetter(*args)(result)


def filter_fields(
    data: dict[str, Any], include: list[str] = [], exclude: list[str] = []
):
    """filter certain fields from dictionary

    Args:
        data (Dict[str,Any]): dictionary to filter
        include (List[str], optional): list of keys to include in the new dictionary. Defaults to [].
        exclude (List[str], optional): list of keys to exclude in the new dictionary. Defaults to [].
    """
    result = {}

    for key, value in data.items():
        if include and (value or value in [False, 0]) and key in include:
            result[key] = value

        elif exclude and (value or value in [False, 0]) and key not in exclude:
            result[key] = value

        elif value or value in [False, 0]:
            result[key] = value

    return result


def get_changed_fields(prev, current):
    """function to compare two dict and return a
        list of fields that have changed

    Args:
        prev (_type_): _description_
        current (_type_): _description_

    Returns:
        _type_: _description_
    """

    prev = prev or {}
    current = current or {}

    if not all([prev, current]):
        data = prev or current
        return [key for key, _ in data.items()]

    current_item_list = list(current.items())
    prev_item_list = list(prev.items())
    assert len(current_item_list) == len(
        prev_item_list
    ), "previous data and current data must have the same number of keys"
    result = []
    for index in range(len(current_item_list)):
        if current_item_list[index][1] != prev_item_list[index][1]:
            result.append(current_item_list[index][0])
    return result


def get_all_methods_starting_with(
    instance: object, startswith: str, *args, **kwargs
) -> list[callable]:
    log("get_all_methods_starting_with()", instance=instance)
    """return a list of method starting with the startswith string

    Args:
        instance (object): _description_
        startswith (str, optional): _description_. Defaults to None.

    Returns:
        List[callable]: list of callable
    """

    return [
        getattr(instance, method_name)
        for method_name in dir(instance)
        if method_name.startswith(startswith)
        and callable(getattr(instance, method_name))
    ]


def make_distinct(qs: QuerySet, field: str = "id") -> QuerySet:
    """function generate unique queryset using subquery

    Args:
        qs (QuerySet): description
        field (str, optional): description. Defaults to "id".

    Returns:
        QuerySet: description
    """
    kwargs = {f"{field}__in": Subquery(qs.values(field))}
    return qs.model.objects.filter(**kwargs)


class FilterAndSearchManager:
    def __init__(
        self,
        *,
        request: HttpRequest,
        filterset_fields: list[str] = [],
        filterset_keys: dict[str, Callable[[Any], Any | None]] = {},
        search_fields: list[str] = [],
        ordering_fields: list[str] = [],
        ordering: list[str] = [],
        filter_map: dict[str, str | list[str]] = {},
    ) -> None:
        """filter, ordering and search management class

        Args:
            request (HttpRequest): django request object
            filterset_fields (list[str], optional): a list of fields in the queryset
            to used and perform filters. Defaults to [].
            filterset_keys (dict[str,Callable[[Any],Any|None]], optional): \
                a dict of field_name:converter queryset in the queryset. Defaults to {
                "rating":int,
                "price":float
            }.
            search_fields (list[str], optional): fields to used for search. Defaults to [].
            ordering_fields (list[str], optional): fileds to use for default ordering
            when ordering is not specified. Defaults to [].
            ordering (list[str], optional): fields allowed to be used for ordering when
            specifying ordering in the request object. Defaults to [].
            filter_map (dict[str,str | list[str]], optional): a dictionary where the key is
              the query params key in the request and the value is the key that will be
              used for the filter. Defaults to {}.

        Examples:
            filter_map: {
                "courses":[
                    "student_teams__courses__id",
                    "instructor_teams__courses__id",
                ],
                "owner":"courses__owner__id",
                "rating[]":"courses__rating",
            }
        """

        self.filterset_fields = filterset_fields
        self.search_fields = search_fields
        self.ordering_fields = ordering_fields
        self.ordering = ordering
        self.request = request
        self.filter_map = filter_map
        self.filterset_keys = filterset_keys

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def subpress_error(
        self, function: Callable[[Any], Any | None], value: Any
    ) -> Any | None:
        try:
            return function(value)
        except (ValueError, TypeError):
            # Ignore errors raised during conversion and continue to the next field.
            pass

    def build_filter_params(
        self,
        request: HttpRequest,
        field_callable_dict: dict[
            str, Callable[[Any], Any] | list[Callable[[Any], Any]]
        ],
    ) -> dict[str, Any]:
        """
        Build filter parameters for Django queryset filter function from request data.

        Parameters:
            request (django.http.HttpRequest): The Django request object containing the data.
            field_callable_dict (dict[str, Callable[[Any], Any]|list[Callable[[Any], Any]]]):\
                 A dictionary with field names as keys and callables as values.

        Returns:
            dict: A dictionary of filter parameters to be used with Django queryset .filter() function.
        """
        filter_params = {}

        if not isinstance(request.GET, QueryDict):
            return filter_params

        for field, field_callable in field_callable_dict.items():
            if isinstance(field_callable, list) and len(field_callable) > 0:
                # If the field_callable is specified as a list, apply each converter to the list of values.
                values = request.GET.getlist(field)
                converted_values = [
                    self.subpress_error(callable_item, val)
                    for val, callable_item in zip(values, field_callable)
                ]
                # Filter out None and empty values from the converted list.
                converted_values = [val for val in converted_values if val is not None]
                if converted_values:
                    filter_params[field] = converted_values
            else:
                # If the field_callable is not a list, apply the converter to the single value.
                value = request.GET.get(field)
                if value is not None:
                    try:
                        converted_value = field_callable(value)
                        if converted_value is not None:
                            filter_params[field] = converted_value
                    except (ValueError, TypeError):
                        # Ignore errors raised during conversion and continue to the next field.
                        pass

        return filter_params

    def filter_queryset_with_filterset_keys(self, queryset: QuerySet) -> QuerySet:
        """method take in a queryset and filter it based on the mapping that was provided
        with filterset_keys

        filterset_keys:
        {
            "name":str,
            "age":int, #this retrieve it as a single value
            "ids":[str] #this try retriving the query params as a list
        }

        Args:
            queryset (QuerySet):

        Returns:
            QuerySet:
        """
        if not self.filterset_keys:
            return queryset

        kwargs = self.build_filter_params(self.request, self.filterset_keys)
        if kwargs:
            queryset = queryset.filter(**kwargs)

        return queryset

    def filter_queryset_with_dict_maping(self, queryset: QuerySet) -> QuerySet:
        """method take in a queryset and filter it based on the mapping that was provided

        Args:
            queryset (QuerySet):

        Returns:
            QuerySet:
        """
        if not self.filter_map:
            return queryset

        query_params: QueryDict = self.request.GET  # get query dictionary
        query_kwargs = {}
        for key, value in self.filter_map.items():  # loop through the filter map
            if key in query_params.dict():  # if the filter map key exists
                if isinstance(value, str):  # check if it is string
                    data_list = query_params.getlist(key)
                    data_single = query_params.get(key)
                    if data_list:
                        query_kwargs[f"{value}__in"] = data_list
                    elif data_single:
                        query_kwargs[value] = data_single
                elif isinstance(value, list):
                    q = Q()
                    data_list = query_params.getlist(key)
                    data_single = query_params.get(key)

                    if data_list:
                        for sub_value in value:
                            q |= Q(**{f"{sub_value}__in": data_list})
                        queryset = queryset.filter(q)
                    elif data_single:
                        query_kwargs[value] = query_params.get(key)
                        for sub_value in value:
                            q |= Q(**{sub_value: data_single})
                        queryset = queryset.filter(q)

        if query_kwargs:
            queryset = queryset.filter(**query_kwargs)

        return queryset

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for Backend in list(self.filter_backends):
            backend: DjangoFilterBackend = Backend()
            queryset = backend.filter_queryset(self.request, queryset, self)
        self.filter_queryset_with_dict_maping(queryset)
        return queryset


class BaseModelMixin(models.Model):
    id: int = models.BigAutoField(primary_key=True)
    uid: str = models.CharField(default=generate_id, editable=False, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, editable=True)
    updated_at = models.DateTimeField(
        auto_now=True, auto_now_add=False, db_index=True, editable=True
    )
    active = models.BooleanField(_("active"), default=True, db_index=True)

    def __str__(self):
        return f"< {type(self).__name__}({self.id}) >"

    @classmethod
    def _serializer_fields(cls, exclude=[], *args):
        args = ["id", "active", "created_at", "updated_at", *args]
        return sorted(list({field for field in args if field and field not in exclude}))

    @classmethod
    def _serializer_extra_kwargs(cls, exclude=[], **kwargs: dict[str, Any]):
        return {
            key: value for key, value in kwargs.items() if value and key not in exclude
        }

    @classmethod
    def serializer_fields(cls, *args, exclude=[]):
        return cls._serializer_fields(exclude, *args)

    @classmethod
    def serializer_extra_kwargs(cls, exclude=[], **kwargs):
        return cls._serializer_extra_kwargs(exclude, **kwargs)

    def get_field_or_none(self, field_name: str) -> tuple[bool, Any]:
        """get a field or return <is not None>,data


        res = getattr(self,field_name,None)\n
        return res is not None,res


        Args:
            field_name (str): _description_

        Returns:
            Tuple[bool,Any]: return result . True,Any
        """
        res = getattr(self, field_name, None)
        return res is not None, res

    def get_attribute_by_path(self, obj: object, dot_path: str) -> Any | None:
        """
        Retrieve an attribute or method of an object using a dot-separated path.

        Args:
            obj: The object to search within.
            dot_path (str): Dot-separated path to the attribute/method.

        Returns:
            Any|None: The attribute or method if found, or None if not found.
        """
        path_components = dot_path.split(".")
        current_obj = obj

        for component in path_components:
            if hasattr(current_obj, component):
                current_obj = getattr(current_obj, component)
            else:
                return None

        return current_obj

    class Meta:
        abstract = True
        ordering = ["-created_at", "id"]


class TestHelper:
    def add_permission_side_effect(
        self, mock_dependency: MagicMock, permission: dict[str, Any]
    ) -> MagicMock:
        mock_dependency.side_effect = (
            lambda base_url, service, permission_id, dot_path: permission.get(dot_path)
        )
        return mock_dependency

    def generate_timedelta(
        self,
        when: Literal["before", "after"],
        period: Literal["weeks", "days", "minutes", "seconds"] = "days",
        value: int = 2,
    ) -> str:
        """
        Args:
            when (Literal["before", "after"]): description
            period (Literal["weeks", "days", "minutes", "seconds"]): description
            value (int): description
        """
        if when == "before":
            return (
                (timezone.now() - timezone.timedelta(**{period: value}))
                .date()
                .isoformat()
            )
        elif when == "after":
            return (
                (timezone.now() + timezone.timedelta(**{period: value}))
                .date()
                .isoformat()
            )

    def no_duplicate(
        self, data: list[str | int] | list[dict[str, Any]], id_field: str | int = "id"
    ) -> bool:
        if not data:
            return True
        if type(data[0]) in [dict, OrderedDict]:
            data = [x.get(id_field) for x in data]
        return len(data) == len(set(data))

    def has_no_duplicate_in_response_results(
        self, response, id_field: str | int = "id"
    ) -> bool:
        data: list[str | int] | list[dict[str, Any]] = response.data.get("results")
        if not data:
            return True
        if type(data[0]) in [dict, OrderedDict]:
            data = [x.get(id_field) for x in data]
        return len(data) == len(set(data))

    def has_fields(self, response, fields: list[int | str]) -> bool:
        data: dict = response.data
        conditions = []
        for x in fields:
            exist = x in data
            conditions.append(exist)
            if not exist:
                logging.warning("field -> '%s' does not exists", x)
        return all(conditions)

    def has_specified_fields(self, data, fields: list[int | str]) -> bool:
        conditions = []
        for x in fields:
            exist = x in data
            conditions.append(exist)
            if not exist:
                logging.warning("field -> '%s' does not exists", x)
        return all(conditions)

    def extract_results_in_response(self, response) -> list[dict]:
        return response.data.get("results")

    def has_fields_in_response_results(self, response, fields: list[int | str]) -> bool:
        results: list[dict] = response.data.get("results")
        if not results:
            return False
        data: dict = results[0]
        conditions = []
        for x in fields:
            exist = x in data
            conditions.append(exist)
            if not exist:
                logging.warning("field -> '%s' does not exists", x)
        return all(conditions)

    def has_paginated_count(self, response, count: int) -> bool:
        return response.data.get("count") == count

    def has_response_status(self, response, status_code: int) -> bool:
        return response.status_code == status_code

    def add_query_params_to_url(self, url: str, params: dict[str, Any]) -> str:
        query_string = urllib.parse.urlencode(params)
        return f"{url}?{query_string}"


def duration_to_timedelta(value):
    """Convert a duration string in the format "DAYS:HH:MM:SS" to a timedelta object."""
    try:
        days, hours, minutes, seconds = map(int, value.split(":"))
        return timezone.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
    except ValueError:
        return None


class PydanticModelFieldEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        elif isinstance(obj, list) and isinstance(obj[0], BaseModel):
            data: list[BaseModel] = obj
            return [model.model_dump(mode="json") for model in data]
        else:
            return super().default(obj)


class PydanticModelField(models.JSONField):
    """Usage

    data = PydanticModelField(pydantic_model=OpenAPISpecSchema) \n
    data = PydanticModelField(pydantic_model=[OpenAPISpecSchema])
    """

    def __init__(
        self,
        pydantic_model: BaseModel | tuple[BaseModel] | dict[str, BaseModel] = None,
        null=True,
        blank=True,
        *args,
        **kwargs,
    ):
        """Pydantic Model field

        Args:
            pydantic_model (BaseModel | Tuple[BaseModel] | dict[str,BaseModel], optional): _description_. Defaults to None. # noqa

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """

        if pydantic_model:
            if isinstance(pydantic_model, (list, tuple)):
                if not pydantic_model:
                    raise ValueError("pydantic_model list cannot be empty")

                for model_class in pydantic_model:
                    if not issubclass(model_class, (BaseModel, BaseTypeModel)):
                        raise ValueError(
                            "All elements in the tuple/list must be subclasses of BaseModel"
                        )
            elif isinstance(pydantic_model, dict):
                for model_class in pydantic_model.values():
                    if not issubclass(model_class, BaseTypeModel):
                        raise ValueError(
                            "All values in the dictionary must be subclasses of BaseTypeModel"
                        )
            elif not issubclass(pydantic_model, (BaseModel, BaseTypeModel)):
                raise ValueError("pydantic_model must be a subclass of BaseModel")
        self.pydantic_model: (
            BaseModel
            | BaseTypeModel
            | None
            | tuple[BaseModel | BaseTypeModel]
            | dict[str, BaseModel | BaseTypeModel]
        ) = pydantic_model

        kwargs["encoder"] = kwargs.get("encoder", PydanticModelFieldEncoder)
        super().__init__(null=null, blank=blank, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                pass

        if value and self.pydantic_model:
            try:
                if isinstance(self.pydantic_model, (list, tuple)):
                    data = []
                    ModelClass = self.pydantic_model[0]
                    value: list[dict]
                    for x in value:
                        data.append(ModelClass(**x))
                    return data
                elif isinstance(self.pydantic_model, dict):
                    value: dict
                    ModelClass = self.pydantic_model.get(value.get("type"))
                    return ModelClass(**value.get("data"))
                elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):
                    if isinstance(value, str):
                        return self.pydantic_model(**json.loads(value))
                    return self.pydantic_model(value)
                else:
                    raise ValueError("Invalid data")
            except Exception as e:
                log("invalid data ", "\n", e)
                return
                # raise ValidationError(f"Invalid data for {self.pydantic_model}: {e}")

        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value: BaseModel | BaseTypeModel | list[BaseModel] | None):
        if value is None:
            return [] if isinstance(self.pydantic_model, (list, tuple)) else {}
        data = {}

        if not self.pydantic_model:
            return

        if isinstance(self.pydantic_model, (list, tuple)):
            if not isinstance(value, (list, tuple)):
                raise ValueError("Value must be a list or tuple")
            data = []
            ModelClass = self.pydantic_model[0]
            for model_instance in value:
                model_instance: BaseModel | BaseTypeModel
                if not isinstance(model_instance, ModelClass):
                    raise ValueError("Value must be a list %s" % str(ModelClass))
                data.append(model_instance.model_dump(mode="json", by_alias=True))
        elif isinstance(self.pydantic_model, dict):
            if not isinstance(value, BaseTypeModel):
                raise ValueError("Value must be an instance of BaseTypeModel")
            _type = getattr(value, "type", None)
            if not _type:
                raise ValueError(
                    "%s must have a field `type`" % value.__class__.__name__
                )
            model_type = _type
            ModelClass = self.pydantic_model.get(model_type)
            if ModelClass is None:
                raise ValueError("Invalid value.type")

            if not isinstance(value, ModelClass):
                raise ValueError("Value must be a list %s" % str(ModelClass))
            data = {
                "type": model_type,
                "data": value.model_dump(mode="json", by_alias=True),
            }
        elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):
            if not isinstance(value, BaseModel):
                if not value:
                    return value
                raise ValueError(
                    f"Value must be an instance of BaseModel: {value.__class__.__name__}"
                )
            return value.model_dump_json(by_alias=True)
        else:
            raise ValueError("Invalid data")
        return json.dumps(data)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class PydanticModelSerializerField(JSONField):
    """
    Example:
        class TestModelRetrieve(serializers.ModelSerializer):
            data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.data.field.pydantic_model
            )\n
            list_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.list_data.field.pydantic_model
            )\n
            type_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.type_data.field.pydantic_model
            )\n

            class Meta:
                model = modelsv2.TestModel\n
                fields = [
                    "data",
                    "list_data",
                    "type_data",
                ]


        data with different type will be

        {
            "type":"WORD_PLAY",
            "data":{
                "key1":"value1",
            }
        }

    Args:
        serializers (_type_): _description_
    """

    def __init__(self, pydantic_model=None, *args, **kwargs):
        self.pydantic_model = pydantic_model
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data: dict):
        try:
            if self.pydantic_model:
                if isinstance(self.pydantic_model, (list, tuple)):
                    deserialized_data = []
                    ModelClass = self.pydantic_model[0]
                    for item in data:
                        deserialized_data.append(ModelClass(**item))
                    return deserialized_data
                elif isinstance(self.pydantic_model, dict):
                    ModelClass = self.pydantic_model.get(data.get("type"))
                    if not ModelClass:
                        raise ValidationError(f"Invalid type; {data.get('type')}")
                    return ModelClass(**data)
                elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):
                    return self.pydantic_model(**data)
                else:
                    raise ValidationError("Invalid data")
            return data
        except PydanticValidationError as e:
            raise ValidationError(e.json())

    def to_representation(self, value) -> str:
        data = PydanticModelField(self.pydantic_model).get_prep_value(value)
        if isinstance(data, str):
            data = json.loads(data)
        return data

    def _format_validation_error(self, error):
        if isinstance(error, PydanticValidationError):
            error_messages = []

            for error_obj in error.errors():
                if isinstance(error_obj, dict):
                    for field, field_errors in error_obj.items():
                        for sub_error in field_errors:
                            error_messages.append(
                                {
                                    "field": field,
                                    "message": str(sub_error),
                                }
                            )
                else:
                    error_messages.append({"field": "", "message": str(error_obj)})

            return error_messages
        return str(error)


def to_snake_case(text: str) -> str:
    # Convert from Kebab Case (hyphenated)
    text = text.replace("-", "_")

    # Convert from CamelCase or PascalCase
    text = re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()

    return text
