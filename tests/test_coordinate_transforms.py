import unittest
import math
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coordinate_transforms import CoordinateTransforms


class TestCoordinateTransforms(unittest.TestCase):
    """Unit tests for coordinate transformations."""

    def setUp(self):
        """Set up test fixtures."""
        # New York coordinates
        self.latitude = 40.7128
        self.longitude = -74.0060
        self.transformer = CoordinateTransforms(self.latitude, self.longitude)

    def test_ra_dec_to_icrf_vector_north_pole(self):
        """Test RA/DEC to ICRF conversion at celestial north pole."""
        # RA = any value, DEC = 90° (north pole)
        los_icrf = self.transformer.ra_dec_to_icrf_vector(0, 90)

        # Should point along Z axis
        expected = np.array([0, 0, 1])
        np.testing.assert_array_almost_equal(los_icrf, expected, decimal=5)

    def test_ra_dec_to_icrf_vector_south_pole(self):
        """Test RA/DEC to ICRF conversion at celestial south pole."""
        # DEC = -90° (south pole)
        los_icrf = self.transformer.ra_dec_to_icrf_vector(0, -90)

        # Should point along -Z axis
        expected = np.array([0, 0, -1])
        np.testing.assert_array_almost_equal(los_icrf, expected, decimal=5)

    def test_ra_dec_to_icrf_vector_vernal_equinox(self):
        """Test RA/DEC at vernal equinox point."""
        # RA = 0h, DEC = 0° (vernal equinox)
        los_icrf = self.transformer.ra_dec_to_icrf_vector(0, 0)

        # Should point along X axis
        expected = np.array([1, 0, 0])
        np.testing.assert_array_almost_equal(los_icrf, expected, decimal=5)

    def test_ra_dec_to_icrf_vector_magnitude(self):
        """Test that RA/DEC conversion produces unit vectors."""
        test_cases = [
            (0, 0),
            (45, 30),
            (180, -45),
            (270, 60),
        ]

        for ra, dec in test_cases:
            los_icrf = self.transformer.ra_dec_to_icrf_vector(ra, dec)
            magnitude = np.linalg.norm(los_icrf)
            self.assertAlmostEqual(magnitude, 1.0, places=5,
                                   msg=f"Failed for RA={ra}, DEC={dec}")

    def test_enu_to_az_el_zenith(self):
        """Test ENU to Az/El conversion at zenith."""
        # Zenith is straight up
        los_enu = np.array([0, 0, 1])
        az, el = self.transformer.enu_to_az_el(los_enu)

        # Elevation should be 90°, azimuth undefined (we use 0)
        self.assertAlmostEqual(el, 90.0, places=1)

    def test_enu_to_az_el_horizon_north(self):
        """Test ENU to Az/El at horizon toward north."""
        # North is along +N axis
        los_enu = np.array([0, 1, 0])
        los_enu = los_enu / np.linalg.norm(los_enu)
        az, el = self.transformer.enu_to_az_el(los_enu)

        # Should point north (0°) at horizon (0°)
        self.assertAlmostEqual(az, 0.0, places=1)
        self.assertAlmostEqual(el, 0.0, places=1)

    def test_enu_to_az_el_horizon_east(self):
        """Test ENU to Az/El at horizon toward east."""
        # East is along +E axis
        los_enu = np.array([1, 0, 0])
        los_enu = los_enu / np.linalg.norm(los_enu)
        az, el = self.transformer.enu_to_az_el(los_enu)

        # Should point east (90°) at horizon (0°)
        self.assertAlmostEqual(az, 90.0, places=1)
        self.assertAlmostEqual(el, 0.0, places=1)

    def test_unwrap_azimuth_no_wrap(self):
        """Test azimuth unwrapping when no wrap is needed."""
        # Current 45°, target 50° - no wrap needed
        az_cmd = self.transformer.unwrap_azimuth(50, 45)
        self.assertAlmostEqual(az_cmd, 50.0, places=1)

    def test_unwrap_azimuth_positive_wrap(self):
        """Test azimuth unwrapping across 0°/360° boundary (positive direction)."""
        # Current 350°, target 10° - should unwrap to 370°
        az_cmd = self.transformer.unwrap_azimuth(10, 350)
        self.assertAlmostEqual(az_cmd, 370.0, places=1)

    def test_unwrap_azimuth_negative_wrap(self):
        """Test azimuth unwrapping across 0°/360° boundary (negative direction)."""
        # Current 10°, target 350° - should unwrap to -10°
        az_cmd = self.transformer.unwrap_azimuth(350, 10)
        self.assertAlmostEqual(az_cmd, -10.0, places=1)

    def test_handle_singularity_below_threshold(self):
        """Test singularity handling below threshold."""
        self.transformer.current_az = 100.0
        self.transformer.current_el = 50.0

        az_cmd, el_cmd, is_singular = self.transformer.handle_singularity(45, 60)

        # Below threshold, should use target values
        self.assertAlmostEqual(az_cmd, 45.0, places=1)
        self.assertAlmostEqual(el_cmd, 60.0, places=1)
        self.assertFalse(is_singular)

    def test_handle_singularity_above_threshold(self):
        """Test singularity handling above threshold."""
        self.transformer.current_az = 100.0
        self.transformer.current_el = 50.0

        az_cmd, el_cmd, is_singular = self.transformer.handle_singularity(45, 88)

        # Above threshold, should freeze azimuth
        self.assertAlmostEqual(az_cmd, 100.0, places=1)  # Frozen at current
        self.assertAlmostEqual(el_cmd, 88.0, places=1)   # Target elevation
        self.assertTrue(is_singular)

    def test_datetime_to_jd_known_epoch(self):
        """Test Julian Date conversion at a known epoch."""
        # J2000.0 epoch: 2000-01-01 12:00:00
        dt = datetime(2000, 1, 1, 12, 0, 0)
        jd = self.transformer._datetime_to_jd(dt)

        # J2000.0 = 2451545.0
        self.assertAlmostEqual(jd, 2451545.0, places=1)

    def test_gmst_at_j2000(self):
        """Test GMST calculation near J2000.0."""
        dt = datetime(2000, 1, 1, 18, 0, 0)  # 6 hours after J2000.0
        gmst = self.transformer._compute_gmst(dt)

        # GMST should be in radians [0, 2π]
        self.assertGreaterEqual(gmst, 0)
        self.assertLessEqual(gmst, 2 * math.pi)

    def test_full_pipeline_south_pole(self):
        """Test full RA/DEC to Az/El pipeline at south pole."""
        # South pole (DEC = -90°)
        dt = datetime(2000, 1, 1, 12, 0, 0)

        result = self.transformer.ra_dec_to_gimbal_command(0, -90, dt)

        # South pole should have negative elevation
        self.assertLess(result['el_cmd'], 0)

    def test_full_pipeline_zenith(self):
        """Test full pipeline when target is at zenith."""
        # Set transformer at equator for simpler test
        transformer_eq = CoordinateTransforms(0, 0)

        # Zenith direction in ICRF (different depending on location/time)
        dt = datetime(2000, 1, 1, 12, 0, 0)

        result = transformer_eq.ra_dec_to_gimbal_command(0, 0, dt)

        # Should have valid commands
        self.assertIsNotNone(result['az_cmd'])
        self.assertIsNotNone(result['el_cmd'])
        self.assertIsInstance(result['los_enu'], np.ndarray)


if __name__ == '__main__':
    unittest.main()
