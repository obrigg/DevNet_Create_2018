import requests
from config import SPARK_URL, SPARK_AUTH, SPARK_ROOM, SPARK_MEMBERS
requests.packages.urllib3.disable_warnings()      # Disable warnings. Living on the wild side..

def delete_room(room_id):
    # delete room with the room id
    url = SPARK_URL + '/rooms/' + room_id
    header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
    requests.delete(url, headers=header, verify=False)
    print('\nDeleted Spark Team :  ', room_id)

# Manually enter a token
token = input("Enter the bot's token: ")
SPARK_AUTH = 'Bearer ' + token

# Get list of rooms
url = SPARK_URL + '/rooms/'
header = {'content-type': 'application/json', 'authorization': SPARK_AUTH}
res = requests.get(url=url, headers=header, verify=False)
rooms = res.json()['items']

# Delete the rooms on the list
for room in rooms:
    delete_room(room['id'])
