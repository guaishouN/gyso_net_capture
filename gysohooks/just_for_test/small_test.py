import re

def validate_address(address):
    ip_port_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$'
    domain_pattern = r'^[a-zA-Z0-9]+([-.][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:\d+)?$'

    if re.match(ip_port_pattern, address) or re.match(domain_pattern, address):
        return True
    else:
        return False

# 测试地址
addresses = ['192.168.0.1:8080', 'www.example.com', 'invalid_address', '127.0.0.1', 'test@example.com']

for address in addresses:
    if validate_address(address):
        print(f"{address} is a valid address")
    else:
        print(f"{address} is an invalid address")