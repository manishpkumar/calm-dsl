from collections import OrderedDict
import json
from json import JSONEncoder, JSONDecoder
import sys

from ruamel.yaml import YAML, resolver

from .schema import get_schema_details


def _validate(vdict, name, value):

    if not (name.startswith('__') and name.endswith('__')):

        try:

            if name not in vdict:
                raise TypeError("Unknown attribute {} given".format(name))
            ValidatorType, is_array = vdict[name]

        except TypeError:

            # Check if value is a variable
            types = EntityTypeBase.get_entity_types()
            VariableType = types.get("Variable", None)
            if not VariableType:
                raise TypeError("Variable type not defined")
            if not isinstance(value, VariableType):
                raise

            # Validate and set variable

            # get validator for variables
            ValidatorType, _ = vdict["variables"]
            is_array = False

            # Set name attribute in variable
            # TODO - use __set__, __get__ interfaces for descriptors
            # TODO - Avoid recursion. caller class should not be a VariableType
            setattr(value, "name", name)

        if ValidatorType is not None:
            ValidatorType.validate(value, is_array)


class EntityDict(OrderedDict):

    def __init__(self, validators):
        self.validators = validators

    def _validate(self, name, value):
        vdict = self.validators
        _validate(vdict, name, value)

    def __setitem__(self, name, value):

        self._validate(name, value)
        super().__setitem__(name, value)


class EntityTypeBase(type):

    subclasses = {}

    @classmethod
    def get_entity_types(cls):
        return cls.subclasses

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "__schema_name__"):
            raise TypeError("Entity type does not have a schema name")

        schema_name = getattr(cls, "__schema_name__")
        cls.subclasses[schema_name] = cls

        # Handle base case (Entity)
        if not schema_name:
            return

        # Set properties on metaclass by fetching from schema
        (schema_props,
         validators,
         defaults,
         display_map) = get_schema_details(schema_name)

        # Set validator dict on metaclass for each prop.
        # To be used during __setattr__() to validate props.
        # Look at validate() for details.
        setattr(cls, "__validator_dict__", validators)

        # Set defaults which will be used during serialization.
        # Look at json_dumps() for details
        setattr(cls, "__default_attrs__", defaults)

        # Attach schema properties to metaclass
        setattr(cls, "__schema_props__", schema_props)

        # Attach display map for compile/decompile
        setattr(cls, "__display_map__", display_map)


class EntityType(EntityTypeBase):

    __schema_name__ = None
    __openapi_type__ = None

    @classmethod
    def to_yaml(mcls, representer, node):
        yaml_tag = resolver.BaseResolver.DEFAULT_MAPPING_TAG
        return representer.represent_mapping(yaml_tag, node.compile())

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):

        schema_name = mcls.__schema_name__

        # Handle base case (Entity)
        if not schema_name:
            return dict()

        validators = getattr(mcls, '__validator_dict__')

        # Class creation would happen using EntityDict() instead of dict().
        # This is done to add validations to class attrs during class creation.
        # Look at __setitem__ in EntityDict
        return EntityDict(validators)

    def __new__(mcls, name, bases, entitydict):

        cls = super().__new__(mcls, name, bases, entitydict)

        openapi_type = getattr(mcls, "__openapi_type__")
        setattr(cls, "__kind__", openapi_type)

        for k, v in cls.get_default_attrs().items():
            # Check if attr was set during class creation
            # else - set default value
            if not hasattr(cls, k):
                setattr(cls, k, v)

        return cls

    @classmethod
    def validate(mcls, name, value):
        if hasattr(mcls, "__validator_dict__"):
            vdict = mcls.__validator_dict__
            _validate(vdict, name, value)

    def __setattr__(cls, name, value):

        # Validate attribute
        cls.validate(name, value)

        # Set attribute
        super().__setattr__(name, value)

    def __str__(cls):
        return cls.__name__

    def __repr__(cls):
        return cls.__name__

    def get_user_attrs(cls):
        user_attrs = {}
        for name, value in cls.__dict__.items():
            if not (name.startswith('__') and name.endswith('__')):
                user_attrs[name] = value

        return user_attrs

    @classmethod
    def get_default_attrs(mcls):
        default_attrs = {}
        if hasattr(mcls, '__default_attrs__'):
            default_attrs = getattr(mcls, '__default_attrs__')

        return default_attrs

    @classmethod
    def update_attrs(mcls, attrs):

        if not hasattr(mcls, "__validator_dict__"):
            return

        vdict = getattr(mcls, "__validator_dict__")
        if "variables" not in vdict:
            return

        # Get a copy of given variables
        attrs["variables"] = list(attrs.get("variables", []))

        # Update list of variables with given class-level variables
        del_keys = []
        for k, v in attrs.items():
            if k not in vdict:
                # ToDo - Check again if it is a variable
                attrs["variables"].append(v)
                del_keys.append(k)

        # Delete attrs
        for k in del_keys:
            attrs.pop(k)

    def get_all_attrs(cls):
        default_attrs = cls.get_default_attrs()
        user_attrs = cls.get_user_attrs()

        # Merge both attrs. Overwrite user attrs on default attrs
        return {**default_attrs, **user_attrs}

    def compile(cls):

        attrs = cls.get_all_attrs()
        cls.update_attrs(attrs)

        # convert keys to api schema
        cdict = {}
        display_map = getattr(type(cls), "__display_map__")
        for k, v in attrs.items():
            cdict.setdefault(display_map[k], v)

        # Add name & description if present
        if "name" in cdict and cdict["name"] == "":
            cdict["name"] = cls.__name__

        if "description" in cdict and cdict["description"] == "":
            cdict["description"] = cls.__doc__ if cls.__doc__ else ""

        # Add extra info for roundtrip
        # TODO - remove during serialization before sending to server
        # cdict['__kind__'] = cls.__kind__

        return cdict

    @classmethod
    def decompile(mcls, cdict):

        # Remove extra info
        name = cdict.pop("name", mcls.__schema_name__)
        description = cdict.pop("description", None)
        # kind = cdict.pop('__kind__')

        # Convert attribute names to x-calm-dsl-display-name, if given
        attrs = {}
        display_map = getattr(mcls, "__display_map__")
        for k, v in cdict.items():
            attrs.setdefault(display_map.inverse[k], v)

        # Create new class based on type
        cls = mcls(name, (Entity, ), attrs)
        cls.__doc__ = description

        return cls

    def json_dumps(cls, pprint=False, sort_keys=False):

        dump = json.dumps(cls,
                          cls=EntityJSONEncoder,
                          sort_keys=sort_keys,
                          indent=4 if pprint else None,
                          separators=(",", ": ") if pprint else (",", ":"))

        # Add newline for pretty print
        return dump + "\n" if pprint else dump

    def json_loads(cls, data):
        return json.loads(data, cls=EntityJSONDecoder)

    def yaml_dump(cls, stream=sys.stdout):

        yaml = YAML()
        types = EntityTypeBase.get_entity_types()

        for _, t in types.items():
            yaml.register_class(t)

        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(cls, stream=stream)


class Entity(metaclass=EntityType):
    pass


class EntityJSONEncoder(JSONEncoder):
    def default(self, cls):

        if not hasattr(cls, '__kind__'):
            return super().default(cls)

        return cls.compile()


class EntityJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, attrs):

        if "__kind__" not in attrs:
            return attrs

        kind = attrs["__kind__"]
        types = EntityTypeBase.get_entity_types()

        Type = types.get(kind, None)
        if not Type:
            raise TypeError("Unknown entity type {} given".format(kind))

        return Type.decompile(attrs)
