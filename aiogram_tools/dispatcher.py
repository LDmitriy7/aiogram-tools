from typing import TypeVar

from aiogram import Dispatcher as _Dispatcher, executor

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

    def run_webhook(self, webhook_path, *, loop=None, skip_updates=None,
                    on_startup=None, on_shutdown=None, check_ip=False, retry_after=None,
                    route_name=executor.DEFAULT_ROUTE_NAME,
                    **kwargs):
        payload = self._gen_payload(locals())
        executor.start_webhook(self, **payload)

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
