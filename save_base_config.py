from cli import cli

# save baseline running configuration

cli('configure terminal ; line vty 0 15 ; length 0 ; transport input ssh ; exit')

output = cli('show run')
filename = '/bootflash/guest-share/CONFIG_FILES/base-config'

f = open(filename, "w")
f.write(output)
f.close