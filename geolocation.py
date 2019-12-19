import googlemaps as gms
import pandas as pd
import re
import time
import requests
import csv
from collections import Counter


def return_match(match):
    if match is None:
        return None
    return (match.group())


from collections import Counter


def remove_duplicates(apple):
    apple = apple.split(" ")
    for i in range(0, len(apple)):
        apple[i] = "".join(apple[i])
    UniqW = Counter(apple)
    s = " ".join(UniqW.keys())
    return s


def is_it_in_it(a, b):
    return (a in b)


def get_district_state(pc):
    apple = requests.get("https://api.postalpincode.in/pincode/" + pc)
    # time.sleep(1)
    return [apple.json()[0]['PostOffice'][0]["District"].upper(), apple.json()[0]['PostOffice'][0]["State"].upper()]


def filter_text(text, pincode, district, state):
    text = remove_duplicates(text)
    if is_it_in_it(district, text):
        temp = text.find(district)
        length_temp = len(district)
        text = text[0:temp] + text[temp + length_temp]
    if is_it_in_it(state, text):
        temp = text.find(state)
        length_temp = len(state)
        text = text[0:temp] + text[temp + length_temp]
    if is_it_in_it("INDIA", text):
        temp = text.find("INDIA")
        length_temp = len("INDIA")
        text = text[0:temp] + text[temp + length_temp]
    if is_it_in_it(pincode, text):
        temp = text.find(pincode)
        length_temp = len(pincode)
        text = text[0:temp] + text[temp + length_temp]
    return text + ", " + district + ", " + state + " " + pincode + ", " + "INDIA"


def csv_writer(filename, data):
    with open(filename, "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


address = pd.read_csv('addresses.csv')

address_list = []
n_rows = (address.shape[0])
for i in range(0, address.shape[0]):
    address_list.append(address.iloc[i]['address'])

temp = []
for v in address_list:
    pincode = str(return_match(re.search(r'\b\d{6}\b', v)))
    v = v.upper()
    if pincode == None:
        address = {'pincode': None, 'state': None, 'district': None, 'country': 'INDIA', 'text_address': v}
        temp.append(address)
    else:
        get_district, get_state = get_district_state(pincode)
        address = {'pincode': pincode, 'state': get_state, 'district': get_district, 'country': 'INDIA',
                   'text_address': filter_text(v, pincode, get_district, get_state)}
        temp.append(address)
address_list = temp

# key is your api key with billing enabled
gmaps = gms.Client(key=" Your_API_Key_Here")
# go to google cloud consoles to activate an API key

geocodes = [["Latitude", "Longitude"]]
for i in range(0, len(address_list)):
    search_string = address_list[i]['text_address']
    geocode_result = gmaps.geocode(search_string)
    latitude = geocode_result[0]['geometry']['location']['lat']
    longitude = geocode_result[0]['geometry']['location']['lng']
    geocodes.append([latitude, longitude])
csv_writer("geocodes.csv", geocodes)
