from __future__ import annotations

import asyncio
from typing import TypeVar, Optional, List

from aiogram import Dispatcher as _Dispatcher, executor
from aiogram import types
from aiogram.types import base

from aiogram_tools.filters import CallbackQueryButton, InlineQueryButton, MessageButton
from aiogram_tools.filters import StorageDataFilter

T = TypeVar('T')


class Dispatcher(_Dispatcher):

    @staticmethod
    def _gen_payload(locals_: dict, exclude: list[str] = None, default_exclude=('self', 'cls')):
        kwargs = locals_.pop('kwargs', {})
        locals_.update(kwargs)

        if exclude is None:
            exclude = []
        return {key: value for key, value in locals_.items() if
                key not in exclude + list(default_exclude)
                and value is not None
                and not key.startswith('_')}

    def _setup_filters(self):
        filters_factory = self.filters_factory
        filters_factory.bind(StorageDataFilter, exclude_event_handlers=[
            self.errors_handlers,
            self.poll_handlers,
            self.poll_answer_handlers,
        ])
        filters_factory.bind(CallbackQueryButton, event_handlers=[
            self.callback_query_handlers
        ])
        filters_factory.bind(InlineQueryButton, event_handlers=[
            self.inline_query_handlers
        ])
        filters_factory.bind(MessageButton, event_handlers=[
            self.message_handlers,
            self.edited_message_handlers,
        ])

        super()._setup_filters()

    def run_polling(self, *, loop=None, skip_updates=False, reset_webhook=True,
                    on_startup=None, on_shutdown=None, timeout=20, relax=0.1, fast=True):
        payload = self._gen_payload(locals())
        executor.start_polling(self, **payload)

    def run_webhook(self, webhook_host, webhook_path, *, loop=None, skip_updates=None,
                    on_startup=None, on_shutdown=None, check_ip=False, retry_after=None,
                    route_name=executor.DEFAULT_ROUTE_NAME,
                    certificate: Optional[base.InputFile] = None,
                    ip_address: Optional[base.String] = None,
                    max_connections: Optional[base.Integer] = None,
                    allowed_updates: Optional[List[base.String]] = None,
                    **kwargs):
        loop = self.loop or asyncio.get_event_loop()
        webhook_task = loop.create_task(self.bot.set_webhook(
            webhook_host + webhook_path,
            certificate=certificate,
            ip_address=ip_address,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=skip_updates,
        ))
        if not loop.is_running():
            loop.run_until_complete(webhook_task)

        executor.start_webhook(
            self,
            webhook_path=webhook_path,
            loop=loop,
            skip_updates=skip_updates,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            check_ip=check_ip,
            retry_after=retry_after,
            route_name=route_name,
            **kwargs
        )

    def message_handler(self, *custom_filters, text=None, commands=None, regexp=None, button=None,
                        content_types=None, chat_type=None, state=None, storage=None,
                        is_reply=None, is_forwarded=None, user_id=None, chat_id=None,
                        text_startswith=None, text_contains=None, text_endswith=None,
                        run_task=None, **kwargs):
        payload = self._gen_payload(locals(), exclude=['custom_filters'])
        return super().message_handler(*custom_filters, **payload)

    def edited_message_handler(self, *custom_filters, text=None, commands=None, regexp=None, button=None,
                               content_types=None, chat_type=None, state=None, storage=None,
                               is_reply=None, is_forwarded=None, user_id=None, chat_id=None,
                               text_startswith=None, text_contains=None, text_endswith=None,
                               run_task=None, **kwargs):
        payload = self._gen_payload(locals(), exclude=['custom_filters'])
        return super().edited_message_handler(*custom_filters, **payload)

    def callback_query_handler(self, *custom_filters, text=None, regexp=None, button=None,
                               chat_type=None, state=None, storage=None,
                               user_id=None, chat_id=None,
                               text_startswith=None, text_contains=None, text_endswith=None,
                               run_task=None, **kwargs):
        payload = self._gen_payload(locals(), exclude=['custom_filters'])
        return super().callback_query_handler(*custom_filters, **payload)

    def inline_handler(self, *custom_filters, text=None, regexp=None, button=None,
                       state=None, storage=None, user_id=None, chat_id=None,
                       text_startswith=None, text_contains=None, text_endswith=None,
                       run_task=None, **kwargs):
        payload = self._gen_payload(locals(), exclude=['custom_filters'])
        return super().inline_handler(*custom_filters, **payload)

    async def process_update(self, update: types.Update):
        """
        Process single update object

        :param update:
        :return:
        """
        types.Update.set_current(update)

        try:
            if update.message:
                types.Message.set_current(update.message)
                types.User.set_current(update.message.from_user)
                types.Chat.set_current(update.message.chat)
                return await self.message_handlers.notify(update.message)
            if update.edited_message:
                types.Message.set_current(update.edited_message)
                types.User.set_current(update.edited_message.from_user)
                types.Chat.set_current(update.edited_message.chat)
                return await self.edited_message_handlers.notify(update.edited_message)
            if update.channel_post:
                types.Message.set_current(update.channel_post)
                types.Chat.set_current(update.channel_post.chat)
                return await self.channel_post_handlers.notify(update.channel_post)
            if update.edited_channel_post:
                types.Message.set_current(update.edited_channel_post)
                types.Chat.set_current(update.edited_channel_post.chat)
                return await self.edited_channel_post_handlers.notify(update.edited_channel_post)
            if update.inline_query:
                types.InlineQuery.set_current(update.inline_query)
                types.User.set_current(update.inline_query.from_user)
                return await self.inline_query_handlers.notify(update.inline_query)
            if update.chosen_inline_result:
                types.ChosenInlineResult.set_current(update.chosen_inline_result)
                types.User.set_current(update.chosen_inline_result.from_user)
                return await self.chosen_inline_result_handlers.notify(update.chosen_inline_result)
            if update.callback_query:
                types.CallbackQuery.set_current(update.callback_query)
                if update.callback_query.message:
                    types.Message.set_current(update.callback_query.message)
                    types.Chat.set_current(update.callback_query.message.chat)
                types.User.set_current(update.callback_query.from_user)
                return await self.callback_query_handlers.notify(update.callback_query)
            if update.shipping_query:
                types.ShippingQuery.set_current(update.shipping_query)
                types.User.set_current(update.shipping_query.from_user)
                return await self.shipping_query_handlers.notify(update.shipping_query)
            if update.pre_checkout_query:
                types.PreCheckoutQuery.set_current(update.pre_checkout_query)
                types.User.set_current(update.pre_checkout_query.from_user)
                return await self.pre_checkout_query_handlers.notify(update.pre_checkout_query)
            if update.poll:
                types.Poll.set_current(update.poll)
                return await self.poll_handlers.notify(update.poll)
            if update.poll_answer:
                types.PollAnswer.set_current(update.poll_answer)
                types.User.set_current(update.poll_answer.user)
                return await self.poll_answer_handlers.notify(update.poll_answer)
            if update.my_chat_member:
                types.ChatMemberUpdated.set_current(update.my_chat_member)
                types.User.set_current(update.my_chat_member.from_user)
                return await self.my_chat_member_handlers.notify(update.my_chat_member)
            if update.chat_member:
                types.ChatMemberUpdated.set_current(update.chat_member)
                types.User.set_current(update.chat_member.from_user)
                return await self.chat_member_handlers.notify(update.chat_member)
        except Exception as e:
            err = await self.errors_handlers.notify(update, e)
            if err:
                return err
            raise
