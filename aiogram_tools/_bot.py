from typing import Union, Optional, List

from aiogram import Bot as _Bot
from aiogram import types
from aiogram.types import base
from aiogram.utils.payload import generate_payload


class Bot(_Bot):

    @staticmethod
    def _gen_payload(_locals: dict):
        kwargs = _locals.pop('kwargs', {})
        payload = generate_payload(['__class__', 'kwargs'], **_locals, **kwargs)
        return payload

    async def send_message(self,
                           chat_id: Union[base.Integer, base.String],
                           text: base.String,
                           reply_markup: Union[types.InlineKeyboardMarkup,
                                               types.ReplyKeyboardMarkup,
                                               types.ReplyKeyboardRemove,
                                               types.ForceReply, None] = None,
                           parse_mode: Optional[base.String] = None,
                           entities: Optional[List[types.MessageEntity]] = None,
                           disable_web_page_preview: Optional[base.Boolean] = None,
                           disable_notification: Optional[base.Boolean] = None,
                           reply_to_message_id: Optional[base.Integer] = None,
                           allow_sending_without_reply: Optional[base.Boolean] = None,
                           ) -> types.Message:
        return await super().send_message(**self._gen_payload(locals()))
