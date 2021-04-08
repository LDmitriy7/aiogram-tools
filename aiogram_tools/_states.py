import inspect
from typing import Optional

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup, StatesGroupMeta


class StatesGroupMeta2(StatesGroupMeta):

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super(StatesGroupMeta, mcs).__new__(mcs, name, bases, namespace)

        states = []
        childs = []

        cls._group_name = name

        for name, prop in namespace.items():

            if isinstance(prop, State):
                states.append(prop)
                StatesGroup2.all_states_groups_states.add(prop)
            elif inspect.isclass(prop) and issubclass(prop, StatesGroup):
                childs.append(prop)
                prop._parent = cls

        cls._parent = None
        cls._childs = tuple(childs)
        cls._states = tuple(states)
        cls._state_names = tuple(state.state for state in states)

        return cls

    @property
    def state_ctx(cls) -> FSMContext:
        return Dispatcher.get_current().current_state()


class StatesGroup2(StatesGroup, metaclass=StatesGroupMeta2):
    all_states_groups_states = set()

    # --- get methods ---

    @classmethod
    async def get_current_state(cls) -> Optional[State]:
        """Search current State instance in all StatesGroups."""
        try:
            state_name = await cls.state_ctx.get_state()
            return cls.get_state_by_name(state_name)
        except AttributeError:
            return None

    @classmethod
    async def get_next_state(cls) -> Optional[State]:
        state = await cls.get_current_state()

        try:
            group_states: tuple[State] = state.group.states
        except AttributeError:
            return None

        next_step = group_states.index(state) + 1
        return cls.get_state_by_index(group_states, next_step)

    @classmethod
    async def get_previous_state(cls) -> Optional[State]:
        state = await cls.get_current_state()

        try:
            group_states: tuple[State] = state.group.states
        except AttributeError:
            return None

        previous_step = group_states.index(state) - 1
        return cls.get_state_by_index(group_states, previous_step)

    @classmethod
    async def get_first_state(cls) -> Optional[State]:
        state = await cls.get_current_state()

        try:
            group_states: tuple[State] = state.group.states
            return group_states[0]
        except AttributeError:
            return None

    @classmethod
    async def get_last_state(cls) -> Optional[State]:
        state = await cls.get_current_state()

        try:
            group_states: tuple[State] = state.group.states
            return group_states[-1]
        except AttributeError:
            return None

    # --- set methods ---

    @classmethod
    async def set_next_state(cls) -> Optional[State]:
        current_state = await cls.get_current_state()
        if current_state:
            states_group: StatesGroup2 = current_state.group
            next_state = await states_group.get_next_state()
            if isinstance(next_state, State):
                await next_state.set()
                return next_state

        await cls.state_ctx.set_state(None)

    @classmethod
    async def set_previous_state(cls) -> Optional[State]:
        current_state = await cls.get_current_state()
        if current_state:
            states_group: StatesGroup2 = current_state.group
            previous_state = await states_group.get_previous_state()
            if isinstance(previous_state, State):
                await previous_state.set()
                return previous_state

        await cls.state_ctx.set_state(None)

    @classmethod
    async def set_first_state(cls) -> Optional[State]:
        current_state = await cls.get_current_state()
        if current_state:
            states_group: StatesGroup2 = current_state.group
            first_state = await states_group.get_first_state()
            if isinstance(first_state, State):
                await first_state.set()
                return first_state

        await cls.state_ctx.set_state(None)

    @classmethod
    async def set_last_state(cls) -> Optional[State]:
        current_state = await cls.get_current_state()
        if current_state:
            states_group: StatesGroup2 = current_state.group
            last_state = await states_group.get_last_state()
            if isinstance(last_state, State):
                await last_state.set()
                return last_state

        await cls.state_ctx.set_state(None)

    # --- Auxiliary methods ---

    @classmethod
    def get_state_by_name(cls, state_name: str) -> Optional[State]:
        """Search for State with state_name in all StatesGroups."""
        for state in cls.all_states_groups_states:
            if state.state == state_name:
                return state

    @staticmethod
    def get_state_by_index(group_states: tuple[State], index: int) -> Optional[State]:
        """Return state with passed index from group or None. Exception safety."""
        if 0 <= index < len(group_states):
            return group_states[index]
