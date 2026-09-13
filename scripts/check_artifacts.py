"""Validate an installed wheel and optionally a native bundle outside checkout."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv

parser = argparse.ArgumentParser()
parser.add_argument('--wheel', type=Path)
parser.add_argument('--desktop', type=Path)
args = parser.parse_args()
if not args.wheel and not args.desktop:
    parser.error('Pass --wheel and/or --desktop')
environment = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QPA_PLATFORMTHEME='generic')
environment.pop('PYTHONPATH', None)
with tempfile.TemporaryDirectory(prefix='feedio-artifacts-') as temporary:
    directory = Path(temporary)
    commands = []
    if args.wheel:
        env = directory / 'venv'
        venv.EnvBuilder(with_pip=True).create(env)
        python = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        subprocess.run([str(python), '-m', 'pip', 'install', str(args.wheel.resolve())], check=True,
                       cwd=directory, env=environment)
        commands.append([str(python), '-m', 'feedio'])
        acceptance = Path(__file__).resolve().with_name('accept_desktop.py')
        subprocess.run([str(python), str(acceptance), '--installed', '--software-rendering'],
                       cwd=directory, env=environment, check=True, timeout=180)
    if args.desktop:
        commands.append([str(args.desktop.resolve())])
    for index, command in enumerate(commands):
        profile = str(directory / f'profile-සිංහල-{index}')
        for options in (['--check'], ['--smoke-test', '--software-rendering']):
            subprocess.run(command + ['--profile', profile] + options, cwd=directory,
                           env=environment, check=True, timeout=45)
    print('Installed artifact initialization, Unicode profile, browser, icons and shutdown passed')
