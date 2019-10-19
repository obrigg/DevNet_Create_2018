

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

pprint(get_restconf_int_oper_data('GigabitEthernet1%2F0%2F1'))

print('Device Hostname via RESTCONF: ', get_restconf_hostname())

"""
This section is an example of NETCONF Requests, DO NOT CHANGE THIS!

import ncclient
import xml
import xml.dom.minidom

from ncclient import manager

def get_netconf_int_oper_status(interface):

    with manager.connect(host=HOST, port=PORT, username=USER,
                         password=PASS, hostkey_verify=False,
                         device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        # XML filter to issue with the get operation
        # IOS-XE 16.6.2+        YANG model called "ietf-interfaces"

        interface_state_filter = '''
                                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                                            <interface>
                                                <name>''' + interface + '''</name>
                                                <oper-status/>
                                            </interface>
                                        </interfaces-state>
                                    </filter>
                                '''

        result = m.get(interface_state_filter)
        xml_doc = xml.dom.minidom.parseString(result.xml)
        int_info = xml_doc.getElementsByTagName('oper-status')
        try:
            oper_status = int_info[0].firstChild.nodeValue
        except:
            oper_status = 'unknown'
        return oper_status

def get_netconf_hostname():

    with manager.connect(host=HOST, port=PORT, username=USER,
                         password=PASS, hostkey_verify=False,
                         device_params={'name': 'default'},
                         allow_agent=False, look_for_keys=False) as m:
        # XML filter to issue with the get operation
        # IOS-XE 16.6.2+        YANG model called "Cisco-IOS-XE-native"

        hostname_filter = '''
                                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                                    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                                        <hostname/>
                                    </native>
                                </filter>
                          '''

        result = m.get(hostname_filter)
        xml_doc = xml.dom.minidom.parseString(result.xml)
        int_info = xml_doc.getElementsByTagName('hostname')
        try:
            hostname = int_info[0].firstChild.nodeValue
        except:
            hostname = 'unknown'
        return hostname

"""
