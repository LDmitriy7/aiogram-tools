from aiogram import Dispatcher as _Dispatcher
from aiogram.utils.payload import generate_payload

from aiogram_tools.filters import CallbackQueryButton, InlineQueryButton, MessageButton
from aiogram_tools.filters import StorageDataFilter


class Dispatcher(_Dispatcher):

    @staticmethod
    def _gen_payload(_locals: dict):
        kwargs = _locals.pop('kwargs', {})
        payload = generate_payload(['__class__', 'custom_filters', 'kwargs'], **_locals, **kwargs)
        return payload

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

    def message_handler(self, *custom_filters, text=None, commands=None, regexp=None, button=None,
                        content_types=None, chat_type=None, state=None, storage=None,
                        is_reply=None, is_forwarded=None, user_id=None, chat_id=None,
                        text_startswith=None, text_contains=None, text_endswith=None,
                        run_task=None, **kwargs):
        return super().message_handler(*custom_filters, **self._gen_payload(locals()))

    def edited_message_handler(self, *custom_filters, text=None, commands=None, regexp=None, button=None,
                               content_types=None, chat_type=None, state=None, storage=None,
                               is_reply=None, is_forwarded=None, user_id=None, chat_id=None,
                               text_startswith=None, text_contains=None, text_endswith=None,
                               run_task=None, **kwargs):
        return super().edited_message_handler(*custom_filters, **self._gen_payload(locals()))

    def callback_query_handler(self, *custom_filters, text=None, regexp=None, button=None,
                               chat_type=None, state=None, storage=None,
                               user_id=None, chat_id=None,
                               text_startswith=None, text_contains=None, text_endswith=None,
                               run_task=None, **kwargs):
        return super().callback_query_handler(*custom_filters, **self._gen_payload(locals()))

    def inline_handler(self, *custom_filters, text=None, regexp=None, button=None,
                       state=None, storage=None, user_id=None, chat_id=None,
                       text_startswith=None, text_contains=None, text_endswith=None,
                       run_task=None, **kwargs):
        return super().inline_handler(*custom_filters, **self._gen_payload(locals()))
