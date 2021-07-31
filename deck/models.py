import datetime
import functools
import re
import typing

import attr
import cattr
from cattr.preconf.json import make_converter
from dateutil.parser import parse

converter = make_converter()
cattr.global_converter = converter
converter.register_structure_hook(datetime.datetime, lambda ts, _: parse(ts))

T = typing.TypeVar("T")


def to_snake(s):
    return re.sub(r"([A-Z]\w+$)", "_\\1", s).lower()


def json_to_snake(d):
    if isinstance(d, list):
        return [json_to_snake(i) if isinstance(i, (dict, list)) else i for i in d]

    return {
        to_snake(a): json_to_snake(b) if isinstance(b, (dict, list)) else b
        for a, b in d.items()
    }


def deserialize(model: typing.Generic[T]) -> typing.Callable:
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs) -> T:
            json_ = fn(*args, **kwargs)
            json_ = json_to_snake(json_)
            return cattr.structure(json_, model)

        return inner

    return outer


@attr.s(auto_attribs=True, frozen=True)
class Label:
    id: typing.Optional[int]
    card_id: typing.Optional[int]
    board_id: typing.Optional[int]
    color: typing.Optional[str]
    title: typing.Optional[str]


@attr.s(auto_attribs=True, frozen=True)
class User:
    primary_key: str
    uid: str
    displayname: str


@attr.s(auto_attribs=True, frozen=True)
class Card:
    id: int
    title: str
    stack_id: int
    last_modified: int
    created_at: int
    owner: str
    order: int
    archived: bool
    notified: bool = False
    deleted_at: int = 0
    duedate: typing.Optional[str] = None
    description: typing.Optional[str] = None
    type: str = "plain"
    labels: typing.Optional[typing.List[Label]] = attr.Factory(list)


@attr.s(auto_attribs=True, frozen=True)
class Stack:
    id: int
    title: str
    board_id: int
    order: int
    deleted_at: int = 0
    cards: typing.List[Card] = attr.Factory(list)


@attr.s(auto_attribs=True, frozen=True)
class Board:
    id: int
    title: str
    owner: str
    color: str
    archived: bool
    deleted_at: int = 0
    last_modified: int = 0
    users: typing.List = attr.Factory(list)
    acl: typing.List = attr.Factory(list)
    labels: typing.List[Label] = attr.Factory(list)
    permissions: typing.Dict[str, bool] = attr.Factory(dict)
