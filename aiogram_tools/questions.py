"""Classes for creating Questions, States with Questions and Conversation States Groups."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Callable, Awaitable, Optional

from aiogram import types

from aiogram_tools.states import State, StatesGroupMeta2, StatesGroup2

KeyboardMarkup = Union[
    types.ReplyKeyboardMarkup, types.InlineKeyboardMarkup, types.ForceReply
]

AsyncFunction = Callable[[], Awaitable]


@dataclass
class QuestText:
    """Text and keyboard for an ordinary question."""
    text: str
    keyboard: KeyboardMarkup


@dataclass
class QuestFunc:
    """Async function for an extraordinary question. Will be called without args."""
    async_func: AsyncFunction


Quest = Union[str, QuestText, QuestFunc, None]
Quests = Union[Quest, list[Quest]]


class ConvState(State):
    """State with question attribute. It should be used to ask next question in conversation."""

    def __init__(self, question: Quests):
        self.question = question
        super().__init__()


class ConvStatesGroupMeta(StatesGroupMeta2):
    """Check if StatesGroup have only ConvState attributes (not State)."""

    def __new__(mcs, class_name, bases, namespace, **kwargs):
        for prop in namespace:
            if isinstance(prop, State) and not isinstance(prop, ConvState):
                err_text = f'{class_name} attrs must be instance of {ConvState.__name__}, not {State.__name__}'
                raise TypeError(err_text)

        return super().__new__(mcs, class_name, bases, namespace, **kwargs)


class ConvStatesGroup(StatesGroup2, metaclass=ConvStatesGroupMeta):
    """StatesGroup with only ConvState attributes (not State)."""


class SingleConvStatesGroup(ConvStatesGroup):
    """ConvStatesGroup with single states (no switching)."""

    @classmethod
    async def get_last_state(cls) -> Optional[State]:
        return await cls.get_current_state()

    @classmethod
    async def get_first_state(cls) -> Optional[State]:
        return await cls.get_current_state()

    @classmethod
    async def get_next_state(cls) -> None:
        return None

    @classmethod
    async def get_previous_state(cls) -> None:
        return None
