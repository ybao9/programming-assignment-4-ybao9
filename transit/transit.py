from __future__ import annotations
import csv


class Stop:
    def __init__(self, stop_id: str, name: str):
        self.stop_id = stop_id
        self.name = name

    def __repr__(self) -> str:
        return f"{self.stop_id}: {self.name}"

class Route:
    def __init__(self, data: dict):
        # self.stops should be a list[Stop] in route order
        self.route_id = data["route_id"]
        self.route_name = data["route_name"]

        self.stops = []
        for item in data["stops"].split(">"):
            stop_id, name = item.split(":", 1)
            self.stops.append(Stop(stop_id, name))

        self.travel_times = [int(x) for x in data["travel_times"].split(",")]

    def serves(self, stop_id: str) -> bool:
        for stop in self.stops:
            if stop.stop_id == stop_id:
                return True
        return False

    def travel_time(self, stop_a: str, stop_b: str) -> int | None:
        a = None
        b = None

        for i, stop in enumerate(self.stops):
            if stop.stop_id == stop_a:
                a = i
            if stop.stop_id == stop_b:
                b = i

        if a is None or b is None:
            return None

        if a == b:
            return 0

        return sum(self.travel_times[min(a, b):max(a, b)])


class TransitSchedule:
    def __init__(self, filename: str):
        self.routes = []
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.routes.append(Route(row))

    def search_by_stop(self, stop_id: str) -> list[Route]:
        result = []
        for route in self.routes:
            if route.serves(stop_id):
                result.append(route)
        return result

    def fastest_route(self, stop_a: str, stop_b: str) -> list[Route]:
        list = []
        for route in self.routes:
            t = route.travel_time(stop_a, stop_b)
            if t is not None:
                list.append((t, route.route_id, route))

        list.sort(key=lambda x: (x[0], x[1]))
        return [item[2] for item in list]
