import re
import math
from datetime import datetime, timedelta
from coordinate_transforms import CoordinateTransforms

class AzEl:
    """Parse ephemeris RA/DEC data and compute Az/El gimbal commands."""

    def __init__(self, ephemeris_file_path, latitude, longitude):
        """
        Initialize with ephemeris file and observer location.

        Args:
            ephemeris_file_path: path to Horizons ephemeris CSV file
            latitude: observer latitude in degrees
            longitude: observer longitude in degrees
        """
        self.latitude = latitude
        self.longitude = longitude
        self.transformer = CoordinateTransforms(latitude, longitude)

        # Data storage
        self.data = []
        self.current_ra = 0.0
        self.current_dec = 0.0
        self.current_azimuth = 0.0
        self.current_elevation = 0.0
        self.current_azimuth_rate = 0.0
        self.current_elevation_rate = 0.0

        # Parse ephemeris file
        self.parse_ephemeris_data(ephemeris_file_path)

        # Get initial Az/El
        if len(self.data) > 0:
            self.get_az_el(datetime.now())

    def parse_ephemeris_data(self, ephemeris_file_path):
        """
        Parse Horizons ephemeris CSV file for RA/DEC data.

        Extracts: Date, R.A._(ICRF), DEC__(ICRF) columns

        Args:
            ephemeris_file_path: path to CSV file
        """
        try:
            with open(ephemeris_file_path, 'r') as f:
                lines = f.readlines()

            # Find data section
            try:
                start_index = lines.index('$$SOE\n') + 1
                end_index = lines.index('$$EOE\n')
            except ValueError:
                print("[ERROR] Could not find $$SOE or $$EOE markers")
                return

            # Parse CSV rows
            # Format: Date, skip, skip, R.A._(ICRF), DEC__(ICRF), ...
            for line in lines[start_index:end_index]:
                parts = [p.strip() for p in line.split(',')]

                if len(parts) < 5:
                    continue

                # Extract datetime
                try:
                    date_str = parts[0]
                    dt = datetime.strptime(date_str, '%Y-%b-%d %H:%M')
                except (ValueError, IndexError):
                    continue

                # Extract RA and DEC (columns 3 and 4 after split)
                # RA is in HMS format (HH MM SS.SS), need to convert to degrees
                # DEC is in DMS format (±DD MM SS.SS), need to convert to degrees
                try:
                    ra_str = parts[3]  # e.g., "09 37 37.24"
                    dec_str = parts[4]  # e.g., "+14 09 32.3"

                    # Convert RA (HMS) to degrees (1 hour = 15 degrees)
                    ra_parts = ra_str.split()
                    if len(ra_parts) == 3:
                        ra_deg = (float(ra_parts[0]) * 15.0 +
                                  float(ra_parts[1]) * 0.25 +
                                  float(ra_parts[2]) / 240.0)
                    else:
                        continue

                    # Convert DEC (DMS) to degrees
                    dec_sign = 1 if '+' in dec_str else -1
                    dec_str_clean = dec_str.replace('+', '').replace('-', '')
                    dec_parts = dec_str_clean.split()
                    if len(dec_parts) == 3:
                        dec_deg = (float(dec_parts[0]) +
                                   float(dec_parts[1]) / 60.0 +
                                   float(dec_parts[2]) / 3600.0) * dec_sign
                    else:
                        continue

                    # Store data
                    self.data.append({
                        'datetime': dt,
                        'ra': ra_deg,
                        'dec': dec_deg
                    })

                except (ValueError, IndexError):
                    continue

            print(f"[INFO] Parsed {len(self.data)} ephemeris points")

        except FileNotFoundError:
            print(f"[ERROR] File not found: {ephemeris_file_path}")

    def linear_interpolate_ra_dec(self, dt):
        """
        Linear interpolation for RA/DEC at given datetime.

        Args:
            dt: datetime object

        Returns:
            ra, dec: interpolated RA and DEC in degrees, or (None, None)
        """
        for i in range(len(self.data) - 1):
            if self.data[i]['datetime'] <= dt <= self.data[i + 1]['datetime']:
                # Interpolation weights
                dt_total = (self.data[i + 1]['datetime'] - self.data[i]['datetime']).total_seconds()
                dt_current = (dt - self.data[i]['datetime']).total_seconds()

                if dt_total == 0:
                    return self.data[i]['ra'], self.data[i]['dec']

                w1 = (dt_total - dt_current) / dt_total
                w2 = dt_current / dt_total

                # Interpolate
                ra = self.data[i]['ra'] * w1 + self.data[i + 1]['ra'] * w2
                dec = self.data[i]['dec'] * w1 + self.data[i + 1]['dec'] * w2

                return ra, dec

        return None, None

    def get_az_el(self, dt):
        """
        Compute Az/El gimbal commands at given datetime.

        Uses RA/DEC from ephemeris and transforms to local Az/El.

        Args:
            dt: datetime object (UT)

        Returns:
            bool: True if successful, False otherwise
        """
        # Interpolate RA/DEC
        ra, dec = self.linear_interpolate_ra_dec(dt)

        if ra is None or dec is None:
            print(f"[ERROR] Datetime {dt} outside ephemeris range")
            return False

        self.current_ra = ra
        self.current_dec = dec

        # Transform to Az/El using coordinate transformer
        result = self.transformer.ra_dec_to_gimbal_command(ra, dec, dt)

        self.current_azimuth = result['az_cmd']
        self.current_elevation = result['el_cmd']

        # Compute rates (numerical differentiation)
        dt_delta = 60  # seconds
        dt_next = dt + timedelta(seconds=dt_delta)
        dt_prev = dt - timedelta(seconds=dt_delta)

        try:
            ra_next, dec_next = self.linear_interpolate_ra_dec(dt_next)
            if ra_next is not None and dec_next is not None:
                result_next = self.transformer.ra_dec_to_gimbal_command(ra_next, dec_next, dt_next)

                ra_prev, dec_prev = self.linear_interpolate_ra_dec(dt_prev)
                if ra_prev is not None and dec_prev is not None:
                    result_prev = self.transformer.ra_dec_to_gimbal_command(ra_prev, dec_prev, dt_prev)

                    # Central difference for rates (deg/s)
                    self.current_azimuth_rate = (result_next['az_cmd'] - result_prev['az_cmd']) / (2 * dt_delta)
                    self.current_elevation_rate = (result_next['el_cmd'] - result_prev['el_cmd']) / (2 * dt_delta)
                else:
                    self.current_azimuth_rate = 0.0
                    self.current_elevation_rate = 0.0
            else:
                self.current_azimuth_rate = 0.0
                self.current_elevation_rate = 0.0
        except Exception as e:
            print(f"[WARN] Error computing rates: {e}")
            self.current_azimuth_rate = 0.0
            self.current_elevation_rate = 0.0

        return True

    def get_current_azimuth(self):
        return self.current_azimuth

    def get_current_elevation(self):
        return self.current_elevation

    def get_current_azimuth_rate(self):
        return self.current_azimuth_rate

    def get_current_elevation_rate(self):
        return self.current_elevation_rate

    def get_current_ra(self):
        return self.current_ra

    def get_current_dec(self):
        return self.current_dec

    def get_daily_azimuth_rate(self):
        """Estimate max azimuth rate over the ephemeris period."""
        if len(self.data) < 2:
            return 0.1

        # Use a scratch transformer for this full-period scan so its
        # azimuth-unwrap state doesn't clobber self.transformer's, which
        # tracks the actual current commanded azimuth used for pointing.
        scan_transformer = CoordinateTransforms(self.latitude, self.longitude)

        max_rate = 0.0
        for i in range(len(self.data) - 1):
            dt = (self.data[i + 1]['datetime'] - self.data[i]['datetime']).total_seconds()
            if dt > 0:
                result1 = scan_transformer.ra_dec_to_gimbal_command(
                    self.data[i]['ra'], self.data[i]['dec'], self.data[i]['datetime'])
                result2 = scan_transformer.ra_dec_to_gimbal_command(
                    self.data[i + 1]['ra'], self.data[i + 1]['dec'], self.data[i + 1]['datetime'])

                az_rate = abs(result2['az_cmd'] - result1['az_cmd']) / dt
                max_rate = max(max_rate, az_rate)

        return max_rate

    def get_daily_elevation_rate(self):
        """Estimate max elevation rate over the ephemeris period."""
        if len(self.data) < 2:
            return 0.1

        # Use a scratch transformer for this full-period scan so its
        # azimuth-unwrap state doesn't clobber self.transformer's, which
        # tracks the actual current commanded azimuth used for pointing.
        scan_transformer = CoordinateTransforms(self.latitude, self.longitude)

        max_rate = 0.0
        for i in range(len(self.data) - 1):
            dt = (self.data[i + 1]['datetime'] - self.data[i]['datetime']).total_seconds()
            if dt > 0:
                result1 = scan_transformer.ra_dec_to_gimbal_command(
                    self.data[i]['ra'], self.data[i]['dec'], self.data[i]['datetime'])
                result2 = scan_transformer.ra_dec_to_gimbal_command(
                    self.data[i + 1]['ra'], self.data[i + 1]['dec'], self.data[i + 1]['datetime'])

                el_rate = abs(result2['el_cmd'] - result1['el_cmd']) / dt
                max_rate = max(max_rate, el_rate)

        return max_rate
