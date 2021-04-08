import inspect

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware


class EmptyAnswerCallbackQuery(BaseMiddleware):
    """Отвечает пустым сообщением на любой CallbackQuery, чтобы убрать анимацию загрузки"""

    @staticmethod
    async def on_post_process_callback_query(query: types.CallbackQuery, *_):
        await query.answer()


class AnswerFromReturn(BaseMiddleware):
    """Отправляет сообщением возращенные из хендлера тексты / выполняет корутины"""

    @staticmethod
    def unfold_results(results: list):
        for item in results:
            if isinstance(item, tuple):
                yield from item
            else:
                yield item

    async def on_post_process_message(self, msg: types.Message, results: list, *_):
        for item in self.unfold_results(results):
            if isinstance(item, str):
                await msg.answer(item)
            elif inspect.iscoroutine(item):
                await item

    async def on_post_process_callback_query(self, query: types.CallbackQuery, results: list, *_):
        for item in self.unfold_results(results):
            if isinstance(item, str):
                await query.message.answer(item)
            elif inspect.iscoroutine(item):
                await item
