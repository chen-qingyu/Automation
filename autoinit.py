# FileName: autoinit.py
# Brief: Python3 script for automating initialize the system environment.
# Author: Qing Yu
# CreateDate: 2023.09.27

import os
import sys
import platform
import importlib
import webbrowser
import tomllib
import argparse

# check version
if not (sys.version_info.major == 3 and sys.version_info.minor >= 12):
    print("Require at least Python >= 3.12")
    exit(1)


with open('autoinit.toml', 'rb') as f:
    DATA: dict = tomllib.load(f)
    LIBS: list[str, ...] = DATA['libraries']
    APPS: list[dict, ...] = DATA['applications']

DOWNLOAD = './Download/'


def main():
    # parse command
    parser = argparse.ArgumentParser(prog="autoinit", description="Python3 script for automating initialize the system environment.")
    parser.add_argument("action", type=str, help="Action", choices=['lib', 'app', 'all'])
    parser.add_argument("name", type=str, help="Python library name or application name", nargs='?', default='')
    args = parser.parse_args()

    global COLOR_START, COLOR_INFO, COLOR_FINISH, COLOR_ERROR
    COLOR_START, COLOR_INFO, COLOR_FINISH, COLOR_ERROR = '', '', '', ''

    print("Start upgrade pip tools.")
    install_lib(['pip', 'setuptools', 'wheel'])
    print("Finish upgrade pip tools.")

    print("Start dynamically load third-party libraries.")
    install_lib(['colorama', 'requests', 'tqdm'])
    global colorama, requests, tqdm
    colorama = importlib.import_module('colorama')
    requests = importlib.import_module('requests')
    tqdm = importlib.import_module('tqdm')
    print("Finish dynamically load third-party libraries.")

    print("Start colorize.")
    colorama.init(autoreset=True)
    COLOR_START = colorama.Fore.BLUE + colorama.Style.BRIGHT
    COLOR_INFO = colorama.Fore.CYAN + colorama.Style.BRIGHT
    COLOR_FINISH = colorama.Fore.GREEN + colorama.Style.BRIGHT
    COLOR_ERROR = colorama.Fore.RED + colorama.Style.BRIGHT
    print(COLOR_FINISH + "Finish colorize.")

    print(COLOR_START + "Checking platform...")
    if platform.system() != 'Windows':
        print(COLOR_ERROR + "This script currently only supports the Windows platform.\n")
        exit(-1)
    print(COLOR_FINISH + "OK.")

    print(COLOR_START + "Checking download folder...")
    if not os.path.exists(DOWNLOAD):
        os.mkdir(DOWNLOAD)
        print(COLOR_INFO + f"Created: {DOWNLOAD}")
    print(COLOR_FINISH + "OK.")

    # process command
    if args.action == 'lib':
        install_lib(LIBS if args.name == '' else [args.name])
    elif args.action == 'app':
        install_app(APPS if args.name == '' else list(filter(lambda app: app['name'].lower() == args.name.lower(), APPS)))
    else:
        install_lib(LIBS)
        install_app(APPS)


def install_lib(libs: list[str, ...]):
    print(COLOR_START + f"Start install/upgrade libraries: {', '.join(libs)}")
    os.system(f'python -m pip install --upgrade --index-url https://pypi.tuna.tsinghua.edu.cn/simple {' '.join(libs)}')
    os.system('python -m pip cache purge')
    print(COLOR_FINISH + f"Finish install/upgrade libraries: {', '.join(libs)}")


def install_app(apps: list[dict, ...]):
    for i, app in zip(range(len(apps)), apps):
        print(COLOR_START + f"({i + 1}/{len(apps)}) Start download/install {app['name']}...")

        match app['method']:
            case 'automatic':
                install(app)
            case 'manual':
                webbrowser.open(app['download_link'])
                input(COLOR_INFO + f"Please download and install {app['name']} manually.")
            case 'winget':
                print(COLOR_INFO + f"Installing {app['name']} using winget...")
                os.system('winget install ' + app['id'])
                print(COLOR_INFO + f"Installed {app['name']} using winget.")
            case _:
                print(COLOR_ERROR + "Error: Wrong method.")

        print(COLOR_FINISH + f"Finish download/install {app['name']}.\n")


def install(app: dict):
    print(COLOR_INFO + f"Installing {app['name']}...")
    file_name = app['download_url'].split('/')[-1]
    response = requests.get(app['download_url'], stream=True)
    length = int(response.headers.get('content-length', 0))
    with open(DOWNLOAD + file_name, 'wb') as fo, tqdm.tqdm(desc=file_name, total=length, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = fo.write(data)
            bar.update(size)
    os.system(f'PowerShell {DOWNLOAD + file_name} {app['install_args']}')
    input(COLOR_INFO + "Wait for the installation to complete.")
    print(COLOR_INFO + f"Installed {app['name']}.")


if __name__ == '__main__':
    main()
