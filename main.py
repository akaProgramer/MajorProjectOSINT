import pandas as pd 
import tkinter as rw
from tkinter import messagebox
import customtkinter as ctk
from tkinter import ttk
import concurrent.futures
import threading
import requests
from time import sleep
from sys import exit
from random import uniform as rand
import regex as re
import socket
import os
import ast


API_URL = 'https://upibankvalidator.com/api/upiValidation?upi='
with open("data/general_suffixes.txt", "r") as suffix_file:
    upi_suffix_dict = suffix_file.read().splitlines()
class App(rw.Tk):
    def __init__(self):
        self.found = 0
        self.count = 0
        super().__init__()
        self.geometry("600x700+300+2")
        self.title("UPI Recon")
        self.open_files()
        # self.wm_iconbitmap("images\me_icon.ico")
        ctk.set_appearance_mode("light")

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
        t= threading.Thread(target=self.searchvpa,args=(searchtext,upi_suffix_dict,5))
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
            car_number= text.replace(" ","")
            car_text= "netc."+ car_number.lower()
            self.start_operation(car_text)
        elif re.fullmatch(number_pattern,text):
            number_text= text
            self.start_operation(number_text)
        else:
            self.status_bar.configure(text= "not a valid input", fg_color="red")
        self.searched_string.configure(text=text)

    def searchvpa(self, searchtext,vpa_dict, threadcount):
        self.search_button.configure(state= rw.DISABLED)
        print(searchtext)
        self.search_bar.delete(0,rw.END)
        if(threadcount == 0):
            for suffix in vpa_dict:
                try:
                    self.address_discovery(searchtext + '@' + suffix, API_URL)
                except KeyboardInterrupt:
                    exit(0)
        else:
            threadcount = 10 if threadcount > 10 else threadcount
            with concurrent.futures.ThreadPoolExecutor(max_workers=threadcount) as executor:
                try:
                    for suffix in vpa_dict:
                        executor.submit(self.address_discovery, searchtext + '@' + suffix, API_URL)
                        sleep(rand(.1, .2))
                        
                except KeyboardInterrupt:
                    executor._threads.clear()
                    concurrent.futures.thread._threads_queues.clear()
        if self.found == 0:
            self.status_bar.configure(text="No record Found",fg="red")
        else:
            self.status_bar.configure(text=f"{self.found} records found")
        self.search_button.configure(state= rw.NORMAL)      
        self.count=0
        self.found=0
        
    def address_discovery(self, vpa, api_url):
        r = requests.post(api_url+vpa)
        # print(r.status_code)
        if r.status_code == 200 and r.json()['isUpiRegistered'] is True:
            handle= vpa.split("@")[1]
            print(handle)
            bank_name= str(self.find_bank_name(handle))[1:-1].replace("'","")
            app_name= str(self.find_app_name(handle))[1:-1].replace("'","")
            name= r.json()['name']
            self.table.insert(parent='',index='end',iid=self.index,text='',values=(name,vpa,app_name,bank_name))
            self.index+=1
            self.found += 1
        # if r.status_code == 400:
        #     print("Bad Request")
        #     pass
        # if r.status_code == 429:
        #     print("Too Many Requests")
        #     pass
        self.count += 1
        self.reportProgress(self.count)
        


    

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
        self.label = ctk.CTkLabel(self.label_frame,text="UPI Recon",bg_color="#ffffff",font=("Roboto Medium",30))
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
        self.table.pack(pady=30,fill=rw.BOTH,expand=True)
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
    def open_files(self):
        with open(os.path.join(os.getcwd(),"data\\apps.txt"), 'r') as apps_file:
            self.app_list=ast.literal_eval(apps_file.read())
            apps_file.close()
        with open(os.path.join(os.getcwd(),"data\\bankshandle.txt"), 'r') as banks_handle_file:
            self.banks_list= ast.literal_eval(banks_handle_file.read())
            banks_handle_file.close()
    def start(self):
        self.window()
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()