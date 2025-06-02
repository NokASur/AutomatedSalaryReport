class Worker:
    def __init__(self, id: int, name: str, ):
        self.id = id
        self.name = name

    def generate_message(self) -> str:
        return f"Test + {self.name}"


# A slobby amoeba
def parse_excel_report(path: str) -> list[Worker]:
    worker = Worker(id=1, name="Name")
    worker2 = Worker(id=2, name="Kekw")
    return [worker, worker2]
