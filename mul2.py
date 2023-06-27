import concurrent.futures
import requests
import json
import itertools

valid_vpa_count = 0
invalid_vpa_count = 0
faulty_handles = []
faulty_handle_count_detct = 0

with open("refined_proxies.txt", "r") as file:
    proxies = file.read().split("\n")

with open("data/general_suffixes.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines()

header = {
    "channel-id": "WEB_UNAUTH",
    "Origin": "https://www.airtel.in",
    "Referer": "https://www.airtel.in/",
}


def address_discovery(proxy, handle):
    global valid_vpa_count, invalid_vpa_count

    try:
        response = requests.get(
            f"https://paydigi.airtel.in/web/pg-service/v1/validate/vpa/akash@{handle}",
            headers=header,
            proxies={"http": proxy, "https": proxy},
            timeout=3,
        )
        print(response.status_code)

        if response.status_code == 200:
            print(f"Proxy {proxy} working")
            json_response = response.json()

            if json_response["data"]["vpaValid"]:
                print(
                    json_response["data"]["payeeAccountName"],
                    json_response["data"]["vpa"],
                )
                name = json_response["data"]["payAccountName"]
                vpa = json_response["data"]["vpa"]
                valid_vpa_count += 1
                print(f"Valid VPA count: {valid_vpa_count}")
                with open("results.txt", "w") as f:
                    f.write(f"name={name} vpa={vpa}")
                return True
            else:
                invalid_vpa_count += 1
                print(f"Invalid VPA count: {invalid_vpa_count}")
                return True
        else:
            print(f"Proxy {proxy} not working. Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"Proxy {proxy} not working")
        return False


def process_handle(proxy_cycle, handle):
    global faulty_handle_count_detct, faulty_handles

    proxy = next(proxy_cycle)
    vpa_check = address_discovery(proxy, handle)

    if not vpa_check:
        while not vpa_check:
            print("inwhileloop")
            print(handle)
            proxy = next(proxy_cycle)
            vpa_check = address_discovery(proxy, handle)
            print(vpa_check)
            faulty_handle_count_detct += 1

            if faulty_handle_count_detct >= 20:
                faulty_handles.append(handle)
                vpa_check = True

        print("byeloop")
        faulty_handle_count_detct = 0


def main():
    global faulty_handles

    proxy_cycle = itertools.cycle(proxies)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for handle in upi_suffix_dict:
            executor.submit(process_handle, proxy_cycle, handle)

    print(f"Invalid VPA count: {invalid_vpa_count}")
    print(f"Valid VPA count: {valid_vpa_count}")
    print(f"Faulty handles: {faulty_handles}")

    with open("faulty_handlesfor_car", "w") as f:
        f.write("\n".join(faulty_handles))


if __name__ == "__main__":
    main()
