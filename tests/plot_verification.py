"""
Plot the astropy verification results produced by verify_iss_pointing.py.

Reads a *_verified.csv (utc_time, az_cmd_deg, el_cmd_deg, az_astropy_deg,
el_astropy_deg, az_diff_deg, el_diff_deg, separation_deg) and saves plots
to artifacts/.

Usage:
    python3 tests/plot_verification.py [verified_csv]
"""
import sys
import os
import csv
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # headless-safe, no display needed
import matplotlib.pyplot as plt

MOTOR_ANGLE_RESOLUTION_DEG = 0.4
# artifacts/ lives at repo root, not tests/artifacts/
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ARTIFACTS_DIR = os.path.join(REPO_ROOT, 'artifacts')


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else 'iss_one_orbit_commands_verified.csv'

    with open(input_csv, newline='') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("[ERROR] No rows in {}".format(input_csv))
        sys.exit(1)

    t0 = datetime.fromisoformat(rows[0]['utc_time'])
    t_min = [(datetime.fromisoformat(r['utc_time']) - t0).total_seconds() / 60.0 for r in rows]
    az_cmd = [float(r['az_cmd_deg']) for r in rows]
    el_cmd = [float(r['el_cmd_deg']) for r in rows]
    az_astropy = [float(r['az_astropy_deg']) for r in rows]
    el_astropy = [float(r['el_astropy_deg']) for r in rows]
    az_diff = [float(r['az_diff_deg']) for r in rows]
    el_diff = [float(r['el_diff_deg']) for r in rows]
    separation = [float(r['separation_deg']) for r in rows]

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # 1) Total angular separation vs time, with motor resolution threshold
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(t_min, separation, color='#0ca30c', linewidth=1.8, label='Angular separation')
    ax.axhline(MOTOR_ANGLE_RESOLUTION_DEG, color='#898781', linestyle='--', linewidth=1,
               label='Motor resolution ({:.1f}°)'.format(MOTOR_ANGLE_RESOLUTION_DEG))
    ax.set_xlabel('Minutes into orbit')
    ax.set_ylabel('Angular separation (deg)')
    ax.set_title('Pointing accuracy vs astropy reference (one ISS orbit)')
    ax.legend(loc='upper right')
    ax.grid(True, linewidth=0.5, alpha=0.4)
    fig.tight_layout()
    out1 = os.path.join(ARTIFACTS_DIR, 'separation_error.png')
    fig.savefig(out1, dpi=150)
    plt.close(fig)

    # 2) Az/El component diff vs time
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    ax1.plot(t_min, az_diff, color='#2a78d6', linewidth=1.8)
    ax1.axhline(0, color='#c3c2b7', linewidth=1)
    ax1.set_ylabel('Az diff (deg)')
    ax1.set_title('Az/El command error vs astropy reference')
    ax1.grid(True, linewidth=0.5, alpha=0.4)

    ax2.plot(t_min, el_diff, color='#eb6834', linewidth=1.8)
    ax2.axhline(0, color='#c3c2b7', linewidth=1)
    ax2.set_xlabel('Minutes into orbit')
    ax2.set_ylabel('El diff (deg)')
    ax2.grid(True, linewidth=0.5, alpha=0.4)
    fig.tight_layout()
    out2 = os.path.join(ARTIFACTS_DIR, 'az_el_diff.png')
    fig.savefig(out2, dpi=150)
    plt.close(fig)

    # 3) Commanded vs reference sky track (az/el overlaid)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
    ax1.plot(t_min, [a % 360 for a in az_cmd], color='#0ca30c', linewidth=2, label='Our command')
    ax1.plot(t_min, az_astropy, color='#d03b3b', linewidth=1, linestyle='--', label='astropy reference')
    ax1.set_ylabel('Azimuth (deg)')
    ax1.set_title('Commanded vs. astropy-reference sky track')
    ax1.legend(loc='best')
    ax1.grid(True, linewidth=0.5, alpha=0.4)

    ax2.plot(t_min, el_cmd, color='#0ca30c', linewidth=2, label='Our command')
    ax2.plot(t_min, el_astropy, color='#d03b3b', linewidth=1, linestyle='--', label='astropy reference')
    ax2.set_xlabel('Minutes into orbit')
    ax2.set_ylabel('Elevation (deg)')
    ax2.legend(loc='best')
    ax2.grid(True, linewidth=0.5, alpha=0.4)
    fig.tight_layout()
    out3 = os.path.join(ARTIFACTS_DIR, 'sky_track_comparison.png')
    fig.savefig(out3, dpi=150)
    plt.close(fig)

    print("Saved plots:")
    print("  {}".format(out1))
    print("  {}".format(out2))
    print("  {}".format(out3))


if __name__ == '__main__':
    main()
