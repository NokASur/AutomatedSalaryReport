import redis
import os
import logging

from telegram import Update
from telegram.ext import ContextTypes
from logs.logging_module import logger, generate_handler
from config.config import REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, ADMIN_CODES, TEST_CODE
from telegram_bot.lib.helpers import *

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

r.delete("Chat_ids")

r.hset(TEST_CODE, mapping={"State": "Registered", "Message": "Test message"})

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_path, exist_ok=True)

logger.addHandler(generate_handler(os.path.join(log_path, "telegram_bot_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "telegram_bot_error.log"), logging.ERROR))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Здравствуйте {user.name}! Введите свой уникальный код для регистрации.\n"
        f"Пример кода: XXXX-XXXX-XXXX-XXXX"
    )
    logger.info(f"Chat initiated with user: {user}")
    context.user_data["state"] = AWAITING_CODE
    return context.user_data["state"]


async def handle_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip().upper()
    chat_id = update.message.chat_id

    if user_code in ADMIN_CODES:
        r.sadd("ADMIN_CHAT_IDS", chat_id)
        await update.message.reply_text(f"Админ зарегистрирован.")
        context.user_data["state"] = CODE_CONFIRMED
        return context.user_data["state"]

    if check_code_format(user_code):
        await update.message.reply_text(
            f"Неверный формат кода, должно быть ровно 16 уникальных символов с разделительными тире.\n"
            f"Корректный формат: 'XXXX-XXXX-XXXX-XXXX'."
        )
        logger.info(f"Incorrect code format: {user_code}")

        context.user_data["state"] = AWAITING_CODE
        return context.user_data["state"]

    if not r.exists(user_code):
        await update.message.reply_text(
            f"Данный код не зарегистрирован за рабочим.\n"
            f"Попробуйте заново когда работодатель отправит хотя бы один отчет с вашим кодом."
        )
        logger.info(f"Unauthorized code attempt: {user_code}")

        context.user_data["state"] = AWAITING_CODE
        return context.user_data["state"]

    await update.message.reply_text(
        f"Код подтвержден.\n"
        f"Теперь сюда будут периодически приходить краткие отчеты по вашей работе."
    )
    r.hset(user_code, "State", "Activated")
    r.hset(user_code, "Chat_id", str(chat_id))
    r.hset(str(chat_id), "User_code", user_code)
    r.sadd("Chat_ids", str(chat_id))
    logger.info(f"Correct code used: {user_code}")

    context.user_data["state"] = CODE_CONFIRMED
    return context.user_data["state"]


async def handle_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    calling_state = context.user_data.get("state")
    await update.message.reply_text(
        f"На данный момент бот просто присылает информацию по мере её поступления на сервер.\n"
        f"В будущем будет возможно задавать вопросы через бота. Сейчас же предлагаю просто отдохнуть :В"
    )
    context.user_data["state"] = calling_state
    return context.user_data["state"]


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Что-то явно пошло не так, попробуйте отправить обычное текстовое сообщение.\n"
        f"Если ситуация повторится, сообщи работодателю. Будет отлично, если ты приложишь скриншоты чата.\n"
        f"Так будет проще отследить причины ошибки. Спасибо!"
    )
    logger.error("Something went wrong after user message")
    context.user_data["state"] = AWAITING_CODE
    return context.user_data["state"]


async def quit_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы покинули панель управления.")
    context.user_data["state"] = CODE_CONFIRMED
    return context.user_data["state"]


async def discard_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = r.smembers("Chat_ids")
    for chat_id in chat_ids:
        logger.info(f"Chat_id: {chat_id} found")
        user_code = r.hget(str(chat_id), "User_code")
        r.hset(user_code, "Message", "")
    await update.message.reply_text("Все сгенерированные сообщения успешно удалены.")


async def erase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state", None) == AWAITING_CODE:
        await update.message.reply_text(
            f"Вы еще не зарегистрированы.\n"
            f"Команда /erase нужна для случаев, когда вы хотите перестать получить уведомления через бота"
        )
        context.user_data["state"] = AWAITING_CODE
        return context.user_data["state"]

    chat_id = update.message.chat_id
    user_code = r.hget(str(chat_id), "User_code")
    await update.message.reply_text(
        f"Ваш чат удален из списка зарегистрированных, теперь вам не будут приходить оповещения о работе."
    )
    r.delete(str(chat_id))
    r.hset(user_code, "State", "Registered")
    r.srem("Chat_ids", str(chat_id))
    logger.info(f"user_code: {user_code} from chat_id: {chat_id} successfully erased.")
    context.user_data["state"] = AWAITING_CODE
    return context.user_data["state"]


async def enter_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    admin_chat_ids = r.smembers("ADMIN_CHAT_IDS")
    if str(chat_id) not in admin_chat_ids:
        await update.message.reply_text("Вы не являетесь админом.")
        logger.error(f'Failed admin panel authorization. Chat id: {chat_id} not in admin chat ids: {admin_chat_ids}')
        return CODE_CONFIRMED
    await update.message.reply_text("Вы успешно вошли в панель управления.")
    logger.info(f'Admin panel entered from chat_id: {chat_id}')
    context.user_data["state"] = ADMIN_PANEL
    return context.user_data["state"]


async def check_redis_and_notify(context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_ids = r.smembers("Chat_ids")
        for chat_id in chat_ids:
            logger.info(f"Chat_id: {chat_id} found")
            user_code = r.hget(str(chat_id), "User_code")
            message = r.hget(user_code, "Message")
            r.hset(user_code, "Message", "")
            # await context.bot.send_message(chat_id, message)
            # logger.info(f"Message: {message} sent to {chat_id}.")
            if message != "":
                await context.bot.send_message(chat_id, message)
                logger.info(f"Message: {message} sent to {chat_id}.")
    except redis.RedisError as e:
        logger.error(f"Redis error in check_redis_and_notify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in check_redis_and_notify: {e}")


async def confirm_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_redis_and_notify(context)
    await update.message.reply_text("Текущая серия сообщений успешно подтверждена.")
    context.user_data["state"] = ADMIN_PANEL
    return context.user_data["state"]


async def display_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_count = 0
    full_message = []
    try:
        current_full_message_part = ""
        chat_ids = r.smembers("Chat_ids")
        logger.info(chat_ids)
        for chat_id in chat_ids:
            logger.info(f"Chat_id: {chat_id} found")
            user_code = r.hget(str(chat_id), "User_code")
            logger.info(f"User code: {user_code} found")
            message = r.hget(user_code, "Message")
            logger.info(f"Message: {message} found")
            if message:
                message_count += 1
                current_full_message_part += f"Сообщение {message_count}\n{message}\n\n"
                logger.info(f"FMessage: {current_full_message_part}")
                if message_count % 5 == 0:
                    current_full_message_part = ""

        await update.message.reply_text(f"Новых сообщений: {message_count}")
        for message_part in full_message:
            await update.message.reply_text(message_part)

        context.user_data["state"] = ADMIN_PANEL
        return context.user_data["state"]

    except redis.RedisError as e:
        logger.error(f"Redis error in check_redis_and_notify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in check_redis_and_notify: {e}")


async def help_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Help request from {context.user_data["state"]}.\n'
                f'Covered states: {HELP_MESSAGES}.\n'
                f'Reply: Ваш текущий статус диалога: {HELP_MESSAGES[context.user_data["state"]][0]}\n'
                f"Доступные команды:\n{HELP_MESSAGES[context.user_data['state']][1]}")
    await update.message.reply_text(f"Ваш текущий статус диалога: {HELP_MESSAGES[context.user_data['state']][0]}\n"
                                    f"Доступные команды:\n{HELP_MESSAGES[context.user_data['state']][1]}")
    return context.user_data["state"]
