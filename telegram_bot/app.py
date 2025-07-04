from telegram_bot.lib.callbacks import *
from telegram_bot.lib.jobs import check_redis_and_notify_admins
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config.config import TELEGRAM_TOKEN

START_COMMANDS = ['start', 's']
ERASE_COMMANDS = ['erase', 'e']
ADMIN_COMMANDS = ['admin', 'a']
CONFIRM_COMMANDS = ['confirm', 'c']
DISCARD_COMMANDS = ['discard', 'd']
QUIT_COMMANDS = ['quit', 'q']


def main():
    logger.info("Started app")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_CODE: [
                CommandHandler(START_COMMANDS, start),
                MessageHandler(filters.TEXT, handle_code_input)
            ],
            CODE_CONFIRMED: [
                CommandHandler(ERASE_COMMANDS, erase),
                CommandHandler(ADMIN_COMMANDS, enter_admin),
                MessageHandler(filters.TEXT, handle_replies)
            ],
            ADMIN: [
                CommandHandler(ERASE_COMMANDS, erase),
                CommandHandler(CONFIRM_COMMANDS, confirm_messages),
                CommandHandler(DISCARD_COMMANDS, discard_messages),
                CommandHandler(QUIT_COMMANDS, quit_admin),
                MessageHandler(filters.TEXT, handle_replies)
            ]
        },
        fallbacks=[CommandHandler('error', error)],
    )

    app.add_handler(conv_handler)

    job_queue = app.job_queue

    job_queue.run_repeating(
        callback=check_redis_and_notify_admins,
        interval=10,
    )

    app.run_polling()


if __name__ == '__main__':
    main()
