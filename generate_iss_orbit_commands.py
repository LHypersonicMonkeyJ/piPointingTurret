"""
Generate example Az/El pointing commands for the ISS over one orbit.

This fetches a fine-resolution (15s step) Horizons ephemeris for the ISS
covering ~1 orbital period, then runs it through the *exact same*
AzEl/CoordinateTransforms pipeline pointing.py uses, and writes the
resulting commands to a CSV for offline accuracy analysis.

Note: this writes to its own file (ephemeris/test_iss_one_orbit.txt) and
does NOT touch ephemeris/id-125544_<date>.txt, which is the live cache
pointing.py uses during normal operation.

Usage:
    python3 generate_iss_orbit_commands.py [output_csv]
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone
import csv

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from horizons import Horizons
from az_el import AzEl

ISS_COMMAND_ID = '-125544'
ISS_ORBITAL_PERIOD_MIN = 92.68  # approximate, varies slightly with altitude/decay
FETCH_MARGIN_MIN = 10  # extra time on each end so interpolation never runs out of data
# az_el.py's ephemeris parser only understands '%Y-%b-%d %H:%M' (no seconds), so
# the fetch step must land on whole minutes - a bare step count (e.g. N equal
# steps) produces fractional-minute timestamps that silently fail to parse.
STEP_SIZE = "'1m'"

EPHEMERIS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'ephemeris', 'test_iss_one_orbit.txt')
SAMPLE_INTERVAL_SEC = 15  # how often to sample AzEl for the output command list


def fetch_fine_resolution_ephemeris(longitude, latitude, altitude):
    """Fetch a fine-step ISS ephemeris covering one orbit + margin, independent
    of Horizons.request_ephemeris (which caches to the live daily file)."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=FETCH_MARGIN_MIN)
    stop = now + timedelta(minutes=ISS_ORBITAL_PERIOD_MIN + FETCH_MARGIN_MIN)

    site_coord = "{:.8f},{:.8f},{:.8f}".format(longitude, latitude, altitude * 1e-3)
    params = {
        'format': 'json',
        'EPHEM_TYPE': 'OBSERVER',
        'OBJ_DATA': 'NO',
        'COMMAND': ISS_COMMAND_ID,
        'START_TIME': "'{}'".format(start.strftime('%Y-%b-%d %H:%M')),
        'STOP_TIME': "'{}'".format(stop.strftime('%Y-%b-%d %H:%M')),
        'STEP_SIZE': STEP_SIZE,
        'CENTER': 'coord@399',
        'SITE_COORD': "'{}'".format(site_coord),
        'OUT_UNITS': 'KM-S',
        'REF_SYSTEM': 'ICRF',
        'REF_PLANE': 'FRAME',
        'CSV_FORMAT': 'YES',
        'TIME_TYPE': 'UT',
    }

    print("[INFO] Requesting ISS ephemeris at {} steps from {} to {} UTC..."
          .format(STEP_SIZE, start, stop))
    response = requests.get('https://ssd.jpl.nasa.gov/api/horizons.api', params=params, timeout=30)
    data = json.loads(response.text)

    if response.status_code != 200 or 'signature' not in data:
        print("[ERROR] Horizons request failed: {}".format(json.dumps(data, indent=2)))
        sys.exit(1)

    os.makedirs(os.path.dirname(EPHEMERIS_PATH), exist_ok=True)
    with open(EPHEMERIS_PATH, 'w') as f:
        f.write(data['result'])
    print("[INFO] Wrote fine-resolution ephemeris to {}".format(EPHEMERIS_PATH))
    return start, stop


def main():
    output_csv = sys.argv[1] if len(sys.argv) > 1 else 'iss_one_orbit_commands.csv'

    # Reuse Horizons only for observer location (IP geolocation + fallback)
    horizons = Horizons()
    longitude = horizons.get_my_longitude()
    latitude = horizons.get_my_latitude()
    altitude = horizons.get_my_altitude()
    print("[INFO] Observer location: lat={:.5f}, lon={:.5f}, alt={:.2f}m"
          .format(latitude, longitude, altitude))

    orbit_start, orbit_end = fetch_fine_resolution_ephemeris(longitude, latitude, altitude)

    # Run through the exact same pipeline pointing.py uses
    az_el = AzEl(EPHEMERIS_PATH, latitude, longitude)

    rows = []
    t = orbit_start
    real_orbit_end = orbit_start + timedelta(minutes=ISS_ORBITAL_PERIOD_MIN)
    while t <= real_orbit_end:
        # Use a naive UTC datetime to match how ephemeris timestamps are parsed
        t_naive = t.replace(tzinfo=None)
        ok = az_el.get_az_el(t_naive)
        if ok:
            rows.append({
                'utc_time': t_naive.isoformat(),
                'ra_deg': az_el.current_ra,
                'dec_deg': az_el.current_dec,
                'az_cmd_deg': az_el.current_azimuth,
                'el_cmd_deg': az_el.current_elevation,
                'az_rate_dps': az_el.current_azimuth_rate,
                'el_rate_dps': az_el.current_elevation_rate,
            })
        t += timedelta(seconds=SAMPLE_INTERVAL_SEC)

    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("[INFO] Wrote {} commands over one ISS orbit ({:.2f} min) to {}"
          .format(len(rows), ISS_ORBITAL_PERIOD_MIN, output_csv))
    print("[INFO] Observer: lat={:.6f} lon={:.6f} alt={:.2f}m (needed for verification step)"
          .format(latitude, longitude, altitude))


if __name__ == '__main__':
    main()
