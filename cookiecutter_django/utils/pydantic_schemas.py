from contextlib import contextmanager
from typing import Any, Dict, List, Literal, Optional, Union, Iterator

from pydantic import AliasChoices, Field, ValidationError

from core.utils.interface import BaseModel
from core.utils.generators import generate_example


def is_recursion_validation_error(exc: ValidationError) -> bool:
    errors = exc.errors()
    return len(errors) == 1 and errors[0]["type"] == "recursion_loop"


@contextmanager
def suppress_recursion_validation_error() -> Iterator[None]:
    try:
        yield
    except ValidationError as exc:
        if not is_recursion_validation_error(exc):
            raise exc


class OpenAPISchema(BaseModel):
    openapi: Optional[str] = None


class ContactSchema(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class LicenseSchema(BaseModel):
    name: Optional[str] = None
    identifier: Optional[str] = None
    url: Optional[str] = None


class InfoSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[ContactSchema] = None
    license: Optional[LicenseSchema] = None
    version: Optional[str] = None


class ExternalDocsSchema(BaseModel):
    description: Optional[str] = None
    url: Optional[str] = None


class ServerVariableSchema(BaseModel):
    enum: List[str] = None
    default: Optional[str] = None
    description: Optional[str] = None


class ServerPortSchema(BaseModel):
    enum: List[str]
    description: Optional[str] = None


class ServerEnumDefaultStyleBaseSchema(BaseModel):
    enum: Optional[List[str]] = None
    default: Optional[str] = None


class ServerProtocolSchema(ServerEnumDefaultStyleBaseSchema): ...


class ServerEnvironmentSchema(ServerEnumDefaultStyleBaseSchema): ...


class ServerRegionSchema(ServerEnumDefaultStyleBaseSchema): ...


class ServerSchema(BaseModel):
    url: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[
        Dict[str, ServerVariableSchema]
        | Dict[Literal["protocol"], ServerProtocolSchema]
        | Dict[Literal["port"], ServerPortSchema]
        | Dict[Literal["environment"], ServerEnvironmentSchema]
        | Dict[Literal["region"], ServerRegionSchema]
    ] = None


class ParameterSchemaScheme(BaseModel):
    type: Optional[
        Literal[
            "string", "object", "number", "integer", "boolean", "array", "file", None
        ]
    ] = None
    enum: Optional[List[str | int | float | None] | str | int | float | None] = None
    format: Optional[
        Literal[
            "uuid",
            "int32",
            "int64",
            "float",
            "double",
            "byte",
            "binary",
            "date",
            "date-time",
            "password",
            "duration",
            None,
        ]
        | str
    ] = None
    default: Optional[int | str] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    nullable: Optional[bool] = None
    items: Optional[
        Union[
            "SchemaType.Integer",
            "SchemaType.String",
            "SchemaType.Enum",
            "SchemaType.Number",
            "SchemaType.Boolean",
            "SchemaType.Array",
            "SchemaType.Object",
            "SchemaType.Null",
            "SchemaType.File",
            "SchemaType.AnyType",
            "SchemaType.AnyOf",
            "SchemaType.AllOf",
        ]
        | Dict[Literal["$ref"], str]
    ] = None


class BaseExampleSchema(BaseModel):
    summary: Optional[str] = None
    value: Optional[List[int | str | float | dict] | Dict[str, dict | list] | str] = (
        None
    )


class ParameterExampleSchema(BaseExampleSchema): ...


class RequestBodyExampleSchema(BaseExampleSchema):
    externalValue: Optional[str] = None


class ResponseBodyExampleSchema(BaseExampleSchema):
    externalValue: Optional[str] = None


class BoardSecuritySchema(BaseModel):
    security: Optional[
        List[
            Dict[
                str,
                Dict[Literal["cookieAuth", "jwtAuth", None], List["FlowsScopeType"]],
            ]
        ]
    ] = None


class SchemaProperty(BaseModel):
    type: Optional[
        Literal[
            "string", "object", "number", "integer", "boolean", "array", "file", None
        ]
    ] = None
    enum: Optional[List[str] | str] = None
    format: Optional[
        Literal[
            "uuid",
            "int32",
            "int64",
            "float",
            "double",
            "byte",
            "binary",
            "date",
            "date-time",
            "password",
            None,
        ]
        | None
    ] = None
    default: Optional[int | str] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    nullable: Optional[bool] = None
    description: Optional[str] = None
    maxLength: Optional[int] = None


class MediaTypeColorEncoding(BaseModel):
    style: Optional[
        Literal[
            "form",
            "label",
            "simple",
            "spaceDelimited",
            "pipeDelimited",
            "deepObject",
            "matrix",
            None,
        ]
    ] = None  # noqa: E501
    explode: Optional[bool] = None


class MediaTypeEncoding(BaseModel):
    color: Optional[MediaTypeColorEncoding] = None


class MediaTypeSchema(BaseModel):
    schema_: Optional[
        "SchemaObject"
        | Dict[str, Union["SchemaType.AllOf", "SchemaType.AnyOf", "SchemaObject"]]
        | Dict[Literal["$ref"], str]
    ] = Field(default=None, alias="schema")  # noqa: E501
    encoding: Optional[
        MediaTypeEncoding | Dict[str, Dict[Literal["allowReserved"], bool]]
    ] = None
    example: Optional[Dict[str, str] | str | int] = None
    examples: Optional[
        Dict[str, RequestBodyExampleSchema] | RequestBodyExampleSchema
    ] = None


class ParametersSchema(BaseModel):
    name: Optional[str] = None
    in_: Optional[str] = Field(
        default=None, alias="in", validation_alias=AliasChoices("in", "in_")
    )
    description: Optional[str] = None
    required: Optional[bool | dict] = None
    schema_: Optional[ParameterSchemaScheme | Dict[Literal["$ref"], str]] = Field(
        default=None, alias="schema"
    )
    allowReserved: Optional[bool] = None
    style: Optional[str] = None  # noqa: E501
    explode: Optional[bool] = None
    content: Optional[Dict[str, Dict[str, MediaTypeSchema]]] = None
    allowEmptyValue: Optional[bool] = None
    example: Optional[str | int | float] = None
    examples: Optional[Dict[str, ParameterExampleSchema]] = None
    deprecated: Optional[bool] = None

    @property
    def is_query_parameter(self) -> bool:
        return self.in_ == "query"

    @property
    def is_header_parameter(self) -> bool:
        return self.in_ == "header"

    @property
    def is_path_parameter(self) -> bool:
        return self.in_ == "path"

    @property
    def is_cookie_parameter(self) -> bool:
        return self.in_ == "cookie"


class ContentGenerators:
    def sample(self):
        direction = None
        if isinstance(self, RequestBodySchema):
            direction = "payload"
        else:
            direction = "sample"
        data = {}
        for content_type, values in self.content.items():
            data.update(
                {
                    content_type: {
                        direction: generate_example(values.schema_.model_dump())
                    }
                }
            )
        return data


class RequestBodySchema(ContentGenerators, BaseModel):
    content: Optional[Dict[str, MediaTypeSchema]] = None
    description: Optional[str] = None
    required: Optional[bool] = None


class ResponseHeaders(BaseModel):
    schema_: Optional[SchemaProperty | Dict[Literal["$ref"], str]] = Field(
        default=None, alias="schema"
    )
    description: Optional[str] = None


class ResponseSchema(ContentGenerators, BaseModel):
    content: Optional[Dict[str, MediaTypeSchema]] = (
        None  # {"application/json": content}
    )
    description: Optional[str] = None
    headers: Optional[Dict[str, ResponseHeaders]] = None
    links: Optional[
        List[Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]]
        | Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]
    ] = None


class BaseOperationSchema(BaseModel):
    tags: Optional[List[str] | None] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    operationId: Optional[str] = None
    x_nodeRefID: Optional[str] = Field(
        default=None,
        alias="x-nodeRefID",
        validation_alias=AliasChoices("x-nodeRefID", "x_nodeRefID"),
    )
    parameters: Optional[
        List[ParametersSchema] | Dict[str, ParametersSchema] | Dict[str, str]
    ] = None
    responses: Optional[Dict[str, ResponseSchema]] = None  # {"200": content}
    deprecated: Optional[bool] = None
    servers: Optional[ServerSchema] = None
    security: Optional[
        List[Dict[str, Dict[str, List["FlowsScopeType"]]]]
        | List[Dict[str, str]]
        | List[Any]
    ] = None
    extensions: Optional[Dict] = None
    externalDocs: Optional[ExternalDocsSchema] = None


class ReadOperationSchema(BaseOperationSchema):
    """
    Any of the following methods:

    - GET
    """

    ...
    links: Optional[
        List[Dict[str, "ReadOperationSchema"]] | Dict[str, "ReadOperationSchema"]
    ] = None


class WriteOperationSchema(BaseOperationSchema):
    """
    Any of the following methods:

    - POST
    - PUT
    - PATCH
    - DELETE
    """

    requestBody: Optional[RequestBodySchema] = None
    links: Optional[
        List[Dict[str, "WriteOperationSchema"]] | Dict[str, "WriteOperationSchema"]
    ] = None
    callbacks: Optional[
        Dict[str, Dict[str, Dict[str, "WriteOperationSchema"]]]
        | List[Dict[str, Dict[str, "WriteOperationSchema"]]]
        | "ReadOperationSchema"
    ] = None  # noqa: E501


class SchemaType:
    class Base(BaseModel):
        title: Optional[str] = None
        example: Optional[str | int | float] = None
        readOnly: Optional[bool] = None
        writeOnly: Optional[bool] = None
        nullable: Optional[bool] = None
        default: Optional[int | str | float | bool] = None

    class Integer(Base):
        type: Literal["integer"]
        minumum: Optional[int] = None
        maximum: Optional[int] = None
        exclusiveMinimum: Optional[bool] = None
        exclusiveMaximum: Optional[bool] = None
        multipleOf: Optional[int | float] = None
        format: Optional[Literal["int32", "int64", "float", "double", None]] = None

    class Number(Integer):
        type: Literal["number"]

    class String(Base):
        type: Literal["string"]
        minLength: Optional[int] = None
        maxLength: Optional[int] = None
        pattern: Optional[str] = None
        enum: Optional[List[str | int | float]] = None
        format: Optional[
            Literal[
                "date",
                "date-time",
                "email",
                "password",
                "uuid",
                "byte",
                "binary",
                "hostname",
                "ipv4",
                "ipv6",
                "uri",
                None,
            ]
        ] = None

    class Enum(String):
        enum: Optional[List[str | int | float]] = None

    class Boolean(Base):
        type: Literal["boolean"]

    class File(String):
        format: Optional[Literal["binary", "byte", None]] = None

    class AnyValueBase(Base):
        nullable: Optional[bool] = None
        description: Optional[str] = None

    class AllOf(AnyValueBase):
        allOf: List[Union["SchemaObject", Dict[Literal["$ref"], str]]]

    class AnyOf(AnyValueBase):
        anyOf: Optional[
            Dict[
                str,
                Union[
                    "SchemaType.Integer",
                    "SchemaType.String",
                    "SchemaType.Enum",
                    "SchemaType.Number",
                    "SchemaType.Boolean",
                    "SchemaType.Array",
                    "SchemaType.Object",
                    "SchemaType.Null",
                ],
            ]
            | List[
                Union[
                    "SchemaType.Integer",
                    "SchemaType.String",
                    "SchemaType.Enum",
                    "SchemaType.Number",
                    "SchemaType.Boolean",
                    "SchemaType.Array",
                    "SchemaType.Object",
                    "SchemaType.Null",
                ]
            ]
        ] = None

    class AnyType(Base):
        AnyValue: Optional[
            Dict[
                Literal["allOf", "anyOf"], Union["SchemaType.AllOf", "SchemaType.AnyOf"]
            ]
        ] = None

    class Array(Base):
        type: Literal["array"]
        minItems: Optional[int] = None
        maxItems: Optional[int] = None
        items: Optional[
            Union[
                "SchemaType.Integer",
                "SchemaType.String",
                "SchemaType.Enum",
                "SchemaType.Number",
                "SchemaType.Boolean",
                "SchemaType.Array",
                "SchemaType.Object",
                "SchemaType.Null",
                "SchemaType.File",
                "SchemaType.AnyType",
                "SchemaType.AnyOf",
                "SchemaType.AllOf",
            ]
            | Dict[Literal["$ref"], str]
        ] = None
        uniqueItems: Optional[bool] = None

    class Object(Base):
        type: Literal["object"]
        properties: Optional[
            Dict[
                Union[str, int, float],
                Union[
                    "SchemaType.Integer",
                    "SchemaType.String",
                    "SchemaType.Enum",
                    "SchemaType.Number",
                    "SchemaType.Boolean",
                    "SchemaType.Array",
                    "SchemaType.Object",
                    "SchemaType.Null",
                    "SchemaType.File",
                    "SchemaType.AnyType",
                    "SchemaType.AnyOf",
                    "SchemaType.AllOf",
                ],
            ]
            | Dict[Literal["$ref"], str]
        ] = None
        required: Optional[List[str]] = None
        additionalProperties: Optional[
            Union[bool, "SchemaType.Object", "SchemaType.Null"]
        ] = None
        minProperties: Optional[int] = None
        maxProperties: Optional[int] = None

    class Null(BaseModel):
        type: Literal["null"]


class SchemaObject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[
        Literal["string", "object", "number", "integer", "boolean", "array", "file"]
    ] = None
    properties: Optional[
        Dict[
            Union[str | int | float],
            Union[
                "SchemaType.Integer",
                "SchemaType.String",
                "SchemaType.Enum",
                "SchemaType.Number",
                "SchemaType.Boolean",
                "SchemaType.Array",
                "SchemaType.Object",
                "SchemaType.Null",
                "SchemaType.File",
                "SchemaType.AnyType",
                "SchemaType.AnyOf",
                "SchemaType.AllOf",
                Any,
            ],
        ]
    ] = None  # noqa: E501
    items: Optional[
        Union[
            "SchemaType.Integer",
            "SchemaType.String",
            "SchemaType.Enum",
            "SchemaType.Number",
            "SchemaType.Boolean",
            "SchemaType.Array",
            "SchemaType.Object",
            "SchemaType.Null",
            "SchemaType.File",
            "SchemaType.AnyType",
            "SchemaType.AnyOf",
            "SchemaType.AllOf",
        ]
        | Dict[Literal["$ref"], str]
    ] = None
    required: Optional[List[str]] = None
    maxLength: Optional[int] = None
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    minItems: Optional[int] = None
    maxItems: Optional[int] = None
    uniqueItems: Optional[bool] = None


class PathItem(BaseModel):
    get: Optional[ReadOperationSchema] = None
    put: Optional[WriteOperationSchema] = None
    post: Optional[WriteOperationSchema] = None
    patch: Optional[WriteOperationSchema] = None
    delete: Optional[WriteOperationSchema] = None
    options: Optional[WriteOperationSchema] = None
    head: Optional[WriteOperationSchema] = None
    trace: Optional[WriteOperationSchema] = None


class PathSchema(PathItem):
    summary: Optional[str] = None
    description: Optional[str] = None
    servers: Optional[List[ServerSchema]] = None
    parameters: Optional[List[ParametersSchema]] = None


class TagsSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocsSchema] = None


class ComponentsSchema(BaseModel):
    schemas: Optional[
        Dict[str, Union["SchemaObject", "SchemaType.AllOf", "SchemaType.AnyOf"]]
        | Dict[Literal["$ref"], str]
    ] = None
    parameters: Optional[
        List[Dict[str, ParametersSchema]] | Dict[str, ParametersSchema]
    ] = None
    securitySchemes: Optional[Dict[str, "SecuritySchema" | List] | List[Dict[str, "SecuritySchema" | List]]] = None
    requestBodies: Optional[List[Dict[str, RequestBodySchema]]] | Dict[str, RequestBodySchema] = None
    responses: Optional[List[Dict[str, ResponseSchema]]] | Dict[str, ResponseSchema] = None
    headers: Optional[List[Dict[str, ResponseHeaders]]] | Dict[str, ResponseHeaders] = None
    examples: Optional[
        List[Dict[str, ResponseBodyExampleSchema | RequestBodyExampleSchema]]
    ] | Dict[str, ResponseBodyExampleSchema | RequestBodyExampleSchema] = None
    links: Optional[
        List[Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]]
        | Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]
    ] | Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]] = None
    callbacks: Optional[
        Dict[str, Dict[str, Dict[str, "WriteOperationSchema"]]]
        | List[Dict[str, Dict[str, "WriteOperationSchema"]]]
        | "ReadOperationSchema"
    ] | Dict[str, Dict[str, Dict[str, "WriteOperationSchema"]]] | List[Dict[str, Dict[str, "WriteOperationSchema"]]] | "ReadOperationSchema" = None
    pathItems: Optional[
        List[Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]] | Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]
    ] = None  # noqa: E501


class FlowsScopeType(BaseModel):
    read: Optional[str] = None
    write: Optional[str] = None


class FlowsType(BaseModel):
    authorizationUrl: Optional[str] = None
    tokenUrl: Optional[str] = None
    refreshUrl: Optional[str] = None
    scopes: Optional[FlowsScopeType | Dict[str, str] | List[FlowsScopeType] | List[Dict[str, str]]] = None


class SecuritySchema(BaseModel):
    type: Optional[Literal["apiKey", "http", "oauth2", "openIdConnect", None] | Any] = (
        None
    )
    in_: Optional[Literal["query", "header", "cookie"]] = Field(
        default=None, alias="in"
    )
    name: Optional[str] = None
    description: Optional[str] = None
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional[FlowsType | List[FlowsType] | Dict[str, FlowsType] | List[Dict[str, FlowsType]]] = None
    openIdConnectUrl: Optional[str] = None


class OpenAPISpecSchema(BaseModel):
    openapi: Optional[str] = None
    info: Optional[InfoSchema] = None
    jsonSchemaDialect: Optional[str] = None
    servers: Optional[List[ServerSchema]] = None
    paths: Optional[Dict[str, PathSchema]] = None
    webhooks: Optional[Dict[str, "WriteOperationSchema"]] = None
    components: Optional[ComponentsSchema] = None
    security: Optional[Dict[str, SecuritySchema | List] | List[Dict[str, SecuritySchema | List]]] = None
    tags: Optional[List[TagsSchema]] = None
    externalDocs: Optional[ExternalDocsSchema] = None


class EnpointPathParamters(ParametersSchema):
    in_: Optional[Literal["path"]] = Field(
        default=None, alias="in", validation_alias=AliasChoices("in", "in_")
    )


class EnpointQueryParamters(ParametersSchema):
    in_: Optional[Literal["query"]] = Field(
        default=None, alias="in", validation_alias=AliasChoices("in", "in_")
    )


class EnpointHeaderParamters(ParametersSchema):
    in_: Optional[Literal["header"]] = Field(
        default=None, alias="in", validation_alias=AliasChoices("in", "in_")
    )


class EnpointCookieParamters(ParametersSchema):
    in_: Optional[Literal["cookie"]] = Field(
        default=None, alias="in", validation_alias=AliasChoices("in", "in_")
    )


class EndpointParametersSchema(BaseModel):
    path_parameters: Optional[List[EnpointPathParamters]]
    query_parameters: Optional[List[EnpointQueryParamters]]
    header_parameters: Optional[List[EnpointHeaderParamters]]
    cookie_parameters: Optional[List[EnpointHeaderParamters]]


class EndpointRequestSampleSchema(BaseModel): ...


class EndpointRequestSchema(BaseModel):
    request_body_schema: Optional[RequestBodySchema]
    request_sample: Optional[Dict[str, EndpointRequestSampleSchema]]


class EndPointNodeSchema(BaseModel):
    endpoint: str
    method: List[
        Literal["get", "post", "put", "patch", "delete", "options", "head", "trace"]
    ]
    description: Optional[str] = None
    authorizations: Optional[List[Dict[str, SecuritySchema]]] = None
    paramters: Optional[EndpointParametersSchema] = None
    request: Optional[EndpointRequestSchema] = None
    responses: Optional[Dict[str, ResponseSchema]] = None
    request_samples: Optional[Dict[str, dict]] = None
    response_samples: Optional[Dict[str, dict]] = None
