__author__ = "Oren Brigg"
__author_email__ = "obrigg@cisco.com"
__copyright__ = "Copyright (c) 2020 Cisco Systems, Inc."


from cli import cli
import time
import difflib
from webexteamssdk import WebexTeamsAPI
import json

from config import *

def save_config():
    # save running configuration, use local time to create new config file name
    run = cli('show run')
    output = run[run.find('!'):len(run)]
    timestr = time.strftime('%Y%m%d-%H%M%S')
    filename = '/bootflash/guest-share/CONFIG_FILES/' + timestr + '_shrun'
    f = open(filename, 'w')
    f.write(output)
    f.close
    f = open('/bootflash/guest-share/CONFIG_FILES/current_config_name', 'w')
    f.write(filename)
    f.close
    return filename

def compare_configs(cfg1, cfg2):
    # compare two config files
    d = difflib.unified_diff(cfg1, cfg2)
    diffstr = ''
    for line in d:
        if line.find('Current configuration') == -1:
            if line.find('Last configuration change') == -1:
                if (line.find('+++') == -1) and (line.find('---') == -1):
                    if (line.find('-!') == -1) and (line.find('+!') == -1):
                        if line.startswith('+'):
                            diffstr = diffstr + '\n' + line
                        elif line.startswith('-'):
                            diffstr = diffstr + '\n' + line
    return diffstr

# main application
syslog_input = cli('show logging | in %SYS-5-CONFIG_I')
syslog_lines = syslog_input.split('\n')
lines_no = len(syslog_lines)-2
user_info = syslog_lines[lines_no]
user = user_info.split()[user_info.split().index('by')+1]

old_cfg_fn = '/bootflash/guest-share/CONFIG_FILES/base-config'
new_cfg_fn = save_config()

f = open(old_cfg_fn)
old_cfg = f.readlines()
f.close

f = open(new_cfg_fn)
new_cfg = f.readlines()
f.close

diff = compare_configs(old_cfg,new_cfg)
print (diff)

f = open('/bootflash/guest-share/CONFIG_FILES/diff', 'w')
f.write(diff)
f.close

if diff != '':
    # find the device hostname using RESTCONF
    device_name = cli('show run | inc hostname ').split()[1]
    print('Hostname: ' + device_name)
    # Initialize Webex Teams API
    api = WebexTeamsAPI(access_token=WEBEX_TEAMS_ACCESS_TOKEN, proxies=PROXY)
    bot = api.people.me()
    # Create a new space
    room = api.rooms.create(WEBEX_TEAMS_ROOM)
    # Add members to the space
    for WEBEX_TEAMS_MEMBER in WEBEX_TEAMS_MEMBERS:
        api.memberships.create(room.id,personEmail=WEBEX_TEAMS_MEMBER)
    # Send initial message
    api.messages.create(roomId=room.id, markdown=f"Hello <@all>,  \n# Configuration change detected!**  \nDevice hostname: **{device_name}**, detected the following changes made by user: **{user}**.")
    api.messages.create(roomId=room.id, text=diff)
    api.messages.create(roomId=room.id, markdown=f"Do you approve these changes?  \nMention me using **@{bot.nickName}** and enter '**y**' or '**n**'.")
    counter = 6  # wait for approval = 10 seconds * counter, in this case 10 sec x 6 = 60 seconds
    last_message = ""
    # start approval process
    while (last_message != "Bye Bye") and (last_message != f"{bot.nickName} n") and (last_message != f"{bot.nickName} y"):
        time.sleep(10)
        messages = api.messages.list(room.id, mentionedPeople=bot.id)
        for message in messages:
            last_message = message.text
            break
        print(last_message)
        if last_message == f'{bot.nickName} n':
            cli('configure replace flash:/guest-share/CONFIG_FILES/base-config force')
            approval_result = '- - -  \n<@all>,  \nConfiguration changes **not approved**, Configuration rollback to baseline'
            print('Configuration roll back completed')

        elif last_message == f'{bot.nickName} y':
            print('Configuration change approved')
            # save new baseline running configuration
            output = cli('show run')
            filename = '/bootflash/guest-share/CONFIG_FILES/base-config'
            f = open(filename, "w")
            f.write(output)
            f.close
            print('Saved new baseline configuration')
            approval_result = '- - -  \n<@all>,  \nConfiguration changes **approved**, Saved new baseline configuration'

        else:
            print("No valid response")
            counter = counter -1
            api.messages.create(roomId=room.id, markdown=f'- - -  \n<@all>, I did not receive a valid responce. **{str(counter)} attempts left**.  \nDo you approve these changes?  \nMention me using **@{bot.nickName}** and enter "**y**" or "**n**".')
            if counter == 0:
                last_message = "Bye Bye"
                cli('configure replace flash:/guest-share/CONFIG_FILES/base-config force')
                approval_result = '<@all>,  \nApproval request **timeout**, Configuration rollback to baseline'
                print('Configuration roll back completed')

    api.messages.create(roomId=room.id, markdown=approval_result)
    api.messages.create(roomId=room.id, markdown='This room will be deleted in 30 seconds')
    time.sleep(30)
    api.rooms.delete(room.id)

print('End Application Run')