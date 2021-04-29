from typing import TypeVar

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.mixins import ContextInstanceMixin

T = TypeVar('T')


def make_context_obj(obj_type: type[ContextInstanceMixin]) -> T:
    class ContextObject(obj_type):

        def __getattribute__(self, item):
            ctx_obj = obj_type.get_current()
            if hasattr(ctx_obj, item):
                return getattr(ctx_obj, item)
            return super().__getattribute__(item)

    return ContextObject()


class ContextStorage(FSMContext):
    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def __getattribute__(self, item):
        ctx_storage = Dispatcher.get_current().current_state()
        if hasattr(ctx_storage, item):
            return getattr(ctx_storage, item)
        return super().__getattribute__(item)


update = make_context_obj(types.Update)
message = make_context_obj(types.Message)
chat = make_context_obj(types.Chat)
user = make_context_obj(types.User)
callback_query = make_context_obj(types.CallbackQuery)
inline_query = make_context_obj(types.InlineQuery)
chosen_inline_result = make_context_obj(types.ChosenInlineResult)
shipping_query = make_context_obj(types.ShippingQuery)
pre_checkout_query = make_context_obj(types.PreCheckoutQuery)
poll = make_context_obj(types.Poll)
poll_answer = make_context_obj(types.PollAnswer)
chat_member_updated = make_context_obj(types.ChatMemberUpdated)

storage = ContextStorage()
