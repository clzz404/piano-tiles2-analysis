"""Call the observed reward receiver on an authorized Piano Tiles 2 device."""

import argparse
import json
import shlex
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--type', required=True, choices=('gold', 'diamond'))
    parser.add_argument('--amount', required=True, type=int, help='Positive amount to add')
    parser.add_argument('--serial', help='ADB device serial; optional when only one device is connected')
    parser.add_argument('--adb', default='adb', help='Path to adb executable')
    args = parser.parse_args()
    if not 1 <= args.amount <= 10000:
        parser.error('--amount must be between 1 and 10000')

    reward_type = {'diamond': 1, 'gold': 2}[args.type]
    payload = json.dumps({'type': reward_type, 'num': args.amount}, separators=(',', ':'))
    shell_command = (
        'am broadcast '
        '-a com.cmplay.webview.broadcast.gamebroadcast '
        '-n com.cmplay.tiles2_newest/com.cmplay.webview.broadcast.GameBroadcast '
        '--ez send_prize_boolean true '
        '--es send_prize_number ' + shlex.quote(payload)
    )
    command = [args.adb]
    if args.serial:
        command += ['-s', args.serial]
    command += ['shell', shell_command]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
