import random


class Worker:
    def __init__(
            self,
            unique_id: str | None = None,
            name: str | None = None,
            machine_type: str | None = None,
            commentary: str | None = None,
            work_type: list[str] | None = None,
            mark: list[str] | None = None,
            run_count: list[str] | None = None,
            hours_worked: list[str] | None = None,
            hours_worked_sum: int | None = None,
            days_worked: int | None = None,
            salary_for_day: list[str] | None = None,
            salary_for_month: int | None = None,
            repair_days_count: int | None = None,
            absence_reason: str | None = None,

    ):
        self.unique_id = unique_id
        self.name = name
        self.machine_type = machine_type
        self.commentary = commentary
        self.work_type = work_type
        self.mark = mark
        self.run_count = run_count
        self.hours_worked = hours_worked
        self.hours_worked_sum = hours_worked_sum
        self.days_worked = days_worked
        self.salary_for_day = salary_for_day
        self.salary_for_month = salary_for_month
        self.repair_days_count = repair_days_count
        self.absence_reason = absence_reason

    def generate_message(self, date: str) -> str:
        if self.absence_reason:
            return f"Сегодня вы не работали по причине: {self.absence_reason}."

        greetings = [
            f"Привет, {self.name}! Вот отчёт за {date}:\n",
            f"Здравствуйте, {self.name}! Статистика за {date}:\n",
            f"Добрый день, {self.name}! Ваша сводка за {date}:\n",
            f"{self.name}, приветствую! Информация за {date}:\n",
            f"Отчёт для {self.name} за {date}:\n"
        ]

        work_type_phrases = [
            f"Сегодня вы работали над следующими задачами: {', '.join(self.work_type)}.\n",
            f"В этот день вы занимались: {', '.join(self.work_type)}.\n",
            f"Ваши задачи на сегодня: {', '.join(self.work_type)}.\n",
            f"Сегодняшняя работа включала: {', '.join(self.work_type)}.\n",
            f"Вы работали над: {', '.join(self.work_type)}.\n"
        ]

        daily_stats = [
            f"Отработано: {', '.join([f'{h} ч. ({s} руб.)' for h, s in zip(self.hours_worked, self.salary_for_day)])}.\n",
            f"Результат дня: {', '.join([f'{h} ч. = {s} руб.' for h, s in zip(self.hours_worked, self.salary_for_day)])}.\n",
            f"Вы трудились: {', '.join([f'{h} ч. ({s} руб.)' for h, s in zip(self.hours_worked, self.salary_for_day)])}.\n",
            f"Итог дня: {', '.join([f'{h} ч. → {s} руб.' for h, s in zip(self.hours_worked, self.salary_for_day)])}.\n",
            f"За день: {', '.join([f'{h} ч. ({s} руб.)' for h, s in zip(self.hours_worked, self.salary_for_day)])}.\n"
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
        work_flag = False

        if any(wt for wt in self.work_type):
            message += random.choice(work_type_phrases)
            work_flag = True

        if any(h and s for h, s in zip(self.hours_worked, self.salary_for_day)):
            message += random.choice(daily_stats)
            work_flag = True

        if self.days_worked and self.hours_worked_sum:
            message += random.choice(monthly_stats)
            work_flag = True

        if work_flag:
            message += random.choice(encouragements)

        return message

    def merge_workers(self, worker):
        self.work_type.extend(worker.work_type)
        self.mark.extend(worker.mark)
        self.run_count.extend(worker.run_count)
        self.salary_for_day.extend(worker.salary_for_day)
        self.hours_worked.extend(worker.hours_worked)
