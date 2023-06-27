import requests
import itertools
with open("refined_proxies.txt", "r") as f:
    proxies = f.read().split("\n")
header ={
                    "channel-id": "WEB_UNAUTH",
                    "Origin": "https://www.airtel.in",
                    "Referer": "https://www.airtel.in/",
                }
def check_proxies(proxy):
    try: 
        response = requests.get(f"https://paydigi.airtel.in/web/pg-service/v1/validate/vpa/akash@yesbank", 
        headers= header,
        proxies={'http': proxy, 'https': proxy}, 
        timeout=3)
        print(response.status_code)
        if response.status_code==200:
            print(f"Proxy{proxy} working")
            return True
    except requests.exceptions.RequestException:
        print(f"Proxy{proxy} not working")
        return False
def main():
    success_proxies=[]
    results = {proxy: {'success': 0, 'failure': 0} for proxy in proxies}
    proxy_cycle= itertools.cycle(proxies)
    for i in range(len(proxies)*5):
        proxy= next(proxy_cycle)
        vpa_check=check_proxies(proxy)
        if vpa_check==True:
            results[proxy]['success'] += 1
            with open("good-proxies.txt", 'a') as file:
                file.write(proxy+"\n")
        else:
            results[proxy]['failure'] += 1
    print(results)
    for proxy ,counts in results.items():
        if counts['success'] >3:
            success_proxies.append(proxy)
    print(success_proxies)



main()