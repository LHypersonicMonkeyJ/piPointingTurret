import unittest
import tempfile
import os
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from az_el import AzEl


class TestAzEl(unittest.TestCase):
    """Unit tests for AzEl ephemeris parsing and Az/El computation."""

    def setUp(self):
        """Set up test fixtures."""
        self.latitude = 40.7128
        self.longitude = -74.0060

        # Create a minimal ephemeris file for testing
        self.ephemeris_content = """
*******************************************************************************
Ephemeris / API_USER Test
*******************************************************************************
Target body name: Sun (10)
$$SOE
 2026-Aug-15 00:00, , , 09 37 37.24, +14 09 32.3,    09 39 03.67, +14 02 25.7
 2026-Aug-15 00:05, , , 09 37 38.03, +14 09 28.4,    09 39 04.46, +14 02 21.8
 2026-Aug-15 00:10, , , 09 37 38.82, +14 09 24.5,    09 39 05.25, +14 02 17.9
 2026-Aug-15 00:15, , , 09 37 39.61, +14 09 20.6,    09 39 06.04, +14 02 13.9
$$EOE
*******************************************************************************
"""

    def test_parse_ephemeris_valid_file(self):
        """Test parsing a valid ephemeris file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)
            # Should have parsed 4 data points
            self.assertEqual(len(az_el.data), 4)
        finally:
            os.unlink(temp_file)

    def test_parse_ephemeris_datetime_extraction(self):
        """Test that datetimes are correctly extracted."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)
            # Check first datetime
            self.assertEqual(az_el.data[0]['datetime'].year, 2026)
            self.assertEqual(az_el.data[0]['datetime'].month, 8)
            self.assertEqual(az_el.data[0]['datetime'].day, 15)
            self.assertEqual(az_el.data[0]['datetime'].hour, 0)
            self.assertEqual(az_el.data[0]['datetime'].minute, 0)
        finally:
            os.unlink(temp_file)

    def test_parse_ephemeris_ra_dec_extraction(self):
        """Test that RA/DEC values are correctly extracted and converted."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            # First data point: RA = 09 37 37.24 (should be ~144.405°)
            # 9 * 15 + 37 * 0.25 + 37.24 / 240 ≈ 144.405
            expected_ra = 9 * 15 + 37 * 0.25 + 37.24 / 240.0
            self.assertAlmostEqual(az_el.data[0]['ra'], expected_ra, places=1)

            # First data point: DEC = +14 09 32.3 (should be ~14.159°)
            # 14 + 9/60 + 32.3/3600 ≈ 14.159
            expected_dec = 14 + 9 / 60.0 + 32.3 / 3600.0
            self.assertAlmostEqual(az_el.data[0]['dec'], expected_dec, places=2)
        finally:
            os.unlink(temp_file)

    def test_linear_interpolate_ra_dec_exact_match(self):
        """Test interpolation when datetime exactly matches a data point."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            # Query exact time of first data point
            dt = az_el.data[0]['datetime']
            ra, dec = az_el.linear_interpolate_ra_dec(dt)

            self.assertIsNotNone(ra)
            self.assertIsNotNone(dec)
            self.assertAlmostEqual(ra, az_el.data[0]['ra'], places=5)
            self.assertAlmostEqual(dec, az_el.data[0]['dec'], places=5)
        finally:
            os.unlink(temp_file)

    def test_linear_interpolate_ra_dec_midpoint(self):
        """Test interpolation at midpoint between two data points."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            # Create a time halfway between first and second data points
            dt1 = az_el.data[0]['datetime']
            dt2 = az_el.data[1]['datetime']
            dt_mid = datetime(dt1.year, dt1.month, dt1.day,
                              dt1.hour, int((dt1.minute + dt2.minute) / 2), 30)

            ra, dec = az_el.linear_interpolate_ra_dec(dt_mid)

            # Interpolated values should be between the two points
            self.assertGreaterEqual(ra, min(az_el.data[0]['ra'], az_el.data[1]['ra']))
            self.assertLessEqual(ra, max(az_el.data[0]['ra'], az_el.data[1]['ra']))
        finally:
            os.unlink(temp_file)

    def test_linear_interpolate_ra_dec_outside_range(self):
        """Test interpolation outside ephemeris range returns None."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            # Query time before ephemeris starts
            dt_before = datetime(2026, 8, 14, 23, 55, 0)
            ra, dec = az_el.linear_interpolate_ra_dec(dt_before)

            self.assertIsNone(ra)
            self.assertIsNone(dec)

            # Query time after ephemeris ends
            dt_after = datetime(2026, 8, 15, 0, 20, 0)
            ra, dec = az_el.linear_interpolate_ra_dec(dt_after)

            self.assertIsNone(ra)
            self.assertIsNone(dec)
        finally:
            os.unlink(temp_file)

    def test_get_az_el_returns_bool(self):
        """Test that get_az_el returns boolean status."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            # Valid time
            dt = az_el.data[0]['datetime']
            status = az_el.get_az_el(dt)
            self.assertTrue(status)

            # Invalid time (outside range)
            dt_invalid = datetime(2025, 1, 1, 0, 0, 0)
            status = az_el.get_az_el(dt_invalid)
            self.assertFalse(status)
        finally:
            os.unlink(temp_file)

    def test_get_az_el_sets_current_values(self):
        """Test that get_az_el sets current_azimuth and current_elevation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            dt = az_el.data[0]['datetime']
            az_el.get_az_el(dt)

            # Should have set values
            self.assertIsNotNone(az_el.current_azimuth)
            self.assertIsNotNone(az_el.current_elevation)
            self.assertIsInstance(az_el.current_azimuth, (int, float))
            self.assertIsInstance(az_el.current_elevation, (int, float))
        finally:
            os.unlink(temp_file)

    def test_get_current_accessors(self):
        """Test getter methods for current values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            dt = az_el.data[0]['datetime']
            az_el.get_az_el(dt)

            # Test getters
            az = az_el.get_current_azimuth()
            el = az_el.get_current_elevation()
            ra = az_el.get_current_ra()
            dec = az_el.get_current_dec()

            self.assertIsInstance(az, (int, float))
            self.assertIsInstance(el, (int, float))
            self.assertIsInstance(ra, (int, float))
            self.assertIsInstance(dec, (int, float))
        finally:
            os.unlink(temp_file)

    def test_get_daily_rates(self):
        """Test daily azimuth and elevation rate calculations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.ephemeris_content)
            f.flush()
            temp_file = f.name

        try:
            az_el = AzEl(temp_file, self.latitude, self.longitude)

            az_rate = az_el.get_daily_azimuth_rate()
            el_rate = az_el.get_daily_elevation_rate()

            # Rates should be positive
            self.assertGreater(az_rate, 0)
            self.assertGreater(el_rate, 0)

            # Rates should be reasonable (< 360 deg/sec)
            self.assertLess(az_rate, 360)
            self.assertLess(el_rate, 360)
        finally:
            os.unlink(temp_file)

    def test_ephemeris_file_not_found(self):
        """Test handling of missing ephemeris file."""
        # Should not raise exception, just print error
        az_el = AzEl('/nonexistent/path/to/ephemeris.txt', self.latitude, self.longitude)
        self.assertEqual(len(az_el.data), 0)


if __name__ == '__main__':
    unittest.main()
