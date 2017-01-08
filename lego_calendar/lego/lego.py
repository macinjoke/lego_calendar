import os


def alert(alert_case):
    if alert_case == 0:
        os.system('echo 0 > /sys/class/gpio/gpio21/value')
    elif alert_case == 1:
        os.system('echo 1 > /sys/class/gpio/gpio21/value')
    elif alert_case == 2:
        os.system('echo 1 > /sys/class/gpio/gpio21/value')
    elif alert_case == 3:
        os.system('echo 1 > /sys/class/gpio/gpio21/value')
