# Внешние зависимости
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import MessageButton


# Создаем кнопки меню
def create_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(MessageButton(text="Мероприятия"))

    return builder.as_markup()