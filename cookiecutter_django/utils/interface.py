import json
import string
import random
from logging import getLogger
from typing import Any, ClassVar, Literal
from django.utils.timezone import now
from drf_spectacular.extensions import OpenApiSerializerFieldExtension
from drf_spectacular.plumbing import build_array_type
from pydantic import BaseModel as _BaseModel


logger = getLogger(__file__)


class BaseModel(_BaseModel, OpenApiSerializerFieldExtension):
    target_class: ClassVar[str]
    is_list: ClassVar[bool | None] = None

    @classmethod
    def map_serializer_field(cls, auto_schema, direction):
        if cls.is_list:
            # Return schema for an array of objects
            return build_array_type(cls.model_json_schema())
        else:
            # Return schema for a single object
            return cls.model_json_schema()

    @classmethod
    def replace_ref(
        cls, defs: dict, schema: dict | list
    ) -> dict[str, Any] | list | Any:
        """Function replace all ref with thier object

        Args:
            defs (dict): _description_
            schema (dict | list): _description_

        Returns:
            dict[str,Any]|list|Any: _description_
        """
        if isinstance(schema, list):
            return [cls.replace_ref(defs, value) for value in schema]
        elif isinstance(schema, dict):
            if schema.get("$ref"):
                return defs.get(schema.get("$ref"), schema)
            else:
                return {
                    key: (
                        cls.replace_ref(defs, value)
                        if type(value) in [list, dict]
                        else value
                    )
                    for key, value in schema.items()
                }
        return schema

    @classmethod
    def get_defs(cls, data: dict) -> dict[str, Any]:
        res = {f"#/$defs/{key}": value for key, value in data.get("$defs", {}).items()}
        return cls.replace_ref(res, res)

    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict[str, Any]:
        """Generate jsonschema of the model.

        Returns:
            dict[str,Any]: _description_
        """
        data = super().model_json_schema(*args, **kwargs)
        defs: dict = cls.get_defs(data)
        res = cls.replace_ref(defs=defs, schema=data)
        res.pop("$defs", None)
        return res

    @classmethod
    def model_json_schema_no_defs(cls, *args, **kwargs) -> dict[str, Any]:
        """Generate jsonschema of the model.

        Returns:
            dict[str,Any]:
        """
        data = super().model_json_schema(*args, **kwargs)
        defs: dict = cls.get_defs(data)
        res = cls.replace_ref(defs=defs, schema=data)
        res.pop("$defs", None)
        return res

    def remove_circular_refs(self, ob, _seen=None):
        if _seen is None:
            _seen = set()
        if id(ob) in _seen:
            # circular reference, remove it.
            return None
        _seen.add(id(ob))
        res = ob
        if isinstance(ob, dict):
            res = {
                self.remove_circular_refs(k, _seen): self.remove_circular_refs(v, _seen)
                for k, v in ob.items()
            }
        elif isinstance(ob, (list, tuple, set, frozenset)):
            res = type(ob)(self.remove_circular_refs(v, _seen) for v in ob)
        # remove id again; only *nested* references count
        _seen.remove(id(ob))
        return res

    def model_dump_no_refs(self, *args, **kwargs) -> dict[str, Any]:
        logger.info("Started .model_dump_no_refs")
        data = self.model_dump(*args, **kwargs)
        logger.info("Finished .model_dump_no_refs")
        return data

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        logger.info("Started .model_dump")
        data = super().model_dump(*args, **kwargs)
        defs: dict = self.get_defs(data)
        res = self.replace_ref(defs=defs, schema=data)
        res.pop("$defs", None)
        logger.info("Finished .model_dump")
        return res

    @classmethod
    def to_representation(cls, content):
        main = cls(**content).model_dump(by_alias=True)
        return cls(**main)

    def dict_plain(self) -> dict:
        return json.loads(self.model_dump(by_alias=True, mode="json"))

    def generatestring(data):
        letters = string.ascii_uppercase
        if "minLength" in data.keys():
            minLength = data["minLength"]
        else:
            minLength = 5

        if "maxLength" in data.keys():
            maxLength = data["maxLength"]
        else:
            maxLength = 25

        if "enum" in data.keys():
            outstring = random.choice(data["enum"])
        # elif 'pattern' in data.keys():
        #     outstring = rstr.xeger(data['pattern'])
        elif "format" in data.keys():
            if data["format"] == "date-time":
                outstring = now.strftime("%Y-%m-%d %H:%M:%S")
            elif data["format"] == "date":
                outstring = now.strftime("%Y-%m-%d")
            else:
                pass
        else:
            outstring = "".join(
                random.choice(letters) for i in range(minLength, maxLength)
            )

        return outstring

    def generatenumber(data):
        if "enum" in data.keys():
            outnumber = random.choice(data["enum"])
        elif "format" in data.keys():
            if data["format"] in ("float", "double"):
                outnumber = random.random()
                # outdict[key] = random.uniform(10.5, 75.5)  Returns value within a range
            else:
                pass
        else:
            outnumber = random.random()

        return outnumber

    def generateinteger(data):
        if "multipleOf" in data.keys():
            multipleOf = data["multipleOf"]
        else:
            multipleOf = 1

        if "minimum" in data.keys():
            int32minimum = data["minimum"] / multipleOf
            int64minimum = data["minimum"] / multipleOf
        else:
            int32minimum = 100000
            int64minimum = 10000000000

        if "maximum" in data.keys():
            int32maximum = data["maximum"] / multipleOf
            int64maximum = data["maximum"] / multipleOf
        else:
            int32maximum = 9000000
            int64maximum = 500000000000

        if "enum" in data.keys():
            outinteger = random.choice(data["enum"])
        elif "format" in data.keys():
            if data["format"] == "int32":
                outinteger = random.randint(int32minimum, int32maximum) * multipleOf
            elif data["format"] == "int64":
                outinteger = random.randint(int64minimum, int64maximum) * multipleOf
            else:
                pass
        else:
            outinteger = random.randint(int64minimum, int64maximum) * multipleOf

        return outinteger

    def generate_value(self, data, outdict):
        outlist = []
        for key, value in data.items():
            if "type" in data[key].keys():
                if data[key]["type"] == "string":
                    outdict[key] = self.generatestring(data[key])
                elif data[key]["type"] == "boolean":
                    outdict[key] = random.choice([True, False])
                elif data[key]["type"] == "number":
                    outdict[key] = self.generatenumber(data[key])
                elif data[key]["type"] == "integer":
                    outdict[key] = self.generateinteger(data[key])
                elif data[key]["type"] == "array":
                    if "minItems" in data[key]:
                        minItems = data[key]["minItems"]
                    else:
                        minItems = 1
                    if "maxItems" in data[key]:
                        maxItems = data[key]["maxItems"]
                    else:
                        maxItems = 3
                    if maxItems <= minItems:
                        maxItems = minItems + 1
                    arrayItems = random.randint(minItems, maxItems)
                    if "type" in data[key]["items"].keys():
                        array = []
                        if data[key]["items"]["type"] == "string":
                            for n in range(0, arrayItems):
                                arrayproperty = self.generatestring(data[key]["items"])
                                array.append(arrayproperty)
                            outdict[key] = array
                        elif data[key]["items"]["type"] == "integer":
                            for n in range(0, arrayItems):
                                arrayproperty = self.generateinteger(data[key]["items"])
                                array.append(arrayproperty)
                            outdict[key] = array
                        elif data[key]["items"]["type"] == "number":
                            for n in range(0, arrayItems):
                                arrayproperty = self.generatenumber(data[key]["items"])
                                array.append(arrayproperty)
                            outdict[key] = array
                        elif data[key]["items"]["type"] == "object":
                            arraydict = {}
                            arrayproperties = data[key]["items"]["properties"]
                            outdict[key] = self.generatevalue(
                                arrayproperties, arraydict
                            )
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        outlist.append(outdict)
        return outlist


class BaseModelNoDefs(BaseModel):
    @classmethod
    def model_json_schema(cls, *args, **kwargs) -> dict[str, Any]:
        """Generate jsonschema of the model.

        Returns:
            dict[str,Any]: _description_
        """
        data = super().model_json_schema(*args, **kwargs)
        defs: dict = cls.get_defs(data)
        res = cls.replace_ref(defs=defs, schema=data)
        res.pop("$defs", None)
        return res

    def dict_plain(self) -> dict:
        return json.loads(self.model_dump_json())


class BaseTypeModel(BaseModelNoDefs):
    type: Literal["--none--"] = "--none--"

    @classmethod
    @property
    def object_type(cls) -> str:
        """return the type

        Returns:
            str: _description_
        """
        try:
            return cls.model_fields["type"].default
        except AttributeError:
            return "unknown"
