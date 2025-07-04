import redis
import os
import logging

from telegram import Update
from telegram.ext import ContextTypes
from logs.logging_module import logger, generate_handler
from config.config import REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, ADMIN_CODES, TEST_CODE
from telegram_bot.lib.helpers import check_code_format

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

(
    AWAITING_CODE,
    CODE_CONFIRMED,
    ADMIN,
) = range(3)

# Testing only
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
        f"Привет {user.name}! Введи свой уникальный код для регистрации.\n"
        f"Пример кода: XXXX-XXXX-XXXX-XXXX"
    )
    logger.info(f"Chat initiated with user: {user}")
    return AWAITING_CODE


async def handle_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip().upper()
    chat_id = update.message.chat_id

    if user_code in ADMIN_CODES:
        r.sadd("ADMIN_CHATS", chat_id)
        await update.message.reply_text(f"Админ зарегистрирован")
        return ADMIN

    if check_code_format(user_code):
        await update.message.reply_text(
            f"Неверный формат кода, должно быть ровно 16 уникальных символов с разделительными тире.\n"
            f"Корректный формат: 'XXXX-XXXX-XXXX-XXXX'."
        )
        logger.info(f"Incorrect code format: {user_code}")
        return AWAITING_CODE

    if not r.exists(user_code):
        await update.message.reply_text(
            f"Данный код не зарегистрирован за рабочим.\n"
            f"Попробуйте заново после того, как работодатель отправит хотя бы один отчет с вашим кодом в систему."
        )
        logger.info(f"Unauthorized code attempt: {user_code}")
        return AWAITING_CODE
    await update.message.reply_text(
        f"Код подтвержден.\n"
        f"Теперь сюда будут периодически приходить краткие отчеты по вашей работе.\n"
        f"Если вы хотите отписаться от оповещений - используйте команду '/erase'."
    )
    r.hset(user_code, "State", "Activated")
    r.hset(user_code, "Chat_id", str(chat_id))
    r.hset(str(chat_id), "User_code", user_code)
    r.sadd("Chat_ids", str(chat_id))
    logger.info(f"Correct code used: {user_code}")
    return CODE_CONFIRMED


async def handle_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"На данный момент бот просто присылает информацию по мере её поступления на сервер.\n"
        f"В будущем будет возможно задавать вопросы через бота. Сейчас же предлагаю просто отдохнуть :В"
    )
    return CODE_CONFIRMED


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Что-то явно пошло не так, попробуй отправить обычное текстовое сообщение.\n"
        f"Если ситуация повторится, сообщи работодателю. Будет круто, если ты приложишь скриншоты чата.\n"
        f"Так будет проще отследить причины ошибки. Спасибо!"
    )
    logger.error("Something went wrong after user message")


async def quit_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вы покинули панель управления."
                                    "\n Используйте '/admin' или '/a' чтобы вернуться.")
    return CODE_CONFIRMED


async def discard_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_ids = r.smembers("Chat_ids")
    for chat_id in chat_ids:
        logger.info(f"Chat_id: {chat_id} found")
        user_code = r.hget(str(chat_id), "User_code")
        r.hset(user_code, "Message", "")
    await update.message.reply_text("Все сгенерированные сообщения успешно удалены.\n"
                                    "Чтобы покинуть панель управления - воспользуйтесь '/quit' или '/q'.")


async def erase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("current_state", None) == AWAITING_CODE:
        await update.message.reply_text(
            f"Вы еще не зарегистрированы."f" Команда /erase нужна для случаев, "
            f"когда вы хотите перестать получить уведомления через бота"
        )
        return AWAITING_CODE

    chat_id = update.message.chat_id
    user_code = r.hget(str(chat_id), "User_code")
    await update.message.reply_text(
        f"Ваш чат удален из списка зарегистрированных, теперь вам не будут приходить оповещения о работе.\n"
        f"Если вы хотите вернуть оповещения - заново пройдите регистрацию с помощью команды '/start'."
    )
    r.delete(str(chat_id))
    r.hset(user_code, "State", "Registered")
    r.srem("Chat_ids", str(chat_id))
    logger.info(f"user_code: {user_code} from chat_id: {chat_id} successfully erased.")
    return AWAITING_CODE


async def enter_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_code = r.hget(str(chat_id), "User_code")
    if user_code not in ADMIN_CODES:
        await update.message.reply_text("Вы не являетесь админом.")
        logger.info(f'Failed admin panel authorization. Code {user_code} not in {ADMIN_CODES}')
        return CODE_CONFIRMED
    await update.message.reply_text("Вы успешно вошли в панель управления.\n"
                                    "Используйте '/quit' или '/q' для выхода из панели управления.")
    logger.info(f'Admin panel entered from chat_id: {chat_id}')
    return ADMIN


async def check_redis_and_notify(context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_ids = r.smembers("Chat_ids")
        for chat_id in chat_ids:
            logger.info(f"Chat_id: {chat_id} found")
            user_code = r.hget(str(chat_id), "User_code")
            message = r.hget(user_code, "Message")
            r.hset(user_code, "Message", "")
            if message != "":
                await context.bot.send_message(chat_id, message)
                logger.info(f"Message: {message} sent to {chat_id}.")
    except redis.RedisError as e:
        logger.error(f"Redis error in check_redis_and_notify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in check_redis_and_notify: {e}")


async def confirm_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_redis_and_notify(context)
    await update.message.reply_text("Текущая серия сообщений успешно подтверждена.\n"
                                    "Используйте '/quit' или '/q' для выхода из панели управления.")
    return ADMIN
