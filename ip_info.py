import requests

ip_api_url = "https://api.devjugal.com/ip-info?user_ip=1.1.1.56"
ip_response = requests.get(ip_api_url)
print(ip_response.text)