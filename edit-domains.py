#!/usr/bin/env python3

import argparse, json, sys
import requests
from cfzones import UPS_IP, add_a_record

# Function to get the DNS record ID for the '@' record
def get_dns_record_id(zone_id, headers, domain_name):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    response = requests.get(url, headers=headers)
    result = response.json()
    if result['success']:
        for record in result['result']:
            print('*', record)
            if record['name'] == domain_name:
                return record['id']
    return None

# Function to delete DNS record
def delete_dns_record(zone_id, record_id, headers):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    response = requests.delete(url, headers=headers)
    return response.json()

def get_value(choice):
    return 'on' if choice>0 else 'off'
    
def get_args():
    parser = argparse.ArgumentParser(description='Modify domain configurations in bulk')
    parser.add_argument('-d', '--domain', help='the domain to target')
    parser.add_argument('--arhttps', type=int, choices=[-1, 0, 1], default=-1, help='enable/disable Automatic HTTPS Rewrites')
    parser.add_argument('--auhttps', type=int, choices=[-1, 0, 1], default=-1, help='enable/disable Always Use HTTPS')
    parser.add_argument('-x', '--proxied', choices=['Y', 'N'], help='Should the DNS record be proxied? Must be one of Y or N.')
    return parser.parse_args()

def get_domains(domain):
    if domain is None or domain == '*':
        with open('domains.txt', 'r') as f:
            domains = [line.strip().replace('https://', '') for line in f]
    else:
        domains = [domain]
    return domains

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

def get_zone_id(domain, headers):
    response = requests.get('https://api.cloudflare.com/client/v4/zones', params={'name': domain}, headers=headers)
    response.raise_for_status()
    zone_info = response.json()
    return zone_info['result'][0]['id']

def update_settings(domain, arhttps, auhttps, proxied, headers):
    zone_id = get_zone_id(domain, headers)
    if arhttps != -1:
        data = {'value': get_value(arhttps)}
        response = requests.patch(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/automatic_https_rewrites', headers=headers, json=data)
        response.raise_for_status()
        print(domain, 'arhttps', response.json())
    if auhttps != -1:
        data = {'value': get_value(auhttps)}
        response = requests.patch(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https', headers=headers, json=data)
        response.raise_for_status()
        print(domain, 'auhttps', response.json())
    if proxied:
        record_id = get_dns_record_id(zone_id, headers, domain)
        if record_id:
            delete_result = delete_dns_record(zone_id, record_id, headers)
            print("Delete Result:", delete_result)

        print(domain, add_a_record(zone_id, UPS_IP, headers))

def main():
    args = get_args()
    domains = get_domains(args.domain)
    credentials = get_credentials()
    headers = set_headers(credentials)
    for domain in domains:
        update_settings(domain, args.arhttps, args.auhttps, args.proxied, headers)

if __name__== '__main__':
    main()
