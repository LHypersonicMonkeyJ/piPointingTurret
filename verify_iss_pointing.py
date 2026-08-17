"""
Independently verify Az/El pointing commands using astropy.

Reads the CSV produced by generate_iss_orbit_commands.py (utc_time, ra_deg,
dec_deg, az_cmd_deg, el_cmd_deg, ...), and for each row independently
transforms the same (RA, Dec, time, observer location) to Alt/Az using
astropy's ICRS -> AltAz frame (proper precession/nutation/aberration,
no GMST approximation). This validates coordinate_transforms.py's custom
rotation-matrix pipeline against an industry-standard reference, using the
exact same RA/Dec input so the comparison isolates the coordinate-transform
math rather than the ephemeris data itself.

Usage:
    python3 verify_iss_pointing.py [input_csv] [latitude] [longitude] [altitude_m]

If lat/lon/alt are omitted, it re-derives them the same way pointing.py
does (IP geolocation via Horizons, with the same hardcoded fallback).
"""
import sys
import os
import csv
import math

import numpy as np
import astropy.units as u
from astropy.coordinates import ICRS, AltAz, EarthLocation, SkyCoord
from astropy.time import Time

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Motor angular resolution from lktech_motor.py - used as the pass/fail
# threshold, since sub-resolution pointing error is not physically visible.
MOTOR_ANGLE_RESOLUTION_DEG = 0.4


def angular_separation_deg(az1, el1, az2, el2):
    """Great-circle separation between two (az, el) directions, degrees."""
    az1, el1, az2, el2 = map(math.radians, (az1, el1, az2, el2))
    cos_sep = (math.sin(el1) * math.sin(el2) +
               math.cos(el1) * math.cos(el2) * math.cos(az1 - az2))
    cos_sep = max(-1.0, min(1.0, cos_sep))
    return math.degrees(math.acos(cos_sep))


def get_observer_location():
    from horizons import Horizons
    h = Horizons()
    return h.get_my_latitude(), h.get_my_longitude(), h.get_my_altitude()


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else 'iss_one_orbit_commands.csv'

    if len(sys.argv) > 4:
        latitude, longitude, altitude = map(float, sys.argv[2:5])
    else:
        print("[INFO] No lat/lon/alt given; re-deriving observer location "
              "the same way pointing.py does...")
        latitude, longitude, altitude = get_observer_location()

    print("[INFO] Observer location: lat={:.6f}, lon={:.6f}, alt={:.2f}m"
          .format(latitude, longitude, altitude))

    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg,
                              height=altitude * u.m)

    with open(input_csv, newline='') as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("[ERROR] No rows in {}".format(input_csv))
        sys.exit(1)

    results = []
    for row in rows:
        t = Time(row['utc_time'], scale='utc', location=location)
        ra = float(row['ra_deg']) * u.deg
        dec = float(row['dec_deg']) * u.deg

        icrs_coord = SkyCoord(ra=ra, dec=dec, frame=ICRS())
        altaz_frame = AltAz(obstime=t, location=location)
        altaz = icrs_coord.transform_to(altaz_frame)

        az_astropy = altaz.az.deg
        el_astropy = altaz.alt.deg

        az_cmd = float(row['az_cmd_deg'])
        el_cmd = float(row['el_cmd_deg'])

        # az_cmd is unwrapped (can be outside 0-360 for continuous motion);
        # reduce to 0-360 before comparing to astropy's wrapped azimuth.
        az_cmd_wrapped = az_cmd % 360.0

        sep = angular_separation_deg(az_cmd_wrapped, el_cmd, az_astropy, el_astropy)
        az_diff = (az_cmd_wrapped - az_astropy + 180) % 360 - 180
        el_diff = el_cmd - el_astropy

        results.append({
            'utc_time': row['utc_time'],
            'az_cmd_deg': az_cmd_wrapped,
            'el_cmd_deg': el_cmd,
            'az_astropy_deg': az_astropy,
            'el_astropy_deg': el_astropy,
            'az_diff_deg': az_diff,
            'el_diff_deg': el_diff,
            'separation_deg': sep,
        })

    seps = np.array([r['separation_deg'] for r in results])
    az_diffs = np.array([r['az_diff_deg'] for r in results])
    el_diffs = np.array([r['el_diff_deg'] for r in results])

    output_csv = os.path.splitext(input_csv)[0] + '_verified.csv'
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print("\n=== Verification against astropy ICRS->AltAz ({} points) ===".format(len(results)))
    print("Total angular separation (deg): mean={:.4f}  median={:.4f}  max={:.4f}"
          .format(seps.mean(), np.median(seps), seps.max()))
    print("Azimuth diff (deg):             mean={:+.4f}  std={:.4f}  max_abs={:.4f}"
          .format(az_diffs.mean(), az_diffs.std(), np.abs(az_diffs).max()))
    print("Elevation diff (deg):           mean={:+.4f}  std={:.4f}  max_abs={:.4f}"
          .format(el_diffs.mean(), el_diffs.std(), np.abs(el_diffs).max()))

    n_over_threshold = int((seps > MOTOR_ANGLE_RESOLUTION_DEG).sum())
    print("\nPoints exceeding motor resolution ({:.1f} deg): {} / {}"
          .format(MOTOR_ANGLE_RESOLUTION_DEG, n_over_threshold, len(results)))
    if n_over_threshold == 0:
        print("PASS: all commands are within the motor's mechanical resolution of the "
              "astropy reference position.")
    else:
        print("Some points exceed the threshold - inspect {} for details.".format(output_csv))

    print("\nWrote per-point comparison to {}".format(output_csv))


if __name__ == '__main__':
    main()
