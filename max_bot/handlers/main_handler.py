# Внешние зависимости
import logging
from maxapi import Router
from maxapi.types import BotStarted
from fastapi import HTTPException
# Внутренние модули
from max_bot.utils import redis_service


router = Router()


# Поиск участника
@router.bot_started()
async def bot_started(event: BotStarted):
    try:
        logging.info(event.payload)
        if event.payload:
            participant_data = await redis_service.get_participant(
                participant_id=event.payload.strip()
            )

            text_answer = (
                f"📝 Мероприятие: {participant_data['event_title']}\n\n"
                f"👤 Участник: {participant_data['full_name']}\n"
                f"ℹ️ Инфо: {participant_data['extra_info']}"
            )

        else:
            text_answer = "Ссылка не передана"

    except HTTPException:
        text_answer = "Участник не найден"

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        text_answer = "Ошибка"

    await event.bot.send_message(
        chat_id=event.chat_id,
        text=text_answer
    )