import re
import subprocess
import os


def is_adb_exist() -> bool:
    try:
        subprocess.run('adb --version')
    except FileNotFoundError as e:
        print(e)
        return False
    return True


def get_devices() -> []:
    result = {}
    try:
        output: tuple = subprocess.getstatusoutput('adb devices -l')
        print(output)
        if len(output) > 1:
            print(output[0], output[1])
            if output[0] == 0:
                raw = output[1].replace("List of devices attached\n", '')
                if len(raw) > 8:
                    sub = raw.split("\n")
                    for item in sub:
                        print(item)
                        h = item.split("           ")
                        if len(h) == 2:
                            result[h[0].strip()] = h[1].strip()
        print(result)
    except FileNotFoundError as e:
        print(e)
    finally:
        return result


def reverse_tcp():
    output: tuple = subprocess.getstatusoutput('adb reverse tcp:8080 tcp:8080')
    print(output)


def send_broadcast_cmd():
    cmd = """
        adb shell am start -n 'com.desaysv.dsvcarsettings/com.desaysv.dsvcarsettings.CarSettingsActivity' -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
    """
    output = os.system(cmd)
    print("finish broadcast", output)


def check_evn():
    is_adb_exist()
    get_devices()
    print("adb check evn finished")
    return None


def set_app_evn(is_local=True):
    if is_local:
        reverse_tcp()
    send_broadcast_cmd()
    print(f"adb set_app_evn finished, is local [{is_local}]")
    return None