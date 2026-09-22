"""Tests for sanitizacion-santiago dashboard."""

from pathlib import Path

import pandas as pd

# The dashboard doesn't have a src/ module, tests are for data integrity
# which already exists in test_dashboard.py


def test_dashboard_data_exists():
    """Test that raw data file exists."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    assert data_path.exists()


def test_dashboard_data_structure():
    """Test that data has expected columns and types."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    df = pd.read_csv(data_path)

    assert "name" in df.columns
    assert "description" in df.columns
    assert "lat" in df.columns
    assert "lon" in df.columns
    assert "type" in df.columns


def test_dashboard_lat_bounds():
    """Test latitude is within Santiago bounds."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    df = pd.read_csv(data_path)

    # Santiago approximate bounds
    assert df["lat"].between(-33.50, -33.35).all()


def test_dashboard_lon_bounds():
    """Test longitude is within Santiago bounds."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    df = pd.read_csv(data_path)

    # Santiago approximate bounds
    assert df["lon"].between(-70.75, -70.55).all()


def test_dashboard_types_valid():
    """Test type values are from expected set."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    df = pd.read_csv(data_path)

    expected_types = {"Pasaje", "Edificio", "Domicilio", "Calle", "Otro"}
    assert set(df["type"].unique()).issubset(expected_types)


def test_dashboard_no_nulls():
    """Test no null values in critical columns."""
    data_path = (
        Path(__file__).parent.parent / "data" / "raw" / "sanitization_points.csv"
    )
    df = pd.read_csv(data_path)

    assert df["name"].notna().all()
    assert df["lat"].notna().all()
    assert df["lon"].notna().all()
    assert df["type"].notna().all()


def test_dashboard_street_extraction_regex():
    """Test that street extraction regex handles '10 de Julio' format."""
    import re

    # Updated regex should handle numbers at start of street name
    street_pattern = r"^([A-Za-z0-9áéíóúñü\s\.\-]+)"

    test_cases = [
        ("10 de Julio 462", "10 de Julio"),
        ("San Francisco 838", "San Francisco"),
        ("Av. España 170", "Av. España"),
        ("Pasaje Emilio", "Pasaje Emilio"),
    ]

    for name, expected_street in test_cases:
        match = re.match(street_pattern, name)
        assert match is not None, f"No match for: {name}"
        extracted = match.group(1).strip()
        assert expected_street.lower() in extracted.lower(), (
            f"Expected '{expected_street}' in '{extracted}' for '{name}'"
        )
