#!/usr/bin/env python3

"""
cfzones.py

检查需要加入的域名，是否为二级域名，如果是，则按照原有逻辑直接加入。

如果不是，把二级域名提取出来加入 Cloudflare 的 zone，并将 '@' 解析替换为域名的前缀。

如:
user.example.com {ip}

调用:
add_domain('example.com', {ip})
add_a_record(zone_id, ip_address, headers, 'user') 此函数增加一个参数name, 默认为 '@'
"""

import argparse, json, sys, requests
from utils import get_second_level_domain


# Check Python version
if not sys.version_info >= (3, 6):
    print('Python 3.6 or later is required to run this script.')
    sys.exit(1)

def get_args():
    parser = argparse.ArgumentParser(description='Add domains to Cloudflare')
    parser.add_argument('-i', '--ip', help='the IP address to use for the A record')
    return parser.parse_args()

try:
    import requests
except ImportError as e:
    print('Please install the \'requests\' library using \'pip install requests\'')
    sys.exit(1)

def get_credentials():
    try:
        with open('auth.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError as e:
        sys.exit(e)

def set_headers(credentials):
    headers = {
        'Authorization': 'Bearer ' + credentials['cloudflare']['token'],
        'Content-Type': 'application/json'
    }
    return headers

def add_domain(domain, headers):
    url = 'https://api.cloudflare.com/client/v4/zones'
    data = {
        'name': domain,
        'jump_start': True
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def add_a_record(zone_id, ip_address, headers, name='@'):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    data = {
        'type': 'A',
        'name': name,
        'content': ip_address,
        'ttl': 120,
        'proxied': True
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    UPS_IP = '47.251.0.62'
    args = get_args()
    ip_address = args.ip if args.ip else UPS_IP

    credentials = get_credentials()
    headers = set_headers(credentials)
    
    with open('domains.txt', 'r') as f:
        for line in f:
            domain = line.strip()
            if domain[:8] == 'https://':
                domain = domain[8:]
            zone = add_domain(domain, headers)
            if zone["success"]:
                zone_id = zone['result']['id']
                print(domain, '->', json.dumps(zone['result']['name_servers'], indent=4))
                print(domain, '->', add_a_record(zone_id, ip_address, headers))
            else:
                print('Failed:', domain, json.dumps(zone, indent=4))
if __name__== '__main__' :
    main()
