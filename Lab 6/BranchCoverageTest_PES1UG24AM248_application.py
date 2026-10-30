"""Branch coverage tests for bus_transit_fare.py.

Run from this directory:
    coverage erase
    coverage run --branch --source=bus_transit_fare -m pytest BranchCoverageTest_PES1UG24AM248_application.py
    coverage report -m
"""
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_invalid_manifest_type():
    with pytest.raises(ValueError):
        process_commute_manifest(None, 2.0)


def test_negative_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -0.01)


def test_inactive_route_and_missing_defaults():
    result = process_commute_manifest([{}], 0.0)
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


@pytest.mark.parametrize(
    "route_type, expected_base",
    [("express", 6.0), ("shuttle", 4.0), ("local", 2.5)],
)
def test_each_supported_route_type(route_type, expected_base):
    result = process_commute_manifest(
        [{"route_active": True, "route_type": route_type,
          "commuters": [{"zones": 1, "type": "regular"}]}],
        0.0,
    )
    assert result["total_fare"] == expected_base + 1.0


def test_unknown_route_type():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "intercity",
          "commuters": [{"zones": 1}]}],
        0.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_zero_and_negative_zones_are_rejected():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 0}, {"zones": -2}]}],
        0.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_blacklisted_non_express_commuter_adds_no_fare_but_continues():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 1, "blacklisted": True},
                        {"zones": 1, "type": "regular"}]}],
        0.0,
    )
    assert result == {"total_fare": 3.5, "status": "COMPLETED"}


def test_blacklisted_express_commuter_cancels_manifest_fare():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "express",
          "priority_boarding": False,
          "commuters": [{"zones": 1, "type": "regular"},
                        {"zones": 1, "blacklisted": True},
                        {"zones": 1, "type": "regular"}]}],
        0.0,
    )
    assert result == {"total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_student_senior_and_regular_fares():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 2, "type": "student"},
                        {"zones": 2, "type": "senior"},
                        {"zones": 2, "type": "regular"}]}],
        0.0,
    )
    # Student 1.75 + senior 2.45 + regular 4.50
    assert result == {"total_fare": 8.7, "status": "COMPLETED"}


def test_priority_boarding_fee_is_added():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "priority_boarding": True,
          "commuters": [{"zones": 1, "type": "regular"}]}],
        2.0,
    )
    assert result == {"total_fare": 5.5, "status": "COMPLETED"}


def test_audit_rejected_when_rejections_exceed_four():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "unknown"} for _ in range(5)],
        0.0,
    )
    assert result == {"total_fare": 0.0, "status": "AUDIT_REJECTED"}


def test_completed_status_with_nonzero_fare():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 1, "type": "regular"}]}],
        0.0,
    )
    assert result["status"] == "COMPLETED"


def test_turnstile_no_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_jam_after_two_consecutive_high_readings():
    assert inspect_smartcard_turnstiles([[4, 4]]) == "TURNSTILE_JAM"


def test_turnstile_streak_resets_after_normal_reading():
    assert inspect_smartcard_turnstiles([[4, 2, 5]]) == "OPERATIONAL"


def test_turnstile_operational_with_single_high_reading():
    assert inspect_smartcard_turnstiles([[4, 1, 2]]) == "OPERATIONAL"


def test_turnstile_multiple_devices():
    assert inspect_smartcard_turnstiles([[4], [1, 2, 3]]) == "OPERATIONAL"
