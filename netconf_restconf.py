

# developed by Gabi Zapodeanu, TSA, Global Partner Organization


import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth  # for Basic Auth
from config import HOST, PORT, USER, PASS, EXT_HOST

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable insecure https warnings


ROUTER_AUTH = HTTPBasicAuth(USER, PASS)

def pprint(json_data):

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))

def get_restconf_int_oper_data(interface):

    url = 'https://' + EXT_HOST + '/restconf/data/interfaces-state/interface=' + interface
    print(url)
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.get(url, headers=header, verify=False, auth=ROUTER_AUTH)
    interface_info = response.json()
    oper_data = interface_info['ietf-interfaces:interface']
    return oper_data


def get_restconf_hostname():

    url = 'https://' + EXT_HOST + '/restconf/data/Cisco-IOS-XE-native:native/hostname'
    header = {'Content-type': 'application/yang-data+json', 'accept': 'application/yang-data+json'}
    response = requests.get(url, headers=header, verify=False, auth=ROUTER_AUTH)
    hostname_json = response.json()
    hostname = hostname_json['Cisco-IOS-XE-native:hostname']
    return hostname

pprint(get_restconf_int_oper_data('GigabitEthernet1'))

print('Device Hostname via RESTCONF: ', get_restconf_hostname())