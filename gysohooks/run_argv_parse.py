import sys
import argparse
import re


def validate_address(address):
    ip_port_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'
    domain_pattern = r'^[a-zA-Z0-9]+([-.][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:\d+)?$'

    if re.match(ip_port_pattern, address) or re.match(domain_pattern, address):
        return True
    else:
        return False


def cmd_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    args = parser.parse_args()
    url = args.url
    print(f'find remote url  {args.url}')
    if url is None or url == "":
        return {
            'url': 'localhost'
        }
    elif validate_address(args.url):
        return {
            'url': url
        }
    else:
        print(
            f"{url} is an invalid address, your cmd should looks like "
            f"'gysohooks --url 10.12.11.89:5000   or  gysohooks --url www.xxx.com  or  "
            f"gysohooks'")
