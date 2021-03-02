from aiogram import types, Bot
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import BadRequest

__all__ = ['CheckMembership']


class CheckMembership(BaseMiddleware):
    """Check if user is member of group or subscribed on channel."""

    def __init__(self, chat_username: str, error_text: str = None):
        if not error_text:
            error_text = f'Error, you are not member of {chat_username}'
        self.chat = chat_username
        self.error_text = error_text
        super().__init__()

    async def is_chat_member(self, user_id: int) -> bool:
        """Check if user is currently member of chat."""
        bot = Bot.get_current()
        try:
            chat_member = await bot.get_chat_member(self.chat, user_id)
            return chat_member.is_chat_member()
        except BadRequest:
            return False

    async def on_pre_process_message(self, msg: types.Message, *args):
        is_chat_member = await self.is_chat_member(msg.from_user.id)
        if not is_chat_member:
            await msg.answer(self.error_text)
            raise CancelHandler

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, *args):
        is_chat_member = await self.is_chat_member(query.from_user.id)
        if not is_chat_member:
            await query.message.answer(self.error_text)
            raise CancelHandler
