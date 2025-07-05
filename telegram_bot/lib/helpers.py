(
    AWAITING_CODE,
    CODE_CONFIRMED,
    ADMIN_PANEL,
) = range(3)

START_COMMANDS = ['start', 's']
ERASE_COMMANDS = ['erase', 'e']
ADMIN_COMMANDS = ['admin', 'a']
DISPLAY_COMMANDS = ['display_messages', 'd', 'show']
CONFIRM_COMMANDS = ['confirm', 'c']
DISCARD_COMMANDS = ['discard', 'd']
QUIT_COMMANDS = ['quit', 'q']
HELP_COMMANDS = ['help', 'h']

HELP_MESSAGES: dict[int:(str, str)] = {
    AWAITING_CODE: (
        "Ожидание ввода кода работника.",
        "'/start', '/s' - начало работы с ботом.\n"
        "'/help', '/h' - вывести все доступные команды.\n"
        "'XXXX-XXXX-XXXX-XXXX' - формат кода сотрудника."
    ),
    CODE_CONFIRMED: (
        "Подтвержден код работника.",
        "'/erase', '/e' - сброс диалога с ботом.\n"
        "'/help', '/h' - вывести все доступные команды.\n"
        "'/admin', '/a' - перейти в панель управления."
    ),
    ADMIN_PANEL: (
        "Панель управления.",
        "'/erase', '/e' - сброс диалога с ботом.\n"
        "'/help', '/h' - вывести все доступные команды.\n"
        "'/display_messages', '/d', '/show' - вывести список сгенерированных сообщений.\n"
        "'/confirm', '/c' - отправить все сообщения работникам.\n"
        "'/discard', '/d' - удалить все сообщения.\n"
        "'/quit', '/q' - выйти из панели управления."
    ),
}


def check_code_format(code: str) -> bool:
    if len(code) != 19:
        return True
    skeleton: tuple[str, str, str] = (code[4], code[9], code[14])
    for c in skeleton:
        if c != '-':
            return True
    return False
