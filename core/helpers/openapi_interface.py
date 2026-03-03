from dataclasses import dataclass
from typing import Literal, Optional, List, Any, Dict, Union


@dataclass
class OpenAPISchema:
    openapi: str


@dataclass
class ContactSchema:
    name: Optional[str]
    url: Optional[str]
    email: Optional[str]


@dataclass
class LicenseSchema:
    name: Optional[str]
    identifier: Optional[str]
    url: Optional[str]


@dataclass
class InfoSchema:
    title: str
    description: Optional[str]
    termsOfService: Optional[str]
    contact: ContactSchema
    license: LicenseSchema
    version: str


@dataclass
class ExternalDocsSchema:
    description: Optional[str]
    url: Optional[str]


@dataclass
class ServerVariableSchema:
    enum: List[str]
    default: Optional[str]
    description: Optional[str]


@dataclass
class ServerPortSchema:
    enum: List[str]
    description: Optional[str]


@dataclass
class ServerEnumDefaultStyleBaseSchema:
    enum: List[str]
    default: Optional[str]


@dataclass
class ServerProtocolSchema(ServerEnumDefaultStyleBaseSchema): ...


@dataclass
class ServerEnvironmentSchema(ServerEnumDefaultStyleBaseSchema): ...


@dataclass
class ServerRegionSchema(ServerEnumDefaultStyleBaseSchema): ...


@dataclass
class ServerSchema:
    url: str
    description: Optional[str]
    variables: (
        Dict[str, ServerVariableSchema]
        | Dict[Literal["protocol"], ServerProtocolSchema]
        | Dict[Literal["port"], ServerPortSchema]
        | Dict[Literal["environment"], ServerEnvironmentSchema]
        | Dict[Literal["region"], ServerRegionSchema]
    )


@dataclass
class ParamterSchemaScheme:
    type: Literal["string", "number", "integer", "boolean", "array", "file", None]
    enum: List[str] | str
    format: Literal[
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
    default: Optional[int | str]
    minimum: Optional[int]
    maximum: Optional[int]
    nullable: Optional[bool]


@dataclass
class BaseExampleSchema:
    summary: Optional[str]
    value: List[int | str | float | dict]


@dataclass
class ParameterExampleSchema(BaseExampleSchema): ...


@dataclass
class RequestBodyExampleSchema(BaseExampleSchema):
    externalValue: Optional[str]


@dataclass
class ResponseBodyExampleSchema(BaseExampleSchema):
    externalValue: Optional[str]


@dataclass
class BoardSecuritySchema:
    security: List[
        Dict[str, Literal["cookieAuth", "jwtAuth", None] : List["FlowsScopeType"]]
    ]


class SchemaProperty:
    type: Literal["string", "number", "integer", "boolean", "array", "file", None]
    enum: Optional[List[str] | str]
    format: (
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
    )
    default: Optional[int | str]
    minimum: Optional[int]
    maximum: Optional[int]
    nullable: Optional[bool]
    description: Optional[str]


@dataclass
class MediaTypeColorEncoding:
    style: Literal[
        "form",
        "label",
        "simple",
        "spaceDelimited",
        "pipeDelimited",
        "deepObject",
        "matrix",
        None,
    ]
    explode: Optional[bool]


@dataclass
class MediaTypeEncoding:
    color: MediaTypeColorEncoding


@dataclass
class MediaTypeSchema:
    schema: (
        "SingleSchema"
        | Dict[Literal["$ref"], str]
        | Dict[Literal["oneOf", "anyOf"], Dict[Literal["$ref"], str]]
    )
    encoding: MediaTypeEncoding | Dict[str, Dict[Literal["allowReserved"], bool]]
    example: Dict[str, str]
    examples: RequestBodyExampleSchema | Dict[str, Dict[Literal["$ref"], str]]


@dataclass
class ParamtersSchema:
    name: str
    in_: str | Literal["query", "header", "path", "cookie"]
    description: Optional[str]
    required: Optional[bool]
    schema: ParamterSchemaScheme | List[Dict[Literal["$ref"], str]]
    allowReserved: Optional[bool]
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
    ]  # noqa: E501
    explode: Optional[bool]
    content: Dict[
        str,
        Dict[
            Literal[
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain; charset=utf-8",
                "text/html",
                "application/pdf",
                "image/png",
            ],
            MediaTypeSchema | Dict[Literal["schema"], Dict[Literal["$ref"], str]],
        ],
    ]
    allowEmptyValue: Optional[bool]
    example: Optional[str | int | float]
    examples: Optional[Dict[str, ParameterExampleSchema]]
    deprecated: Optional[bool]


@dataclass
class RequestBodySchema:
    content: Dict[
        str,
        Dict[
            Literal[
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain; charset=utf-8",
                "text/html",
                "application/pdf",
                "image/png",
            ],
            MediaTypeSchema | Dict[Literal["schema"], Dict[Literal["$ref"], str]],
        ],
    ]
    description: Optional[str]
    required: Optional[bool]


@dataclass
class ResponseHeaders:
    schema: SchemaProperty
    description: Optional[str]


@dataclass
class ResponseSchema:
    content: Dict[
        str,
        Dict[
            Literal[
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain; charset=utf-8",
                "text/html",
                "application/pdf",
                "image/png",
            ],
            MediaTypeSchema | Dict[Literal["schema"], Dict[Literal["$ref"], str]],
        ],
    ]
    description: Optional[str]
    headers: Dict[str, ResponseHeaders]


@dataclass
class BaseOperationSchema:
    tags: List[str] | None
    summary: Optional[str]
    description: Optional[str]
    operationId: str
    parameters: Optional[ParamtersSchema | List[Dict[Literal["$ref"], str]]]
    responses: Dict[
        Literal[
            "200",
            "201",
            "400",
            "401",
            "403",
            "404",
            "405",
            "406",
            "409",
            "429",
            "500",
            "501",
            None,
        ],
        ResponseSchema,
    ]
    deprecated: Optional[bool]
    servers: Optional[ServerSchema]
    security: Optional[List[BoardSecuritySchema]]
    extensions: Optional[Dict]
    externalDocs: Optional[ExternalDocsSchema]


@dataclass
class ReadOperationSchema(BaseOperationSchema):
    """
    Any of the following methods:

    - GET
    """

    ...
    links: "ReadOperationSchema"


@dataclass
class WriteOperationSchema(BaseOperationSchema):
    """
    Any of the following methods:

    - POST
    - PUT
    - PATCH
    - DELETE
    """

    requestBody: RequestBodySchema
    links: "WriteOperationSchema"
    callbacks: (
        Dict[str, Dict[str, "WriteOperationSchema"]]
        | Dict[str, List[Dict[str, "WriteOperationSchema"]]]
    )


class SchemaType:
    @dataclass
    class Base:
        readOnly: Optional[bool]
        writeOnly: Optional[bool]

    class Integer(Base):
        type: Literal["integer"]
        minumum: Optional[int]
        maximum: Optional[int]
        exclusiveMinimum: Optional[bool]
        exclusiveMaximum: Optional[bool]
        multipleOf: Optional[int | float]
        format: Optional[Literal["int32", "int64", "float", "double", None]]

    class String(Base):
        type: Literal["string"]
        minLength: Optional[int]
        maxLength: Optional[int]
        pattern: str
        format: Literal[
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

    class Enum(String):
        enum: Optional[List[str | int | float]]

    class Number(Base):
        type: Literal["number"]

    class Boolean(Base):
        type: Literal["boolean"]

    class File(String):
        format: Literal["binary", "byte", None]

    class AnyValueBase(Base):
        nullable: Optional[bool]
        description: Optional[str]

    class AllOf(AnyValueBase):
        allOf: List[
            Union[
                "SchemaType.Integer",
                "SchemaType.String",
                "SchemaType.Enum",
                "SchemaType.Number",
                "SchemaType.Boolean",
                "SchemaType.Array",
                "SchemaType.Object ",
                "SchemaType.Null",
            ]
        ]  # noqa: E501

    class AnyOf(AnyValueBase):
        anyOf: List[
            Union[
                "SchemaType.Integer",
                "SchemaType.String",
                "SchemaType.Enum",
                "SchemaType.Number",
                "SchemaType.Boolean",
                "SchemaType.Array",
                "SchemaType.Object ",
                "SchemaType.Null",
            ]
        ]

    class AnyType(Base):
        AnyValue: Dict[
            Literal["allOf", "anyOf"], Union["SchemaType.AllOf", "SchemaType.AnyOf"]
        ]

    class Array(Base):
        type: Literal["array"]
        minItems: Optional[int]
        maxItems: Optional[int]
        items: Union[
            "SchemaType.Integer",
            "SchemaType.String",
            "SchemaType.Enum",
            "SchemaType.Number",
            "SchemaType.Boolean",
            "SchemaType.Array",
            "SchemaType.Object ",
            "SchemaType.Null",
        ]
        uniqueItems: Optional[bool]

    class Object(Base):
        type: Literal["object"]
        properties: Dict[
            str,
            Union[
                "SchemaType.Integer",
                "SchemaType.String",
                "SchemaType.Enum",
                "SchemaType.Number",
                "SchemaType.Boolean",
                "SchemaType.Array",
                "SchemaType.Object ",
                "SchemaType.Null",
            ],
        ]
        required: List[str]
        additionalProperties: Optional[
            Union[bool, "SchemaType.Object", "SchemaType.Null"]
        ]
        minProperties: Optional[int]
        maxProperties: Optional[int]

    class Null:
        type: Literal["null"]


@dataclass
class SingleSchema:
    title: Optional[str]
    description: Optional[str]
    type: Literal["object"]
    properties: (
        SchemaType.Integer
        | SchemaType.String
        | SchemaType.Number
        | SchemaType.Boolean
        | SchemaType.Array
        | SchemaType.Object
        | SchemaType.Null
        | SchemaType.File
        | SchemaType.AnyType
        | SchemaType.AnyOf
        | SchemaType.AllOf
    )  # noqa: E501
    required: Optional[List[str]]


@dataclass
class PathItem:
    get: Optional[ReadOperationSchema]
    put: Optional[WriteOperationSchema]
    post: Optional[WriteOperationSchema]
    patch: Optional[WriteOperationSchema]
    delete: Optional[WriteOperationSchema]
    options: Optional[WriteOperationSchema]
    head: Optional[WriteOperationSchema]
    trace: Optional[WriteOperationSchema]


@dataclass
class Paths(PathItem):
    summary: Optional[str]
    description: Optional[str]
    servers: Optional[List[ServerSchema]]
    parameters: Optional[List[ParamtersSchema] | Dict[Literal["$ref"], str]]


@dataclass
class TagsSchema:
    name: str
    description: Optional[str]
    externalDocs: Optional[ExternalDocsSchema]


@dataclass
class ComponentsSchema:
    schemas: List[Dict[str, SingleSchema]]
    parameters: List[Dict[str, ParamtersSchema]]
    securitySchemes: List[Dict[str, "SecuritySchema"]]
    requestBodies: List[Dict[str, RequestBodySchema]]
    responses: List[Dict[str, ResponseSchema]]
    headers: Optional[List[Dict[str, ResponseHeaders]]]
    examples: Optional[
        List[Dict[str, ResponseBodyExampleSchema | RequestBodyExampleSchema]]
    ]
    links: Optional[
        List[Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]]
    ]
    callbacks: Optional[
        List[Dict[str, Dict[str, "WriteOperationSchema"] | "ReadOperationSchema"]]
    ]
    pathItems: (
        List[Dict[str, Union["WriteOperationSchema", "ReadOperationSchema"]]]
        | List[Dict[Literal["$ref"], str]]
    )


@dataclass
class FlowsScopeType:
    read: Optional[str]
    write: Optional[str]


@dataclass
class FlowsType:
    authorizationUrl: Optional[str]
    tokenUrl: Optional[str]
    refreshUrl: Optional[str]
    scopes: FlowsScopeType


@dataclass
class SecuritySchema:
    type: Literal["apiKey", "http", "oauth2", "openIdConnect", None] | Any
    in_: Literal["query", "header", "cookie", None]
    name: Optional[str]
    description: Optional[str]
    scheme: Optional[str]
    bearerFormat: Optional[str]
    flows: FlowsType
    openIdConnectUrl: Optional[str]


@dataclass
class OpenAPISpecInterface:
    openapi: str
    info: InfoSchema
    jsonSchemaDialect: Optional[str]
    servers: List[ServerSchema]
    paths: Dict[str, Paths]
    webhooks: Dict[str, "WriteOperationSchema"]
    components: ComponentsSchema
    security: List[SecuritySchema]
    tags: List[Dict[Literal["$ref"], str] | TagsSchema]
    externalDocs: ExternalDocsSchema
