import sys
import argparse
import re


def is_ip_port_pattern(address):
    ip_port_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$'
    return re.match(ip_port_pattern, address)


def validate_address(address):
    ip_port_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$'
    domain_pattern = r'^[a-zA-Z0-9]+([-.][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:\d+)?$'
    localhost_pattern = r'localhost(:\d+)?$'

    if re.match(ip_port_pattern, address) or re.match(domain_pattern, address) or re.match(localhost_pattern, address):
        return True
    else:
        return False


def cmd_parse():
    """
        python gysohook_client.py --action start --host 127.0.0.1 --proxyport 8080 --heartbeat true
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str)
    parser.add_argument('--action', type=str)
    parser.add_argument('--proxyport', type=int)
    parser.add_argument('--heartbeat', type=str)

    args = parser.parse_args()
    host: str = args.host
    action: str = args.action
    proxyport: int = args.proxyport
    heartbeat: bool = args.heartbeat

    if host is None or not validate_address(host):
        host = '127.0.0.1'

    if action is not None and 'stop' == action.strip():
        action = 'stop'
    else:
        action = 'start'

    if proxyport is None or proxyport < 0 or proxyport > 0xFFFF:
        proxyport = 8080

    heartbeat = heartbeat is not None and heartbeat

    return {
            'host': host,
            'action': action,
            'proxyport': proxyport,
            'heartbeat': heartbeat
        }


