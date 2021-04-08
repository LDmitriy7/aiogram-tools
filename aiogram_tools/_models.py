"""Contain all data models."""
from dataclasses import dataclass, field, fields, asdict, Field, is_dataclass
from typing import Union, TypeVar

from bson import ObjectId

T = TypeVar('T')

EmptyList = field(default_factory=list)
EmptyDict = field(default_factory=dict)


@dataclass
class DataModel:

    def to_dict(self):
        return asdict(self)

    @classmethod
    @property
    def field_names(cls) -> list[str]:
        return [f.name for f in fields(cls)]

    @classmethod
    @property
    def fields(cls) -> list[Field]:
        return fields(cls)

    @classmethod
    def _resolve_fields(cls, obj_data: dict) -> dict:
        resolved_data = {}
        for key, value in obj_data.items():
            if key in cls.field_names:
                resolved_data[key] = value
        return resolved_data

    @classmethod
    def from_dict(cls: type[T], obj_data: dict) -> T:
        if not obj_data:
            return None

        resolved_data = cls._resolve_fields(obj_data)

        for _field, value in resolved_data.items():
            field_type = cls.__annotations__.get(_field)
            factory = getattr(field_type, 'from_dict', None)
            if factory:
                resolved_data[_field] = factory(value)

        # noinspection PyArgumentList
        return cls(**resolved_data)


class MongoModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if '_id' not in namespace:
            namespace['_id'] = field(default=None)
            namespace.setdefault('__annotations__', {})['_id'] = None

        cls = super().__new__(mcs, name, bases, namespace)
        return cls


class MongoModel(DataModel, metaclass=MongoModelMeta):
    _id: Union[str, int, ObjectId] = None

    @property
    def id(self) -> Union[str, int, None]:
        if isinstance(self._id, ObjectId):
            return str(self._id)
        return self._id

    @id.setter
    def id(self, value: Union[str, int, None]):
        setattr(self, '_id', value)
