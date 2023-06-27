import pandas as pd 
import tkinter as rw
from tkinter import messagebox
import customtkinter as ctk
from tkinter import ttk
import threading
import requests
from time import sleep
from sys import exit
from random import uniform as rand
import regex as re
import socket
import os
import ast
import itertools


API_URL = 'https://paydigi.airtel.in/web/pg-service/v1/validate/vpa/'
header = {
                "channel-id": "WEB_UNAUTH",
                "Origin": "https://www.airtel.in",
                "Referer": "https://www.airtel.in/",
            }
with open("refined_proxies.txt", "r") as f:
    proxies = f.read().split("\n")
with open("data/general_suffixes.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines()
class App(rw.Tk):
    def __init__(self):
        self.found = 0
        self.count = 0
        super().__init__()
        self.geometry("600x700+300+2")
        self.title("OSINT TOOL")
        self.open_files()
        # self.wm_iconbitmap("images\me_icon.ico")
        ctk.set_appearance_mode("light")
        self.proxy_cycle= itertools.cycle(proxies)

    def check_internet(self):
        try:
            socket.create_connection(("1.1.1.1",53))
            return True
        except OSError:
            pass
        return False
       
    def start_operation(self,searchtext):
        self.index=0
        self.progressbar_percent.configure(text="0%")
        self.progressbar['value'] = 0
        self.searched_string.configure(text=searchtext)
        self.status_bar.configure(text="")
        self.export_button.configure(state=rw.DISABLED)
        self.delete_records()
        t= threading.Thread(target=self.searchvpa,args=(searchtext,upi_suffix_dict))
        t.start()

    def textget(self):
        text= self.search_bar.get()
        self.progressbar['value'] = 0
        self.progressbar_percent.configure(text="0%")
        email_pattern= r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        car_no_pattern1= r'^[A-Za-z]{2}[ -][0-9]{1,2}[a-zA-z](?: [A-Za-z])?(?: [A-Za-z]*)? [0-9]{4}$'
        car_no_pattenn2= r'^[A-Za-z]{2}[ -][0-9]{1,2}(?: [A-Za-z])?(?: [A-Za-z]*)? [0-9]{4}$'
        number_pattern= r'^[6-9]\d{9}$'
        if (re.fullmatch(email_pattern,text)):
            email=text.split("@")
            email_text= email[0]
            self.start_operation(email_text)
        elif (re.fullmatch(car_no_pattern1,text) or re.fullmatch(car_no_pattenn2,text)):
            rto_code_spliting=(text.split(" "))
            rto_code=(rto_code_spliting[0]+"-"+rto_code_spliting[1]).upper()
            self.find_city_by_code(rto_code)
            car_number= text.replace(" ","")
            car_text= "netc."+ car_number.lower()
            self.start_operation(car_text)
        elif re.fullmatch(number_pattern,text):
            number_text= text
            self.start_operation(number_text)
        else:
            self.status_bar.configure(text= "not a valid input", fg_color="red")
        self.searched_string.configure(text=text)

    def searchvpa(self, searchtext,vpa_dict):
        self.search_button.configure(state= rw.DISABLED)
        print(str(searchtext))
        self.search_bar.delete(0,rw.END)
        for suffix in vpa_dict:
            proxy= next(self.proxy_cycle)
            vpa_check=self.address_discovery(searchtext+"@"+suffix,API_URL,proxy)
            if vpa_check == False:
                while vpa_check ==False:
                    print("inwhileloop")
                    print(suffix)
                    proxy= next(self.proxy_cycle)
                    vpa_check=self.address_discovery(searchtext+"@"+suffix,API_URL,proxy)
                print("byeloop")
        if self.found == 0:
            self.status_bar.configure(text="No record Found",fg_color="red")
        else:
            self.status_bar.configure(text=f"{self.found} records found")
        self.search_button.configure(state= rw.NORMAL)      
        self.count=0
        self.found=0
        
    def address_discovery(self, vpa, api_url,proxy):
        try: 
            response = requests.get(api_url+vpa, 
                                    headers= header,
                                    proxies={'http': proxy, 'https': proxy}, 
                                    timeout=3)
            print(proxy)
            print(response.status_code)
            if response.status_code == 200:
                json_response = response.json()
                if json_response["data"]["vpaValid"] == True:
                    handle= vpa.split("@")[1]
                    print(handle)
                    bank_name= str(self.find_bank_name(handle))[1:-1].replace("'","")
                    app_name= str(self.find_app_name(handle))[1:-1].replace("'","")
                    name= json_response['data']['payeeAccountName']
                    print(name)
                    self.table.insert(parent='',index='end',iid=self.index,text='',values=(name,vpa,app_name,bank_name))
                    self.index+=1
                    self.found += 1
                    self.count += 1
                    self.reportProgress(self.count)
                    return True
                elif json_response["data"]["vpaValid"] == False:
                    print("Invalid VPA")
                    self.count += 1
                    self.reportProgress(self.count)
                    return True
            if response.status_code == 400:
                print("Bad Request")
                return True
            if response.status_code == 429:
                print("Too Many Requests")
                return True
        except:
            print("Proxy not working")
            return False
        


    

    def reportProgress(self, value):
        value= (round(((value)/len(upi_suffix_dict))*100))
        self.progressbar['value']= value
        self.progressbar_percent.configure(text=f"{value}%")
        if self.found >=1 and value == 100:
            self.export_button.configure(state=rw.NORMAL)

    def export_function(self):
        data = [self.table.item(item)['values']for item in self.table.get_children()]
        df = pd.DataFrame(data)
        df.to_csv('report.csv',encoding='shift-jis',header=False,index=False)
        messagebox.showinfo("success","successfully saved")

    def window(self):
        self.window_frame = rw.Frame(self)
        self.window_frame.pack(pady=20,expand=True,fill=rw.BOTH)
        self.label_frame= rw.LabelFrame(self.window_frame)
        self.label_frame.pack()
        self.label = ctk.CTkLabel(self.label_frame,text="OSINT TOOL",bg_color="#ffffff",font=("Roboto Medium",30))
        self.label.grid(column= 0, row= 0)
        
        self.action_frame= rw.LabelFrame(self.window_frame)
        self.search_bar_label= ctk.CTkLabel(self.action_frame,text="Enter a mob. no. \ email \ car no.:")
        self.search_bar_label.grid(column=0,row=0,sticky=rw.NSEW)
        self.search_bar= ctk.CTkEntry(self.action_frame,width=200)
        self.search_bar.grid(column=1,row=0,padx=10)
        self.search_button= rw.Button(self.action_frame,text="Search",command= self.textget,cursor="hand2",activebackground="#adb2af")
        self.search_button.grid(column=2,row=0,pady=10,sticky=rw.NSEW)
        self.searched_string= ctk.CTkLabel(self.action_frame,text="")
        self.searched_string.grid(column=0,row=1,sticky=rw.NSEW)
        self.action_frame.pack(pady=20,expand=True,fill=rw.BOTH)
        

        logs_label= rw.LabelFrame(self.window_frame, text= "Results")
        self.progressbar= ttk.Progressbar(logs_label,orient="horizontal",mode="determinate",length=500, maximum=100)
        self.progressbar.pack(padx=5,pady=(2,2),expand=True,fill="x")
        self.progressbar_percent=ctk.CTkLabel(logs_label,text="")
        self.progressbar_percent.pack(pady=(1,15))
        

        table_scrollbar=rw.Scrollbar(logs_label)
        table_scrollbar.pack(side="right",fill="y")
        table_xscrollbar=rw.Scrollbar(logs_label,orient="horizontal")
        table_xscrollbar.pack(side="bottom",fill="x")
        styling=ttk.Style()
        styling.configure(style='Treeview',rowheight=20)
        self.table = ttk.Treeview(logs_label,selectmode="none",yscrollcommand= table_scrollbar.set ,xscrollcommand=table_xscrollbar.set)
        table_scrollbar.configure(command=self.table.yview)
        table_scrollbar.configure(command=self.table.xview)
        self.table['columns'] = ("Name","Virtual Payment Address(VPA)","App Name","Bank Name")
        # self.table_data["show"]="headings"
        self.table.column("#0",width=0,stretch=rw.NO)
        self.table.column("Name",width=50,minwidth=50,anchor=rw.CENTER)
        self.table.column("Virtual Payment Address(VPA)",width=90,minwidth=90,anchor=rw.CENTER)
        self.table.column("App Name",width=50,minwidth=50,anchor=rw.CENTER)
        self.table.column("Bank Name",width=50,minwidth=50,anchor=rw.CENTER)

        self.table.heading("#0",text="")
        self.table.heading("Name",text="Name",anchor= rw.CENTER)
        self.table.heading("Virtual Payment Address(VPA)",text="Virtual Payment Address(VPA)",anchor= rw.CENTER)
        self.table.heading("App Name",text="App Name",anchor= rw.CENTER)
        self.table.heading("Bank Name",text="Bank Name",anchor= rw.CENTER)
        self.table.pack(pady=(30,0),fill=rw.BOTH,expand=True)
        self.other_details= rw.Text(logs_label,height=5)
        self.other_details.insert(rw.END,"Other Details\n\n",'row')
        self.other_details.tag_configure('row',font=('TkDefaultFont', 10, 'bold'))
        self.other_details.configure(state=rw.DISABLED)
        self.other_details.pack()
        self.export_button= rw.Button(logs_label,text="Export",state=rw.DISABLED,command=self.export_function,cursor="hand2")
        self.export_button.pack()
        self.status_bar= ctk.CTkLabel(logs_label,text="")
        self.status_bar.pack()
        logs_label.pack(fill="both",expand=True)
        
    def delete_records(self):
        for row in self.table.get_children():
            self.table.delete(row)
    def find_app_name(self,handle):
        apps=[]
        for app_name,handles in self.app_list.items():
            if handle in handles:
                apps.append(app_name)
        return(apps)
    def find_bank_name(self,handle):
        banks=[]
        for bank_name,handles in self.banks_list.items():
            if handle in handles:
               banks.append(bank_name) 
        return(banks)
    def find_city_by_code(self, code):
        q_city=code
        q_state=code[0]+code[1]
        state=self.state_codes[q_state]
        found=False
        for states,cities in self.rto_code_list.items():
            for city in cities:
                if q_city in city:
                        city=city.split(":")
                        city=city[1]
                        found= True
                        self.other_details.configure(state=rw.NORMAL)
                        self.other_details.insert(rw.END,city+", "+state+"\n")
                        self.other_details.configure(state=rw.DISABLED)
                        break
        if not found:
            print("not found")
    def open_files(self):
        with open(os.path.join(os.getcwd(),"data\\apps.txt"), 'r') as apps_file:
            self.app_list=ast.literal_eval(apps_file.read())
            apps_file.close()
        with open(os.path.join(os.getcwd(),"data\\bankshandle.txt"), 'r') as banks_handle_file:
            self.banks_list= ast.literal_eval(banks_handle_file.read())
            banks_handle_file.close()
        with open(os.path.join(os.getcwd(),"data\\rto_codes.txt"), 'r') as rto_codes_file:
            self.rto_code_list=ast.literal_eval(rto_codes_file.read())
            rto_codes_file.close()
        with open(os.path.join(os.getcwd(),"data\\state_code.txt"), 'r') as state_codes_file:
            self.state_codes = ast.literal_eval(state_codes_file.read())
            state_codes_file.close()
    def start(self):
        self.window()
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()