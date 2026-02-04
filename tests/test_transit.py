from transit import Stop, Route, TransitSchedule

ROUTES = "routes.csv"

# --------------------------------------------------------------------
# Stop
# --------------------------------------------------------------------

def test_stop_init_sets_attributes():
    s = Stop("S1", "Midway Terminal")
    assert s.stop_id == "S1"
    assert s.name == "Midway Terminal"


def test_stop_repr_matches_spec_format():
    s = Stop("S42", "Garfield Blvd")
    assert repr(s) == "S42: Garfield Blvd"


# --------------------------------------------------------------------
# TransitSchedule: loading
# --------------------------------------------------------------------

def test_schedule_loads_all_routes_from_routes_csv():
    sched = TransitSchedule(str(ROUTES))
    assert isinstance(sched.routes, list)
    assert len(sched.routes) == 25


def test_schedule_contains_known_route_ids():
    sched = TransitSchedule(str(ROUTES))
    ids = {r.route_id for r in sched.routes}
    for expected in {"55", "X55", "9", "8", "X20", "53"}:
        assert expected in ids


# --------------------------------------------------------------------
# Route parsing and attributes (via loaded schedule)
# --------------------------------------------------------------------

def test_loaded_route_has_expected_attributes_types():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert isinstance(r.route_id, str)
    assert isinstance(r.route_name, str)
    assert isinstance(r.stops, list)
    assert isinstance(r.travel_times, list)
    assert all(isinstance(x, Stop) for x in r.stops)

def test_loaded_route_stops_are_ids_only_not_names():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    # Route 55 is defined with stop IDs S1..S8 in our ROUTES file.
    assert [s.stop_id for s in r.stops[:4]] == ["S1", "S2", "S3", "S4"]

# --------------------------------------------------------------------
# Route.serves()
# --------------------------------------------------------------------

def test_route_serves_true_for_known_stop():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.serves("S1") is True
    assert r.serves("S8") is True


def test_route_serves_false_for_unknown_stop():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.serves("S999") is False

def test_route_parsing_and_serves():
    data = {
        "route_id": "55",
        "route_name": "Garfield Bus",
        "stops": "S1:Garfield Blvd>S2:Halsted St>S3:State St>S4:Midway",
        "travel_times": "5,7,6"
    }

    r = Route(data)

    # stops should be parsed in order (Stop objects)
    assert [s.stop_id for s in r.stops] == ["S1", "S2", "S3", "S4"]

    assert r.serves("S1") is True
    assert r.serves("S9") is False

# --------------------------------------------------------------------
# Route.travel_time()
# --------------------------------------------------------------------

def test_travel_time_returns_none_if_stop_missing():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.travel_time("S1", "S999") is None
    assert r.travel_time("S999", "S1") is None


def test_travel_time_same_stop_served_returns_zero():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.travel_time("S4", "S4") == 0


def test_travel_time_forward_computes_sum_between_stops():
    sched = TransitSchedule(str(ROUTES))
    # 55 Garfield Crosstown:
    # S1->S2 6, S2->S3 5, S3->S4 6, S4->S5 7, S5->S6 5, S6->S7 4, S7->S8 6
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.travel_time("S1", "S2") == 6
    assert r.travel_time("S2", "S4") == 5 + 6
    assert r.travel_time("S1", "S8") == 6 + 5 + 6 + 7 + 5 + 4 + 6


def test_travel_time_reverse_direction_is_supported():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    # Reverse: S8 -> S5 should equal the sum of segments S5->S6 + S6->S7 + S7->S8
    assert r.travel_time("S8", "S5") == 5 + 4 + 6


def test_travel_time_adjacent_is_one_segment_even_in_reverse():
    sched = TransitSchedule(str(ROUTES))
    r = next(rt for rt in sched.routes if rt.route_id == "55")
    assert r.travel_time("S2", "S1") == 6
    assert r.travel_time("S8", "S7") == 6


# --------------------------------------------------------------------
# TransitSchedule.search_by_stop()
# --------------------------------------------------------------------

def test_search_by_stop_returns_empty_list_when_no_routes():
    sched = TransitSchedule(str(ROUTES))
    assert sched.search_by_stop("S999") == []


def test_search_by_stop_finds_hub_stop_with_many_routes():
    sched = TransitSchedule(str(ROUTES))
    routes = sched.search_by_stop("S7")  # State St is a hub in our dataset
    ids = {r.route_id for r in routes}
    # A handful we know serve S7
    for expected in {"55", "X55", "9", "8", "12", "21", "34", "60", "20", "X20", "62"}:
        assert expected in ids
    assert len(ids) >= 10  # should be many routes


# --------------------------------------------------------------------
# TransitSchedule.fastest_route()
# --------------------------------------------------------------------

def test_fastest_route_excludes_routes_not_serving_both_stops():
    sched = TransitSchedule(str(ROUTES))
    # S23 is only on route 22 (Clark Street) in our dataset; S27 is only on 95.
    res = sched.fastest_route("S23", "S27")
    assert res == []


def test_fastest_route_orders_by_time_and_is_deterministic_on_ties():
    sched = TransitSchedule(str(ROUTES))
    # Compare Garfield Crosstown vs Garfield Express between S1 and S8:
    # 55: S1->...->S8 = 39
    # X55: S1->S3 (8) + S3->S5 (10) + S5->S7 (7) + S7->S8 (8) = 33
    res = sched.fastest_route("S1", "S8")
    ids = [r.route_id for r in res]
    assert ids[0] == "X55"
    assert "55" in ids
    # Ensure ordering by travel time is correct for these two
    r_x55 = next(r for r in res if r.route_id == "X55")
    r_55 = next(r for r in res if r.route_id == "55")
    assert r_x55.travel_time("S1", "S8") < r_55.travel_time("S1", "S8")


def test_fastest_route_same_stop_returns_all_routes_serving_stop_sorted_by_route_id():
    sched = TransitSchedule(str(ROUTES))
    res = sched.fastest_route("S1", "S1")
    ids = [r.route_id for r in res]

    # Every returned route must serve S1 and have travel time 0
    for r in res:
        assert r.serves("S1")
        assert r.travel_time("S1", "S1") == 0

    # Deterministic tie-break: route_id ascending (string sort)
    assert ids == sorted(ids)


def test_fastest_route_includes_multiple_routes_and_sorts_correctly():
    sched = TransitSchedule(str(ROUTES))
    # Between S35 (West Terminal) and S7 (State St):
    # X20 is direct with time 14
    # 20 is multi-stop: S35->S20 6, S20->S5 5, S5->S6 5, S6->S7 4 => 20
    res = sched.fastest_route("S35", "S7")
    ids = [r.route_id for r in res]
    assert ids[:2] == ["X20", "20"]
    assert res[0].travel_time("S35", "S7") == 14
    assert res[1].travel_time("S35", "S7") == 20