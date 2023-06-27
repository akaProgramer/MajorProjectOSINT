import threading
import requests
import json
import itertools

valid_vpa_count=0
invalid_vpa_count=0
faulty_handles=[]
faulty_handle_count_detct=0
with open("refined_proxies.txt", "r") as file:
    proxies = file.read().split("\n")

with open("data/general_suffixes.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines()
print(upi_suffix_dict)
header ={
                    "channel-id": "WEB_UNAUTH",
                    "Origin": "https://www.airtel.in",
                    "Referer": "https://www.airtel.in/",
                }
def addres_discvry(proxy,handle):
       global valid_vpa_count,invalid_vpa_count
       try: 
            response = requests.get(f"https://paydigi.airtel.in/web/pg-service/v1/validate/vpa/netc.up80fz1295@{handle}", 
                                    headers= header,
                                    proxies={'http': proxy, 'https': proxy}, 
                                    timeout=3)
            print(response.status_code)
            if response.status_code==200:
                print(f"Proxy{proxy} working")
                json_response = response.json()
                if json_response["data"]["vpaValid"] == True:
                    print(
                        json_response["data"]["payeeAccountName"],
                        json_response["data"]["vpa"],
                    )
                    name=json_response["data"]["payAccountName"]
                    vpa=json_response["data"]["vpa"]
                    valid_vpa_count+=1
                    print(f"valid {valid_vpa_count},handle")
                    with open("results.txt", "w") as f:
                        f.write(f"name={name} vpa={vpa}")
                    return True
                elif json_response["data"]["vpaValid"] == False:
                    invalid_vpa_count+=1
                    print(f"invalid vpa {invalid_vpa_count},handle")
                    return True
            
                # return 200
            else:
                 print(f"Proxy{proxy} not working status: {response.status_code}")
                 print("nothing")
                 return False
       except requests.exceptions.RequestException:
            print(f"Proxy{proxy} not working")
            return False
def main():
    global faulty_handle_count_detct,faulty_handles
    proxy_cycle= itertools.cycle(proxies)
    for handle in upi_suffix_dict:
        proxy= next(proxy_cycle)
        vpa_check=addres_discvry(proxy,handle)
        if vpa_check == False:
            while vpa_check ==False:
                print("inwhileloop")
                print(handle)
                proxy= next(proxy_cycle)
                vpa_check=addres_discvry(proxy,handle)
                print(vpa_check)
                faulty_handle_count_detct+=1
                if faulty_handle_count_detct>=20:
                    faulty_handles.append(handle)
                    vpa_check=True
            print("byeloop")
            faulty_handle_count_detct=0
    print(f"invalid_vpa_count{invalid_vpa_count}")
    print(f"valid_vpa_count{valid_vpa_count}")
    print(f"faulty_handles:{faulty_handles}")
    with open("faulty_handlesfor_car","w") as f:
        for faulty_handle in faulty_handles:
            f.write(faulty_handle)

# for _ in range(2):
#     threading.Thread(target=main).start()
main()