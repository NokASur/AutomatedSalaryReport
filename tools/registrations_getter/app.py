import logging
import os
from logs.logging_module import logger, generate_handler
import redis
from config.config import REDIS_PASSWORD, REDIS_PORT, HOST

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_path, exist_ok=True)
logger.addHandler(generate_handler(os.path.join(log_path, "report_sender_all.log"), logging.DEBUG))
logger.addHandler(generate_handler(os.path.join(log_path, "report_sender_error.log"), logging.ERROR))
logger.setLevel(logging.DEBUG)
logger.info(f"Logger enabled")

r = redis.Redis(
    host=HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0,
    decode_responses=True
)

with open('Registrations.txt', 'w') as f:
    try:
        chat_ids = r.smembers("Chat_ids")
        count = 0
        codes = ''
        for chat_id in chat_ids:
            user_code = r.hget(str(chat_id), "User_code")
            logger.info(f"User code found: {user_code}")
            count += 1
            codes += user_code + '\n'

        f.write(f'Registered workers count: {count}\n'
                f'Codes list:\n'
                f'{codes}')
    except Exception as e:
        logger.error(f"Error occurred: {e}")
