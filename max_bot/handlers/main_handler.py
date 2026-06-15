# Внешние зависимости
import logging
from maxapi import Router, F
from maxapi.types import BotStarted, MessageCreated, MessageCallback, InputMediaBuffer
from maxapi.enums.upload_type import UploadType
from maxapi.context import StatesGroup, State, MemoryContext
from fastapi import HTTPException
# Внутренние модули
from max_bot.utils import redis_service, normalize_phone, generate_qr_bytes
from max_bot.core import cfg
from max_bot.keyboards import create_main_keyboard, create_events_inline


router = Router()


class SelectEvent(StatesGroup):
    current_event = State()


@router.bot_started()
async def bot_started(event: BotStarted, context: MemoryContext):
    await context.clear()

    attachments = []

    try:
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
            text_answer = (
                "👋 Добро пожаловать в бот верификации участников!\n\n"
                "Здесь вы можете получить QR-код для прохода на мероприятие.\n\n"
                "1️⃣ Нажмите «Мероприятия 🎟» и выберите своё мероприятие\n"
                "2️⃣ Отправьте номер телефона, на который вы зарегистрированы\n\n"
                "Если вы есть в списке участников — я пришлю вам QR-код для прохода 🎫"
            )
            attachments.append(create_main_keyboard())

    except HTTPException:
        text_answer = "Участник не найден"

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        text_answer = "Ошибка"

    await event.bot.send_message(
        chat_id=event.chat_id,
        text=text_answer,
        attachments=attachments
    )


# Список всех мероприятий
@router.message_created(F.message.body.text.lower() == "мероприятия")
async def get_events_command(event: MessageCreated, context: MemoryContext):
    await context.clear()

    events = await redis_service.get_all_events()

    if not events:
        await event.message.answer(text="Сейчас нет доступных мероприятий")
        return

    await event.message.answer(
        text="Выберите мероприятие из списка ниже 👇:",
        attachments=[create_events_inline(events)]
    )


# Выбор мероприятия
@router.message_callback(F.callback.payload.startswith("e:"))
async def select_event_callback_run(event: MessageCallback, context: MemoryContext):
    event_id = event.callback.payload.replace("e:", "")

    events = await redis_service.get_all_events()
    event_title = next(
        (e["event_title"] for e in events if e["event_id"] == event_id),
        "-"
    )

    await context.update_data(event_id=event_id)
    await context.set_state(SelectEvent.current_event)

    await event.message.answer(
        text=(
            f"Вы выбрали мероприятие: {event_title}\n\n"
            "Напишите номер телефона в формате: +7 (999) 123-45-67"
        )
    )


# Поиск участника по номеру телефона
@router.message_created(SelectEvent.current_event, F.message.body)
async def participant_by_phone_command(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()
    event_id = data.get("event_id")

    if event_id is None:
        return

    # 1. проверка формата
    phone = normalize_phone(event.message.body.text)

    if phone is None:
        await event.message.answer(
            text=(
                "❌ Неверный формат номера.\n\n"
                "Отправьте номер из 11 цифр, например: +7 (999) 123-45-67"
            )
        )
        return  # остаёмся в состоянии, ждём корректный ввод

    # 2. поиск участника
    try:
        participant = await redis_service.get_participant_by_phone(
            event_id=event_id,
            phone=phone
        )

    except HTTPException:
        await event.message.answer(
            text=(
                "😔 Вы не найдены в списке участников этого мероприятия.\n\n"
                "Проверьте номер и попробуйте снова, либо обратитесь к организатору."
            )
        )
        return

    except Exception as e:
        logging.error(f"Unexpected error (phone lookup): {e}")
        await event.message.answer(text="Произошла ошибка, попробуйте позже")
        return

    # 3. найден — формируем и отправляем QR
    qr_link = (
        f"https://max.ru/{cfg.USERNAME_MAX_BOT}"
        f"?start={participant['participant_id']}"
    )
    qr_bytes = generate_qr_bytes(qr_link)

    caption = (
        f"✅ Вы в списке участников!\n\n"
        f"📝 Мероприятие: {participant['event_title']}\n"
        f"👤 {participant['full_name']}\n\n"
        f"🎫 Покажите этот QR-код на входе."
    )

    await context.clear()

    media = InputMediaBuffer(
        buffer=qr_bytes,
        filename="qr.png",
        type=UploadType.IMAGE
    )

    await event.message.answer(text=caption, attachments=[media])