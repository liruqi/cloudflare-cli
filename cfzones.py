#!/usr/bin/env python3

import json, sys, requests

UPS_IP = '47.251.0.62'

# Check Python version
if not sys.version_info >= (3, 6):
    print('Python 3.6 or later is required to run this script.')
    sys.exit(1)

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

def add_a_record(zone_id, ip_address, headers):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    data = {
        'type': 'A',
        'name': '@',
        'content': ip_address,
        'ttl': 120,
        'proxied': True
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    credentials = get_credentials()
    headers = set_headers(credentials)
    
    with open('domains.txt', 'r') as f:
        for line in f:
            domain = line.strip()
            if domain[:8] == 'https://':
                domain = domain[8:]
            zone = add_domain(domain, headers)
            zone_id = zone['result']['id']
            print(domain, '->', json.dumps(zone, indent=4))
            print(domain, '->', add_a_record(zone_id, UPS_IP, headers))

if __name__== '__main__' :
    main()
