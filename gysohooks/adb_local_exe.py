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


def reverse_tcp(proxyport):
    output: tuple = subprocess.getstatusoutput(f'adb reverse tcp:{proxyport} tcp:{proxyport}')
    print(output)


def send_broadcast_cmd(action, host, proxyport, heartbeat):
    """
     adb shell am broadcast  -f 0x01000000  -c desaysv.intent.gysohook -a intent.action.start --es hostname 127.0.0.1 --ei port 8080  --ez heartbeat true
     adb shell am broadcast  -f 0x01000000  -c desaysv.intent.gysohook -a intent.action.start --es hostname www.xxxx.com
     adb shell am broadcast  -f 0x01000000  -c desaysv.intent.gysohook -a intent.action.start

     if localhost
        adb reverse tcp:8080 tcp:8080
     [stop hook]
    adb shell am broadcast  -f 0x01000000  -c desaysv.intent.gysohook -a intent.action.stop
    """
    cmd = f"""
        adb shell am broadcast  -f 0x01000000  -c desaysv.intent.gysohook -a intent.action.{action} --es hostname {host} --ei port {proxyport}  --ez heartbeat {heartbeat}
    """
    output = os.system(cmd)
    print("finish broadcast", output)


def check_evn():
    is_adb_exist()
    get_devices()
    print("adb check evn finished")
    return None


def is_local(host: str):
    return "127.0.0.1" == host.strip() or "localhost" == host.strip()


def set_app_evn(action='start', host='127.0.0.1', proxyport=8080, heartbeat=False):
    if is_local(host):
        reverse_tcp(proxyport)
    send_broadcast_cmd(action, host, proxyport, heartbeat)
    print(f"adb set_app_evn finished, is local[{is_local}]action[{action}]"
          f"host[{host}]proxyport[{proxyport}]heartbeat[{heartbeat}]")
