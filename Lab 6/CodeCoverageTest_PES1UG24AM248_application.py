"""Line/code coverage tests for bus_transit_fare.py.

Run from this directory:
    coverage erase
    coverage run --source=bus_transit_fare -m pytest CodeCoverageTest_PES1UG24AM248_application.py
    coverage report -m
"""
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_invalid_manifest_input():
    with pytest.raises(ValueError):
        process_commute_manifest("not-a-list", 2.0)


def test_invalid_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1.0)


def test_inactive_manifest_is_skipped():
    result = process_commute_manifest(
        [{"route_active": False, "route_type": "local",
          "commuters": [{"zones": 1, "type": "regular"}]}],
        2.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_express_blacklisted_and_priority_booking():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "express",
          "priority_boarding": True,
          "commuters": [{"zones": 2, "type": "regular", "blacklisted": True}]}],
        2.0,
    )
    assert result == {"total_fare": 2.0, "status": "COMPLETED"}



def test_blacklisted_local_commuter_adds_zero_fare():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 1, "blacklisted": True}]}],
        0.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_shuttle_student_and_senior_fares():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "shuttle",
          "commuters": [{"zones": 2, "type": "student"},
                        {"zones": 1, "type": "senior"}]}],
        1.0,
    )
    assert result["total_fare"] == 5.65
    assert result["status"] == "COMPLETED"


def test_local_regular_and_invalid_zone():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 2, "type": "regular"},
                        {"zones": 0, "type": "regular"}]}],
        1.0,
    )
    assert result["total_fare"] == 4.5


def test_unknown_route_is_rejected():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "night",
          "commuters": [{"zones": 1, "type": "regular"}]}],
        1.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_audit_rejection_after_five_invalid_rides():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 0} for _ in range(5)]}],
        1.0,
    )
    assert result["status"] == "AUDIT_REJECTED"


def test_turnstile_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_jam():
    assert inspect_smartcard_turnstiles([[4, 5]]) == "TURNSTILE_JAM"


def test_turnstile_operational():
    assert inspect_smartcard_turnstiles([[1, 4, 1, 2]]) == "OPERATIONAL"
