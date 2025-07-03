from callbacks import *


async def check_redis_and_notify_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_count = 0
    full_message = ""
    try:
        admin_chat_ids = r.smembers("ADMIN_CHATS")
        chat_ids = r.smembers("Chat_ids")
        for chat_id in chat_ids:
            logger.info(f"Chat_id: {chat_id} found")
            user_code = r.hget(str(chat_id), "User_code")
            message = r.hget(user_code, "Message")
            r.hset(user_code, "Message", "")
            if message != "":
                message_count += 1
                full_message += f"Сообщение {message_count}\n{message}\n\n"
                # await context.bot.send_message(chat_id, message)
                # logger.info(f"Message: {message} sent to {chat_id}.")
        for admin_chat_id in admin_chat_ids:
            await context.bot.send_message(admin_chat_id, "Новый список сообщений:")
            await context.bot.send_message(admin_chat_id, full_message)
            await context.bot.send_message(admin_chat_id,
                                           "Для того чтобы подтвердить корректность сгенерированных сообщений, введите команду '/confirm'\n"
                                           "Для удаления сообщений - '/discard'")

    except redis.RedisError as e:
        logger.error(f"Redis error in check_redis_and_notify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in check_redis_and_notify: {e}")
