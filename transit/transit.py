class Stop:
    def __init__(self, stop_id: str, name: str):
        pass

    def __repr__(self) -> str:
        pass


class Route:
    def __init__(self, data: dict):
        # self.stops should be a list[Stop] in route order
        pass

    def serves(self, stop_id: str) -> bool:
        pass

    def travel_time(self, stop_a: str, stop_b: str) -> int | None:
        pass


class TransitSchedule:
    def __init__(self, filename: str):
        pass

    def search_by_stop(self, stop_id: str) -> list[Route]:
        pass

    def fastest_route(self, stop_a: str, stop_b: str) -> list[Route]:
        pass