import redis
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from logs.logging_module import logger, generate_handler
from config.config import TELEGRAM_TOKEN, REDIS_PASSWORD, REDIS_HOST, REDIS_PORT

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

# Code for testing only
r.hset("85C9-176A-1000-TEST", mapping={"State": "Activated", "Message": "Test message"})
r.hset("85C9-176A-1001-TEST", mapping={"State": "Registered", "Message": "Test message"})
# Code for testing only

(
    AWAITING_CODE,
    CODE_CONFIRMED,
) = range(2)

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
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


def check_code_format(code: str) -> bool:
    if len(code) != 19:
        return True
    skeleton: tuple[str, str, str] = (code[4], code[9], code[14])
    for c in skeleton:
        if c != '-':
            return True
    return False


async def handle_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip().upper()
    chat_id = update.message.chat_id

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
        f"Если вы хотите отписаться от оповещений - напищите в чат 'erase'."
    )
    r.hset(user_code, "State", "Activated")
    r.hset(user_code, "Chat_id", str(chat_id))
    r.hset(str(chat_id), "User_code", user_code)
    r.sadd("Chat_ids", str(chat_id))
    logger.info(f"Correct code used: {user_code}")
    return CODE_CONFIRMED


async def handle_unauthorized_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip().upper()
    if message == "ERASE":
        chat_id = update.message.chat_id
        user_code = r.hget(str(chat_id), "User_code")
        await update.message.reply_text(
            f"Ваш чат удален из списка зарегистрированных, теперь вам не будут приходить оповещения о работе.\n"
            f"Если вы хотите вернуть оповещения - заново пройдите регистрацию с помощью команды '/start'."
        )
        r.delete(str(chat_id))
        r.delete(user_code)
        r.srem("Chat_ids", str(chat_id))
        logger.info(f"user_code: {user_code} from chat_id: {chat_id} successfully erased.")
        return AWAITING_CODE

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


async def check_redis_and_notify(context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_ids = r.smembers("Chat_ids")
        for chat_id in chat_ids:
            logger.info(f"Chat_id: {chat_id} found")
            user_code = r.hget(str(chat_id), "User_code")
            message = r.hget(user_code, "Message")
            if message != "":
                await context.bot.send_message(chat_id, message)
                logger.info(f"Message: {message} sent to {chat_id}.")
    except redis.RedisError as e:
        logger.error(f"Redis error in check_redis_and_notify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in check_redis_and_notify: {e}")


def main():
    logger.info("Started app")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_CODE: [MessageHandler(filters.TEXT, handle_code_input)],
            CODE_CONFIRMED: [MessageHandler(filters.TEXT, handle_unauthorized_reply)]
        },
        fallbacks=[CommandHandler('error', error)],
    )

    app.add_handler(conv_handler)

    job_queue = app.job_queue

    job_queue.run_repeating(
        callback=check_redis_and_notify,
        interval=10,
    )

    app.run_polling()


if __name__ == '__main__':
    main()
