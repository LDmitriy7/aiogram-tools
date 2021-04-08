"""Contain class for passing current objects (e.g. Message) instances and derivatives to functions."""

from __future__ import annotations

import functools
import inspect
from typing import Optional, Any, Awaitable, Callable

from aiogram import types, Dispatcher as Dispatcher, Bot as Bot
from aiogram_tools._states import State, StatesGroup2
from aiogram.utils.mixins import ContextInstanceMixin

__all__ = ['CurrentObjects']


async def get_udata(obj: Dispatcher) -> dict:
    try:
        return await obj.current_state().get_data()
    except AttributeError:
        return {}


async def get_raw_state(obj: Dispatcher) -> Optional[str]:
    return await obj.current_state().get_state()


async def get_state(obj: Dispatcher) -> Optional[State]:
    return await StatesGroup2.get_current_state()


class ContextObj:

    def __init__(self, ctx_type: type[ContextInstanceMixin], get_target: callable = lambda x: x):
        self.ctx_type = ctx_type
        self.get_target = get_target

    async def get_current(self) -> Optional[Any]:
        try:
            obj = self.ctx_type.get_current()

            target = self.get_target(obj)
            if inspect.isawaitable(target):
                target = await target

            return target
        except AttributeError:
            return None

    def __repr__(self):
        return f'{type(self).__name__}(type={self.ctx_type.__name__}, target={self.get_target.__name__})'


class CurrentObjects:
    """Context telegram objects and derivatives.
    You can specify own objects and aliases at runtime.
    """
    bot = ContextObj(Bot)
    dp = ContextObj(Dispatcher)
    update = ContextObj(types.Update)
    msg = ContextObj(types.Message)
    user = ContextObj(types.User)
    chat = ContextObj(types.Chat)
    query = ContextObj(types.CallbackQuery)
    iquery = ContextObj(types.InlineQuery)

    # --- Dispatcher derivatives ---
    raw_state = ContextObj(Dispatcher, get_raw_state)
    state = ContextObj(Dispatcher, get_state)
    state_ctx = ContextObj(Dispatcher, lambda obj: obj.current_state())
    sdata = ContextObj(Dispatcher, get_udata)

    # --- Message derivatives ---
    text = ContextObj(types.Message, lambda obj: obj.text)
    msg_id = ContextObj(types.Message, lambda obj: obj.message_id)
    msg_url = ContextObj(types.Message, lambda obj: obj.url)
    reply_to = ContextObj(types.Message, lambda obj: obj.reply_to_message)
    markup = ContextObj(types.Message, lambda obj: obj.reply_markup)

    contact = ContextObj(types.Message, lambda obj: obj.contact)
    voice = ContextObj(types.Message, lambda obj: obj.voice)
    video = ContextObj(types.Message, lambda obj: obj.video)
    caption = ContextObj(types.Message, lambda obj: obj.caption)
    photo = ContextObj(types.Message, lambda obj: obj.photo)
    document = ContextObj(types.Message, lambda obj: obj.document)
    audio = ContextObj(types.Message, lambda obj: obj.audio)
    via_bot = ContextObj(types.Message, lambda obj: obj.via_bot)
    animation = ContextObj(types.Message, lambda obj: obj.animation)
    date = ContextObj(types.Message, lambda obj: obj.date)
    invoice = ContextObj(types.Message, lambda obj: obj.invoice)
    payment = ContextObj(types.Message, lambda obj: obj.successful_payment)
    new_chat_members = ContextObj(types.Message, lambda obj: obj.new_chat_members)

    # --- User derivatives ---
    user_id = ContextObj(types.User, lambda obj: obj.id)
    user_name = ContextObj(types.User, lambda obj: obj.full_name)
    username = ContextObj(types.User, lambda obj: obj.username)

    # --- CallbackQuery derivatives ---
    data = ContextObj(types.CallbackQuery, lambda obj: obj.data)
    query_id = ContextObj(types.CallbackQuery, lambda obj: obj.id)
    inline_msg_id = ContextObj(types.CallbackQuery, lambda obj: obj.inline_message_id)

    # --- Chat derivatives ---
    chat_id = ContextObj(types.Chat, lambda obj: obj.id)
    chat_type = ContextObj(types.Chat, lambda obj: obj.type)

    # --- InlineQuery derivatives ---
    idata = ContextObj(types.InlineQuery, lambda obj: obj.query)
    iquery_id = ContextObj(types.InlineQuery, lambda obj: obj.id)

    @classmethod
    @property
    def keywords(cls) -> set[str]:
        return {k for k, v in vars(cls).items() if isinstance(v, ContextObj)}

    @classmethod
    async def get(cls, ctx_obj: str) -> Optional[Any]:
        """Return current object by key."""
        obj: ContextObj = getattr(cls, ctx_obj)
        return await obj.get_current()

    @classmethod
    def set_alias(cls, ctx_obj: str, alias: str):
        setattr(cls, alias, getattr(cls, ctx_obj))

    @classmethod
    def set_ctx_obj(cls, name: str, ctx_obj: type[ContextInstanceMixin], get_target: callable = lambda x: x):
        setattr(cls, name, ContextObj(ctx_obj, get_target))

    @classmethod
    def decorate_handler(cls, handler) -> callable:
        """Now handler will receive current objects only according it's signature."""

        @functools.wraps(handler)
        async def wrapper(*args, **kwargs):
            for arg in args:
                if isinstance(arg, types.Update):
                    types.Update.set_current(arg)

            resolved_kwargs = {}
            spec_args = inspect.getfullargspec(handler).args

            for arg in spec_args:
                if arg in kwargs:
                    resolved_kwargs[arg] = kwargs[arg]
                elif arg in cls.keywords:
                    resolved_kwargs[arg] = await cls.get(arg)
            return await handler(**resolved_kwargs)

        return wrapper

    @classmethod
    def decorate(cls, func) -> Callable[..., Awaitable]:
        """Now func will receive current objects for missing args (kwargs only)."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            spec_kwargs = inspect.getfullargspec(func).kwonlyargs

            for arg in spec_kwargs:
                if arg not in kwargs:
                    if arg in cls.keywords:
                        kwargs[arg] = await cls.get(arg)

            result = func(*args, **kwargs)

            if inspect.isawaitable(result):
                return await result
            else:
                return result

        return wrapper
