import requests
import json
print("--------------------------------------")
#change for your API KEY
url = 'http://apilayer.net/api/validate?access_key=63c060ca3ee86d8b9644bef09e4a598f&number=+919540608104'
response = requests.get(url)
answer = response.json()

if answer["valid"] == True:
    #print(answer)
    print("Number:",answer["number"])
    print("International format:",answer["international_format"])
    print("Country prefix:",answer["country_prefix"])
    print("Country name:",answer["country_name"])
    print("Location:",answer["location"])
    print("Carrier:",answer["carrier"])
    print("Line type:",answer["line_type"])
else:
    print("not a valid number")