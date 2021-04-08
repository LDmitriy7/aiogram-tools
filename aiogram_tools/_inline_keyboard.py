from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.helper import Item, Helper


class InlineKeyboard(InlineKeyboardMarkup, Helper):
    DATA_ROWS: list[Item, tuple[Item]] = []

    def __init__(self, cdata_and_text: dict[str, str] = None, row_width=2):
        """Buttons in format: {callback_data:text} for DATA_ROWS."""
        super().__init__(row_width)

        if cdata_and_text:
            buttons = {cdata.upper(): text for cdata, text in cdata_and_text.items() if text}
        else:
            buttons = {}

        for data_row in self.data_rows:
            btn_row = self.make_buttons_row(data_row, buttons)
            self.row(*btn_row)

    @property
    def data_rows(self) -> list[list[str]]:
        return [self._to_values_list(row) for row in self.DATA_ROWS]

    def make_buttons_row(self, data_row: list[str], buttons: dict) -> list[InlineKeyboardButton]:
        return [self._make_data_button(cdata, buttons) for cdata in data_row if cdata in buttons]

    @staticmethod
    def _to_values_list(data_row: str or tuple[str]) -> list[str]:
        if not isinstance(data_row, tuple):
            data_row = (data_row,)
        return [button.value for button in data_row]

    @staticmethod
    def _make_data_button(data: str, _locals: dict) -> InlineKeyboardButton:
        return InlineKeyboardButton(_locals[data], callback_data=data)
