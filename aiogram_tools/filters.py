from __future__ import annotations

import re
from abc import abstractmethod
from contextlib import suppress
from typing import Optional, Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import InlineKeyboardButton, KeyboardButton


class StorageDataFilter(BoundFilter):
    """Check if all items matches the relevant items in the storage (for current User+Chat)."""

    key = 'storage'

    def __init__(self, dispatcher, storage: dict):
        self.dispatcher = dispatcher
        self.storage = storage

    def is_matching(self, storage_data: dict) -> bool:
        for key, value in self.storage.items():
            if key not in storage_data:
                return False

            if value == '*':
                continue

            if isinstance(value, (list, tuple, set)) and storage_data[key] in value:
                continue

            if storage_data[key] == value:
                continue

            return False
        return True

    async def check(self, *args) -> bool:
        state_ctx = self.dispatcher.current_state()
        storage_data = await state_ctx.get_data()
        return self.is_matching(storage_data)


class _ButtonFilter(BoundFilter):
    key = 'button'

    @abstractmethod
    def cast_button(self, button):
        """Cast button to string for matching"""

    @abstractmethod
    def cast_update(self, obj):
        """Cast update-obj to string for matching"""

    @staticmethod
    def make_regexp(text: str):
        return re.sub(r'{(.+?)}', r'(?P<\1>.+)', text)

    def __init__(self, button):
        buttons_regexps = []
        if not isinstance(button, (list, tuple, set)):
            button = [button]

        for item in button:
            if isinstance(item, str):
                button_data = item
            else:
                button_data = self.cast_button(item)

            assert isinstance(button_data, str), f'Invalid data for {self.__class__.__name__} filter'
            buttons_regexps.append(self.make_regexp(button_data))

        self.buttons_regexps = buttons_regexps

    def check_one(self, obj, button_regexp: str) -> Optional[dict]:
        obj_data = self.cast_update(obj)
        with suppress(TypeError):
            match = re.fullmatch(button_regexp, obj_data)
            if match:
                return {'button': match.groupdict()}

    async def check(self, obj) -> Union[dict, bool]:
        for regexp in self.buttons_regexps:
            result = self.check_one(obj, regexp)
            if result:
                return result
        return False


class CallbackQueryButton(_ButtonFilter):

    def cast_button(self, button: InlineKeyboardButton):
        return button.callback_data

    def cast_update(self, obj: types.CallbackQuery):
        return obj.data


class InlineQueryButton(_ButtonFilter):

    def cast_button(self, button: InlineKeyboardButton):
        if button.switch_inline_query is None:
            return button.switch_inline_query_current_chat
        return button.switch_inline_query

    def cast_update(self, obj: types.InlineQuery):
        return obj.query


class MessageButton(_ButtonFilter):

    def cast_button(self, button: Union[KeyboardButton, InlineKeyboardButton]):
        if isinstance(button, KeyboardButton):
            return button.text

        assert 'start=' in button.url, f'Invalid data for {self.__class__.__name__} filter'

        start_param = button.url.split("start=")[-1]
        return f'/start {start_param}'

    def cast_update(self, obj: types.Message):
        return obj.text
