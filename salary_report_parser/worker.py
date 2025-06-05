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
        message = f"Здравствуйте, {self.name}! Держите подробную информацию по вашему рабочему дню за {date}!:\n"
        work_flag = False
        if self.work_type:
            message += f"В этот день вы занимались следующей/ими задачей/ами: {self.work_type}.\n"
        if self.hours_worked and self.hours_worked_sum:
            message += "Вы отработали {self.hours_worked} часов и заработали {self.salary_for_day} рублей!\n"
            work_flag = True
        if self.days_worked and self.hours_worked_sum:
            message += f"За последний месяц было наработано {self.hours_worked_sum} часов и заработано{self.salary_for_month} рублей.\n"
            work_flag = True
        if work_flag:
            message += f"Отличная работа!"
        return message
