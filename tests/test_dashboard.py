"""Tests for sanitization_points.csv data integrity."""

from pathlib import Path

import pandas as pd
import pytest

DATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "raw" / "sanitization_points.csv"
)

EXPECTED_COLUMNS = ["name", "description", "lat", "lon", "type"]
EXPECTED_TYPES = {"Pasaje", "Edificio", "Domicilio", "Calle", "Otro"}
LAT_MIN, LAT_MAX = -33.48, -33.42
LON_MIN, LON_MAX = -70.68, -70.63


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)


def test_row_count(df):
    assert len(df) == 87


def test_columns_exist(df):
    assert list(df.columns) == EXPECTED_COLUMNS


def test_all_types_present(df):
    assert set(df["type"].unique()) == EXPECTED_TYPES


def test_lat_in_santiago_bounds(df):
    assert df["lat"].between(LAT_MIN, LAT_MAX).all()


def test_lon_in_santiago_bounds(df):
    assert df["lon"].between(LON_MIN, LON_MAX).all()
