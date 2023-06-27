import ast
import os

q_city= "up-80"
found= False
with open(os.path.join(os.getcwd(),"data\\rto_codes.txt"), 'r') as apps_file:
            rto_code_list=ast.literal_eval(apps_file.read())


for states,cities in rto_code_list.items():
        for city in cities:
                if q_city in city:
                        city=city.split(":")
                        print(f"{city[1]}")
                        found= True
                        break
if not found:
        print(f"{q_city} not found")

