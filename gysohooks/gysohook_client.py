import run_argv_parse
import webbrowser
import adb_local_exe


if __name__ == '__main__':
    p_argvs = run_argv_parse.cmd_parse()
    status = adb_local_exe.check_evn()
    host = p_argvs['host']
    action = p_argvs['action']
    proxyport = p_argvs['proxyport']
    heartbeat = p_argvs['heartbeat']

    adb_local_exe.set_app_evn(action, host, proxyport, heartbeat)
    if proxyport == 8080:
        webbrowser.open(f"http://{host}:{5000}")


