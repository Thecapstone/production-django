from random import choice
from json import JSONEncoder
import random
from django.utils.timezone import now, timedelta
from faker import Faker

from core.utils.utils import to_snake_case

try:
    # If requests >=1.0 is available, we will use it
    import requests

    if not callable(requests.Response.json):
        requests = None
except ImportError:
    requests = None


class JsonSchemaIgnoredKeyword:
    """
    Constants for all the keywords that need to be ignored since they don't add
    in any sort of contraints on the data like range, data-type, etc. These keywords only
    provide descriptive information and can be hence ignored when generating examples.
    """

    SCHEMA = "$schema"
    TITLE = "title"
    DESCRIPTION = "description"


class JsonSchemaKeyword:
    """
    Constants for all the keywords that are needed for generating the examples when parsing through the
    JSON schema. These provide information about the data and include validators, data-types, etc.
    """

    ID = "$id"
    TYPE = "type"
    PROPERTIES = "properties"
    TYPE = "type"
    REQUIRED = "required"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    DEFINITIONS = "definitions"
    REF = "$ref"
    ITEMS = "items"


class DataType:
    """
    Constants representing the data-types currently supported.
    """

    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"
    NUMBER = "number"
    NULL = OBJECT = "object"
    ARRAY = "array"


class Node(JSONEncoder):
    """
    Represents a node in the example. This node is generated from the JSON schema.
    """

    def __init__(
        self, *, type=DataType.NULL, properties=None, items=None, definitions=None
    ):
        """
        Initializes the schema node with the required information.

        :param type: The data-type of the node. Defaults to `NULL`.
        :param properties: The properties of the node if the data-type is  an object.
        Defaults to `None`.
        :param items: The definition of the items if the node is an array.
        Defaults to `None`.
        :param definitions: The map containing the definitions to be used further in the JSON schema.
        Defaults to `None`.
        """
        self.type = type
        self.properties = properties
        self.items = items
        self.definitions = definitions
        self.value = {}  # defaults to that of an object - represented by empty `dict`

    def default(self, o):
        # return o.__dict__
        return JSONEncoder.default(self, o)


def generate_example(json_schema=None):
    """
    Generates a random example from the given JSON schema.

    :param json_schema: The JSON schema read from a `schema.json` file.
    :returns: The reference to the root example node.
    """
    fake = Faker()
    if not json_schema:
        raise Exception("Expected a JSON schema, none found!")
    # example generation logic begins from here
    type = json_schema[JsonSchemaKeyword.TYPE]
    node = Node(type=type)  # the root node
    if type == DataType.STRING:
        node.value = generate_string_example(
            type=type, data=json_schema, current_key=None
        )
    if type == DataType.INTEGER:
        node.value = generate_integer_example(
            type=type, data=json_schema, current_key=None
        )
    elif type == DataType.NUMBER:
        node.value = generate_number_example(
            type=type, data=json_schema, current_key=None
        )
    elif type == DataType.BOOLEAN:
        node.value = fake.pybool()
    elif type == DataType.ARRAY:
        node.value = generate_array_example(
            type=type, items=json_schema[JsonSchemaKeyword.ITEMS], current_key=None
        )
    elif type == DataType.OBJECT:
        node.value = generate_object_example(json_schema[JsonSchemaKeyword.PROPERTIES])
    return node.value


def generate_string_example(type, data, current_key: str = None):
    """
    Generates a random string example, this could be anything from the list of
    these strings.
    :returns: A random string.
    """

    value = [v for k, v in data.items()]
    values = data[current_key] if current_key else value[0]
    fake = Faker()
    if values.get("minLength", None):
        minLength = values["minLength"]
    else:
        minLength = fake.pyint(max_value=5)

    if values.get("maxLength", None):
        maxLength = values["maxLength"]
    else:
        maxLength = fake.pyint(min_value=minLength + 1, max_value=25)

    enum = (
        data[current_key].get("enum", None)
        if current_key
        else value[0].get("enum", None)
    )
    format_ = (
        data[current_key].get("format", None)
        if current_key
        else value[0].get("format", None)
    )
    example = (
        data[current_key].get("example", None)
        if current_key
        else value[0].get("example", None)
    )

    if enum:
        outstring = random.choice(enum)
    # elif 'pattern' in data.keys():
    elif example:
        outstring = example
    #     outstring = rstr.xeger(data['pattern'])
    elif format_:
        match format_:
            case "date-time":
                outstring = now().strftime("%Y-%m-%d %H:%M:%S")
            case "date":
                outstring = now().strftime("%Y-%m-%d")
            case "uri":
                outstring = fake.file_path()
            case "duration":
                outstring = timedelta(minutes=10).total_seconds()
            case "password":
                outstring = "********"
            case "email":
                outstring = fake.email()
            case _:
                try:
                    outstring = getattr(fake, data[current_key]["format"])()
                except AttributeError:
                    outstring = fake.pystr(
                        min_chars=minLength, max_chars=maxLength, prefix="UF -> "
                    )

    else:
        try:
            outstring = getattr(fake, to_snake_case(current_key))(
                min_chars=minLength, max_chars=maxLength, prefix="UF -> "
            )
        except TypeError:
            outstring = getattr(fake, to_snake_case(current_key))()
        except AttributeError:
            outstring = fake.pystr(min_chars=minLength, max_chars=maxLength)
    if isinstance(outstring, bytes):
        outstring = fake.pystr()
    return outstring


def generate_integer_example(type, data, current_key):
    """
    Generates a random integer example, this could be anything from the list of
    these integers.
    :returns: An integer.
    """
    fake = Faker()
    value = [v for k, v in data.items()]
    format_ = data[current_key].get("format") if current_key else value[0].get("format")
    enum = (
        data[current_key].get("enum", None)
        if current_key
        else value[0].get("enum", None)
    )
    example = (
        data[current_key].get("example", None)
        if current_key
        else value[0].get("example", None)
    )
    if enum:
        outint = random.choice(enum)
    elif example:
        outint = example
    elif format_:
        match format_:
            case "double":
                outint = fake.pyfloat()
            case _:
                try:
                    outint = getattr(fake, f"py{format_}")()
                except AttributeError:
                    outint = fake.pyint()
    else:
        outint = fake.pyint()
    return outint


def generate_number_example(type, data, current_key):
    """
    Generates a random numbers example, this could be anything from the list of
    these numbers.
    :returns: A number - decimal.
    """
    return generate_integer_example(type, data, current_key)


def generate_boolean_example():
    """
    Generates a random booleans example, this could be anything from the list of
    these booleans.
    :returns: Either True or False.
    """
    fake = Faker()
    return fake.pybool()


def generate_array_example(type, items, current_key):
    """
    Generates a random array with the items as per their schema definition.

    :param items: The schema definition of the items in the array.
    :param definitions: A `dict` that defined the schema of certain properties in-case the items use the `$ref` to
    reference it.
    """
    item_count = choice([0, 1, 2, 3])  # randomizing item count
    value = []
    type = items[JsonSchemaKeyword.TYPE]
    for i in range(0, item_count):
        node = Node(type=type)
        if type == DataType.STRING:
            node.value = generate_string_example(
                type=type, data=items, current_key=current_key
            )
        elif type == DataType.INTEGER:
            node.value = generate_integer_example(
                type=type, data=items, current_key=current_key
            )
        elif type == DataType.NUMBER:
            node.value = generate_number_example(
                type=type, data=items, current_key=current_key
            )
        elif type == DataType.BOOLEAN:
            node.value = generate_boolean_example()
        elif type == DataType.ARRAY:
            node.value = generate_array_example(
                type=type, items=items[JsonSchemaKeyword.ITEMS], current_key=current_key
            )
        elif type == DataType.OBJECT:
            node.value = generate_object_example(items[JsonSchemaKeyword.PROPERTIES])
        value.append(node.value)
    return value


def generate_object_example(properties):
    """
    Generates an object example from the properties and definitions obtained from the JSON schema.

    :param properties: A `dict` that defines the properties of the object.
    :param definitions: A `dict` that defined the schema of certain properties in-case the properties of this
    object  use the `$ref` to reference them.
    """
    value = {}
    for k, v in properties.items():
        type = (
            v[JsonSchemaKeyword.TYPE] if JsonSchemaKeyword.TYPE in v else DataType.NULL
        )
        props = None
        node = Node(type=type)
        if type == DataType.STRING:
            node.value = generate_string_example(
                type=type, data=properties, current_key=k
            )
        elif type == DataType.INTEGER:
            node.value = generate_integer_example(
                type=type, data=properties, current_key=k
            )
        elif type == DataType.NUMBER:
            node.value = generate_number_example(
                type=type, data=properties, current_key=k
            )
        elif type == DataType.BOOLEAN:
            node.value = generate_boolean_example()
        elif type == DataType.ARRAY:
            node.value = generate_array_example(
                type=type, items=v[JsonSchemaKeyword.ITEMS], current_key=k
            )
        elif type == DataType.OBJECT:
            try:
                node.value = generate_object_example(
                    v[JsonSchemaKeyword.PROPERTIES] if not props else props
                )
            except KeyError:
                node.value = {
                    "additionalProp1": "string",
                    "additionalProp2": "string",
                    "additionalProp3": "string",
                }
            except UnicodeDecodeError:
                pass
        value[k] = node.value
    return value


def resolve_ref(ref, definitions):
    """
    Resolves the reference using the definitions and provides the schema of the referenced user-type.

    :param ref: The reference string to be resolved against the definitions.
    :param definitions: The `dict`that holds the definitions of user-types.
    """
    ref = ref.split("/")[-1]
    return definitions[ref] if ref in definitions else None
