# Внешние зависимости
from typing import List, Dict
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton


# Создаем инлайн кнопки выбора мероприятий
def create_events_inline(events: List[Dict[str, str]]):
    builder = InlineKeyboardBuilder()

    for event in events:
        builder.row(CallbackButton(
            text=event["event_title"],
            payload=f"e:{event['event_id']}")
        )

    return builder.as_markup()