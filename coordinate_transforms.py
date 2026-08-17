import numpy as np
import math
from datetime import datetime

class CoordinateTransforms:
    """Transform ICRF RA/DEC angles to local Az/El gimbal commands."""

    def __init__(self, latitude, longitude):
        """
        Initialize with observer location in geodetic coordinates.

        Assumes local frame is aligned with gravity (Z-up, ENU).

        Args:
            latitude: observer latitude in degrees
            longitude: observer longitude in degrees
        """
        self.lat = math.radians(latitude)
        self.lon = math.radians(longitude)

        # Cache for current device state
        self.current_az = 0.0
        self.current_el = 0.0

    def ra_dec_to_icrf_vector(self, ra_deg, dec_deg):
        """
        Convert RA/DEC angles (ICRF) to unit vector in ICRF frame.

        Args:
            ra_deg: Right Ascension in degrees (0-360)
            dec_deg: Declination in degrees (-90 to +90)

        Returns:
            los_icrf: unit vector [X, Y, Z] in ICRF frame
        """
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)

        # Standard spherical-to-Cartesian conversion for ICRF
        x = math.cos(dec) * math.cos(ra)
        y = math.cos(dec) * math.sin(ra)
        z = math.sin(dec)

        return np.array([x, y, z])

    def icrf_to_enu(self, los_icrf, datetime_obj):
        """
        Convert ICRF direction vector to ENU (East-North-Up) local frame.

        Handles ICRF → ITRF → ENU transformation.

        Args:
            los_icrf: unit vector in ICRF frame [X, Y, Z]
            datetime_obj: datetime object (for Earth rotation angle)

        Returns:
            los_enu: unit vector in ENU frame [E, N, U]
        """
        # Step 1: ICRF → ITRF (Earth rotation)
        # Simplified: rotate about Z-axis by Greenwich Mean Sidereal Time (GMST)
        gmst = self._compute_gmst(datetime_obj)

        # Rotation matrix: ICRF → ITRF (rotation about Z by -GMST)
        cos_gmst = math.cos(gmst)
        sin_gmst = math.sin(gmst)
        R_icrf_to_itrf = np.array([
            [cos_gmst,  sin_gmst,  0],
            [-sin_gmst, cos_gmst,  0],
            [0,         0,         1]
        ])

        los_itrf = R_icrf_to_itrf @ los_icrf

        # Step 2: ITRF → ENU
        # Rotation matrix from ITRF to ENU (local topocentric)
        sin_lat = math.sin(self.lat)
        cos_lat = math.cos(self.lat)
        sin_lon = math.sin(self.lon)
        cos_lon = math.cos(self.lon)

        R_itrf_to_enu = np.array([
            [-sin_lon,                cos_lon,           0],
            [-sin_lat * cos_lon,  -sin_lat * sin_lon,  cos_lat],
            [cos_lat * cos_lon,   cos_lat * sin_lon,   sin_lat]
        ])

        los_enu = R_itrf_to_enu @ los_itrf

        # Normalize (should already be ~1, but ensure numerical stability)
        los_enu = los_enu / np.linalg.norm(los_enu)

        return los_enu

    def _compute_gmst(self, dt):
        """
        Compute Greenwich Mean Sidereal Time (GMST) in radians.

        Simplified formula (accurate enough for tracking, not astrometric precision).

        Args:
            dt: datetime object (UT)

        Returns:
            gmst: angle in radians
        """
        # Julian Date from epoch 2000.0
        jd = self._datetime_to_jd(dt)
        jd2000 = 2451545.0
        d = jd - jd2000  # days from J2000.0 (fractional, i.e. includes time of day)
        t = d / 36525.0  # centuries from J2000.0

        # GMST formula in degrees (IAU 1982), linear term uses raw day count `d`
        # (not centuries `t`) since it carries the sub-day rotation rate.
        gmst_deg = (280.46061837 + 360.98564736629 * d +
                    0.000387933 * t**2 - t**3 / 38710000.0)

        gmst_deg = gmst_deg % 360.0
        return math.radians(gmst_deg)

    def _datetime_to_jd(self, dt):
        """Convert Python datetime to Julian Date."""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3

        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd = jdn + (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0

        return jd

    def enu_to_az_el(self, los_enu):
        """
        Convert ENU unit vector to azimuth and elevation.

        Args:
            los_enu: normalized line-of-sight vector in ENU [E, N, U]

        Returns:
            az, el: azimuth (0-360°) and elevation (-90 to +90°)
        """
        E = los_enu[0]
        N = los_enu[1]
        U = los_enu[2]

        # Elevation: angle above horizon
        el = math.degrees(math.asin(U))

        # Azimuth: angle from North, clockwise
        # atan2(E, N) gives angle, convert to 0-360°
        az = math.degrees(math.atan2(E, N))
        if az < 0:
            az += 360.0

        return az, el

    def unwrap_azimuth(self, az_target, az_current):
        """
        Unwrap azimuth to take shortest path and handle 0/360 wrap.

        Args:
            az_target: target azimuth (0-360°)
            az_current: current/last azimuth command

        Returns:
            az_command: unwrapped azimuth command (may exceed 0-360° range)
        """
        # Compute shortest path
        delta = az_target - az_current

        # Normalize to -180 to +180
        while delta > 180:
            delta -= 360
        while delta < -180:
            delta += 360

        # Compute unwrapped target
        az_command = az_current + delta

        return az_command

    def handle_singularity(self, az, el, el_threshold=85.0):
        """
        Handle gimbal singularities near zenith.

        When elevation is too high, azimuth becomes undefined/unstable.
        Strategy: freeze azimuth, only command elevation.

        Args:
            az, el: target azimuth and elevation
            el_threshold: elevation angle to trigger singularity handling (degrees)

        Returns:
            az_cmd, el_cmd: commanded azimuth and elevation
            singularity_active: boolean indicating if singularity handling is active
        """
        singularity_active = False

        if abs(el) > el_threshold:
            singularity_active = True
            # Near zenith: freeze azimuth, only update elevation
            az_cmd = self.current_az
            el_cmd = el
            print(f"[SINGULARITY] Elevation {el:.1f}° > threshold {el_threshold}°. Freezing azimuth.")
        else:
            az_cmd = az
            el_cmd = el

        return az_cmd, el_cmd, singularity_active

    def ra_dec_to_gimbal_command(self, ra_deg, dec_deg, datetime_obj):
        """
        Full pipeline: RA/DEC (ICRF) → ENU → Az/El gimbal commands.

        Args:
            ra_deg: Right Ascension in degrees (0-360)
            dec_deg: Declination in degrees (-90 to +90)
            datetime_obj: datetime object (UT) for Earth rotation

        Returns:
            dict with:
                'az_cmd': azimuth command (degrees, may unwrap)
                'el_cmd': elevation command (degrees)
                'los_enu': line-of-sight unit vector in ENU
                'los_icrf': line-of-sight unit vector in ICRF
                'singularity_active': boolean
        """
        # Step 1: RA/DEC → ICRF unit vector
        los_icrf = self.ra_dec_to_icrf_vector(ra_deg, dec_deg)

        # Step 2: ICRF → ENU
        los_enu = self.icrf_to_enu(los_icrf, datetime_obj)

        # Step 3: ENU → Az/El
        az_raw, el_raw = self.enu_to_az_el(los_enu)

        # Step 4: Unwrap azimuth for continuous motion
        az_cmd = self.unwrap_azimuth(az_raw, self.current_az)

        # Step 5: Handle singularities
        az_cmd, el_cmd, singularity_active = self.handle_singularity(az_cmd, el_raw)

        # Step 6: Update current state
        self.current_az = az_cmd
        self.current_el = el_cmd

        result = {
            'az_cmd': az_cmd,
            'el_cmd': el_cmd,
            'az_raw': az_raw,
            'el_raw': el_raw,
            'los_enu': los_enu,
            'los_icrf': los_icrf,
            'singularity_active': singularity_active,
            'az_unwrap_turns': (az_cmd - az_raw) / 360.0
        }

        return result

    def update_gimbal_state(self, az, el):
        """Update current gimbal position (called after motor moves)."""
        self.current_az = az
        self.current_el = el
