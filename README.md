[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/lKS_OqLu)
# Programming Assignment 4

## Goals

This assignment will give you practice with object-oriented programming concepts including class design, composition, and constructing an application by loading structured data from a file into interacting objects.

## Transit Schedule

In this part, you will model a bus transit schedule using three classes:

- `Stop`: represents a single bus stop
- `Route`: represents a route with an ordered list of stops and travel times between them
- `TransitSchedule`: reads route data from a CSV file and supports search operations

*Be extra mindful of code reuse*. Create helper functions and methods as needed.

### Input File Format

You will be given a CSV file with the following header:

```
route_id,route_name,stops,travel_times
```

- Each row describes a route.
- `route_id` is a string (e.g., "55")
- `route_name` is a string (e.g., "Garfield Bus")
- `stops` is a `>`-separated list of stops in route order
- Each stop is encoded as STOP_ID:STOP_NAME.
  - Example: `S1:Garfield Blvd>S2:Halsted St>S3:State St>S4:Midway`
- `travel_times` is a comma-separated list of integers, describing the minutes between consecutive stops.
  - Example: `5,7,6`

The following rule will always hold:
```
len(travel_times) == len(stops) - 1
```

**Important:** The provided file will be valid CSV. Fields containing commas (e.g., `travel_times`) will be quoted. Example row:
```
55,Garfield Bus,"S1:Garfield Blvd>S2:Halsted St>S3:State St>S4:Midway","5,7,6" 
```

## Stop
Write a class named `Stop`, each instance of which represents a single bus stop.

It should have the following attributes:
- `self.stop_id`: A unique identifier for the stop (string)
- `self.name`:  The name of the stop (string)

It should have the following methods:
- `__init__(self, stop_id: str, name: str)`
  - Initialize a stop with the given ID and name.
- `__repr__(self) -> str`
  - Return a string representation in the format: `"S42: Garfield Blvd"`

## Route
Write a class named `Route`, each instance of which represents one bus route.

It should have the following attributes:
- `self.route_id`: A unique identifier for the route (string)
- `self.route_name`: The name of the route (string)
- `self.stops`: A list of `Stop` objects in route order
  - Example:
```[Stop("S1", "Garfield Blvd"), Stop("S2", "Halsted St")]```
- `self.travel_times`: A list of integers representing minutes between consecutive stops
  - Example:
``` [5, 7]```

It should have the following methods:
- `__init__(self, data: dict)`
  - Accept a dictionary corresponding to a row in the CSV file and initialize the route.
  - In particular, you must parse:
    -  `data["stops"]` into the ordered list of `Stop` objects stored in `self.stops`
    - `data["travel_times"]` into a list of integers stored in `self.travel_times`
  - `serves(self, stop_id: str) -> bool`
    - Return `True` if this route serves a stop with the given stop ID (that is, if any `Stop` in `self.stops` has `stop_id` equal to the given value), and `False` otherwise.
  - `travel_time(self, stop_a: str, stop_b: str) -> int | None`
    - Return the total travel time in minutes to travel from the stop with ID `stop_a` to the stop with ID `stop_b` along this route.
    - The stops are identified by matching the given IDs against the `stop_id` values of the `Stop` objects in `self.stops`.


**Rules:**
- The route may be traveled in either direction.
- If either stop is **not** served by this route, return `None`.
- If `stop_a == stop_b` and the stop is served by the route, `return 0`.
- Otherwise, the time is the sum of the travel times between the two stops along the route.

Example:
- Stops:
```
S1 > S2 > S3 > S4
```
- Travel times:
``` 
[5, 7, 6]
```

- Then:
``` 
travel_time("S1", "S4") # 18 
travel_time("S4", "S2") # 13
```


## TransitSchedule

Write a class named `TransitSchedule`, which manages a collection of routes and supports search operations.

It should have the following methods:
- `__init__(self, filename: str)`: Read the CSV file and initialize the schedule. You should create a `Route` object for each row in the file and store all routes in the schedule.
- `search_by_stop(self, stop_id: str) -> list[Route]`
  - Return a list of all routes that serve the given stop.
- `fastest_route(self, stop_a: str, stop_b: str) -> list[Route]`
  - Return a list of `Route`s that serve both stops (identified by their stop IDs), ordered from fastest to slowest based on the travel time between the two stops.

**Rules:**
- Exclude routes where `travel_time(stop_a, stop_b)` is `None`.
- Sort by travel time ***ascending*** (i.e., fastest first)
- Ties should be broken by `route_id` ascending.

## Sample of Dataset 
`routes.csv` is valid CSV, and looks like the following:

```
route_id | route_name | stops | travel_times -------------------------------------------------------------------------------- 
55,Garfield Bus,"S1:Garfield Blvd>S2:Halsted St>S3:State St>S4:Midway","5,7,6"
6,Jackson Express,"S2:Halsted St>S3:State St>S5:Jackson Blvd","4,8"
12,Midway Local,"S4:Midway>S3:State St>S2:Halsted St>S1:Garfield Blvd","6,7,5"
```
