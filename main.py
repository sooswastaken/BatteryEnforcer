import subprocess
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer


def get_battery_percentage():
    process = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode('utf-8')
    search_str = 'InternalBattery'
    start_index = output.find(search_str) + len(search_str)
    end_index = output.find('%', start_index)
    battery_percentage = output[start_index:end_index].split()[-1]
    return int(battery_percentage)  # Convert to integer for comparison


def is_charging():
    process = subprocess.Popen(['pmset', '-g', 'batt'], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode('utf-8')
    if 'AC Power' in output or '(charging)' in output:
        return True
    elif '(discharging)' in output or 'Battery Power' in output:
        return False
    elif '(charged)' in output or 'AC Power' in output:
        return False
    else:
        return None


def get_base_folder():
    if os.name == 'nt':
        return os.path.join(os.getenv('APPDATA'), 'BatteryEnforcer')
    elif os.name == 'posix':
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'BatteryEnforcer')
    else:
        raise OSError("Unsupported operating system")


def check_battery_status():
    if get_battery_percentage() < 10 and not is_charging():
        subprocess.Popen(['pmset', 'sleepnow'])


def main():
    base_folder = get_base_folder()
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    icon_path = get_base_folder() + '/icon.png'
    if not os.path.exists(icon_path):
        subprocess.run(['curl', '-A',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                        '-o', icon_path, 'https://fastupload.io/secure/file/vgKGxO2J2z8Qn'])

    tray_icon = QSystemTrayIcon(QIcon(icon_path), app)

    menu = QMenu()
    action = QAction("Quit")
    action.triggered.connect(app.quit)
    menu.addAction(action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    # Setup timer to check battery status every minute
    timer = QTimer()
    timer.timeout.connect(check_battery_status)
    timer.start(60000)  # time in milliseconds

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
