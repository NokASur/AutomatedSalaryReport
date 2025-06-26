import random

class Worker:
    def __init__(
            self,
            id: int,
            name: str | None = None,
            machine_type: str | None = None,
            commentary: str | None = None,
            work_type: str | None = None,
            mark1: int | None = None,
            mark2: int | None = None,
            run_count1: str | None = None,
            run_count2: str | None = None,
            hours_worked: int | None = None,
            hours_worked_sum: int | None = None,
            days_worked: int | None = None,
            salary_for_day: int | None = None,
            salary_for_month: int | None = None,
            repair_days_count: int | None = None,
            absence_reason: str | None = None,

    ):
        self.id = id
        self.name = name
        self.machine_type = machine_type
        self.commentary = commentary
        self.work_type = work_type
        self.mark1 = mark1
        self.mark2 = mark2
        self.run_count1 = run_count1
        self.run_count2 = run_count2
        self.hours_worked = hours_worked
        self.hours_worked_sum = hours_worked_sum
        self.days_worked = days_worked
        self.salary_for_day = salary_for_day
        self.salary_for_month = salary_for_month
        self.repair_days_count = repair_days_count
        self.absence_reason = absence_reason

    def generate_message(self, date: str) -> str:
        greetings = [
            f"Привет, {self.name}! Вот отчёт за {date}:\n",
            f"Здравствуйте, {self.name}! Статистика за {date}:\n",
            f"Добрый день, {self.name}! Ваша сводка за {date}:\n",
            f"{self.name}, приветствую! Информация за {date}:\n",
            f"Отчёт для {self.name} за {date}:\n"
        ]

        work_type_phrases = [
            f"Сегодня вы работали над: {self.work_type}.\n",
            f"В этот день вашими задачами были: {self.work_type}.\n",
            f"Вы занимались следующим: {self.work_type}.\n",
            f"Задачи на этот день: {self.work_type}.\n",
            f"Сегодняшняя работа включала: {self.work_type}.\n"
        ]

        daily_stats = [
            f"Отработано часов: {self.hours_worked}. Заработок: {self.salary_for_day} руб.\n",
            f"Сегодняшний результат: {self.hours_worked} часов = {self.salary_for_day} руб.\n",
            f"Вы трудились {self.hours_worked} ч. и заработали {self.salary_for_day} руб.\n",
            f"Итог дня: {self.hours_worked} ч. работы → {self.salary_for_day} руб.\n",
            f"За день вышло {self.hours_worked} рабочих часа, сумма: {self.salary_for_day} руб.\n"
        ]

        monthly_stats = [
            f"За месяц наработано: {self.hours_worked_sum} ч. ({self.salary_for_month} руб.)\n",
            f"Месячная статистика: {self.hours_worked_sum} часов, доход: {self.salary_for_month} руб.\n",
            f"Общее время за месяц: {self.hours_worked_sum} ч. Заработок: {self.salary_for_month} руб.\n",
            f"Наработка за месяц: {self.hours_worked_sum} часов → {self.salary_for_month} руб.\n",
            f"Итоги месяца: {self.hours_worked_sum} ч. = {self.salary_for_month} руб.\n"
        ]

        encouragements = [
            "Отличный результат!",
            "Так держать!",
            "Продолжайте в том же духе!",
            "Прекрасная работа!",
            "Вы молодец!",
            "Ваши усилия впечатляют!",
            "Это продуктивный день!",
            "Вот это эффективность!",
            "Замечательные показатели!",
            "Вы на верном пути!"
        ]

        message = random.choice(greetings)

        if self.work_type:
            message += random.choice(work_type_phrases)

        work_flag = False

        if self.hours_worked and self.salary_for_day:
            message += random.choice(daily_stats)
            work_flag = True

        if self.days_worked and self.hours_worked_sum:
            message += random.choice(monthly_stats)
            work_flag = True

        if work_flag:
            message += random.choice(encouragements)

        return message
