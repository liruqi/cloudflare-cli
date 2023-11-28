#!/usr/bin/env python3

import argparse, json, sys
import requests

def get_args():
    parser = argparse.ArgumentParser(description='Modify domain configurations in bulk')
    parser.add_argument('-d', '--domain', required=True, help='the domain to target')
    parser.add_argument('--arhttps', type=int, choices=[0, 1], help='enable/disable Automatic HTTPS Rewrites')
    parser.add_argument('--auhttps', type=int, choices=[0, 1], help='enable/disable Always Use HTTPS')
    return parser.parse_args()

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

def update_settings(domain, arhttps, auhttps, headers):
    zone_id = get_zone_id(domain, headers)
    data = {
        'always_use_https': bool(auhttps),
        'automatic_https_rewrites': bool(arhttps)
    }
    response = requests.patch(f'https://api.cloudflare.com/client/v4/zones/{zone_id}/settings', headers=headers, json=data)
    response.raise_for_status()

def main():
    args = get_args()
    credentials = get_credentials()
    headers = set_headers(credentials)
    update_settings(args.domain, args.arhttps, args.auhttps, headers)

if __name__== '__main__':
    main()