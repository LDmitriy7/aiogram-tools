from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Union, Optional, Literal

from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.storage import FSMContextProxy

from aiogram_tools._questions import ConvState, ConvStatesGroup, ConvStatesGroupMeta
from aiogram_tools._questions import Quest, Quests, QuestText, QuestFunc

__all__ = ['UpdateData', 'UpdateUserState', 'AnswerOnReturn']

T = TypeVar('T')
_StorageData = Union[str, int, tuple, dict, None]
StorageData = Union[_StorageData, list[_StorageData]]
NewState = Union[Literal['next', 'previous', 'exit'], ConvState, type[ConvStatesGroup], None]


def to_list(obj) -> list:
    """Cast obj to list if it's not yet."""
    if not isinstance(obj, list):
        obj = [obj]
    return obj


TypeT = type[T]


def search_in_results(obj_type: Union[TypeT, tuple[TypeT]], container: list) -> Optional[T]:
    """Recursive search for instance of obj_type in lists/tuples."""
    if isinstance(container, (list, tuple)):
        for item in container:
            obj = search_in_results(obj_type, item)
            if obj is not None:  # object found
                return obj
    elif isinstance(container, obj_type):
        return container


async def ask_question(question: Quests):
    """Send message for each Quest in question [current Chat]."""
    chat = types.Chat.get_current()
    bot = Bot.get_current()

    async def ask_quest(quest: Quest):
        if isinstance(quest, str):
            await bot.send_message(chat.id, quest)
        elif isinstance(quest, QuestText):
            await bot.send_message(chat.id, quest.text, reply_markup=quest.keyboard)
        elif isinstance(quest, QuestFunc):
            await quest.async_func()

    for q in to_list(question):
        await ask_quest(q)


@dataclass
class UpdateData:
    set_data: dict[str, StorageData] = field(default_factory=dict)
    extend_data: dict[str, StorageData] = field(default_factory=dict)
    remove_data: dict[str, StorageData] = field(default_factory=dict)
    delete_keys: Union[str, list[str]] = field(default_factory=list)
    new_state: NewState = 'next'
    on_conv_exit: Quests = None

    @property
    def state_ctx(self) -> FSMContext:
        return Dispatcher.get_current().current_state()

    def _extend_data(self, proxy: FSMContextProxy, no_error=True):
        for key, value in self.extend_data.items():
            if no_error:
                proxy.setdefault(key, [])
            proxy[key].extend(to_list(value))

    def _remove_data(self, proxy: FSMContextProxy, no_error=True):
        for key, value in self.remove_data.items():
            for item in to_list(value):
                if no_error:
                    if item in proxy[key]:
                        proxy[key].remove(item)
                else:
                    proxy[key].remove(item)

    def _delete_keys(self, proxy: FSMContextProxy, no_error=True):
        for key in to_list(self.delete_keys):
            if no_error:
                proxy.pop(key)
            else:
                del proxy[key]

    async def update_storage(self):
        """Set, extend or delete items in storage for current User+Chat."""
        async with self.state_ctx.proxy() as udata:
            udata.update(self.set_data)
            self._extend_data(udata)
            self._remove_data(udata)
            self._delete_keys(udata)

    async def get_new_state(self) -> Union[ConvState, bool, None]:
        """Return new ConvState(...) to be set."""

        if isinstance(self.new_state, ConvState):
            return self.new_state

        if isinstance(self.new_state, ConvStatesGroupMeta):
            return self.new_state.states[0]

        if self.new_state == 'previous':
            state = await ConvStatesGroup.get_current_state()
            if state and state.group:
                group: ConvStatesGroup = state.group
                new_state = await group.get_previous_state()
                return new_state

        if self.new_state == 'next':
            state = await ConvStatesGroup.get_current_state()
            if state:
                group: ConvStatesGroup = state.group
                new_state = await group.get_next_state()
                return new_state

        if self.new_state == 'exit':
            return None

        if self.new_state is None:
            return False

    async def switch_state(self, new_state: Union[ConvState, bool, None]):
        """
        If ConvState(...) passed - set new state and ask question;
        Elif None passed - finish conversation with on_conv_exit;
        Else - do nothing
        """
        if new_state is None:
            await self.state_ctx.finish()
            await ask_question(self.on_conv_exit)
        elif isinstance(new_state, ConvState):
            await new_state.set()
            await ask_question(new_state.question)


class PostMiddleware(BaseMiddleware, ABC):
    """Abstract Middleware for post processing Message and CallbackQuery."""

    @staticmethod
    @abstractmethod
    async def on_post_process_message(msg: types.Message, results: list, state_dict: dict):
        """Works after processing any message by handler."""

    @classmethod
    async def on_post_process_callback_query(cls, query: types.CallbackQuery, results: list, state_dict: dict):
        """Answer query [empty text] and call on_post_process_message(query.message)."""
        await query.answer()
        await cls.on_post_process_message(query.message, results, state_dict)


class UpdateUserState(PostMiddleware):
    """Handle returned from handler UpdateData instance.

    1) Update storage for current User+Chat (set, extend or delete items).
    2) Switch state context for current User+Chat.
      Set new ConvState(...) and ask question; or
      Finish conversation with on_conv_exit; or
      Do nothing
    """

    @staticmethod
    async def on_post_process_message(msg: types.Message, results: list, *args):
        new_data = search_in_results(UpdateData, results)

        if new_data:
            await new_data.update_storage()
            new_state = await new_data.get_new_state()
            await new_data.switch_state(new_state)


class AnswerOnReturn(PostMiddleware):
    """Ask question from returned string, QuestText or QuestFunc."""

    @staticmethod
    async def on_post_process_message(msg: types.Message, results: list, state_dict: dict):
        question = search_in_results((str, QuestText, QuestFunc), results)
        if question:
            await ask_question(question)
