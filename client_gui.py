# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

from tkinter import *
from PIL import ImageTk, Image
import tkinter as tk
import tkinter.messagebox as tm
import os
import json




class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label_1 = Label(self, text="Display Name")
        self.label_2 = Label(self, text="DnsName")
        self.label_3 = Label(self, text="LoginName")
        self.label_4 = Label(self, text="Password")
        
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self)
        self.entry_3 = Entry(self)
        self.entry_4 = Entry(self, show="*")
        
        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)
        self.label_3.grid(row=2, sticky=E)
        self.label_4.grid(row=3, sticky=E)
        self.entry_3.grid(row=2, column=1)
        self.entry_4.grid(row=3, column=1)
        
        
        self.submitbtn = Button(self, text="Submit", command = self._submit_btn_clicked)
        self.submitbtn.grid(columnspan=2)
        
        self.pack()
    
    def _submit_btn_clicked(self):
        #print("Clicked")
        displayName = self.entry_1.get()
        dnsName = self.entry_2.get()
        loginName = self.entry_3.get()
        password = self.entry_4.get()
        
        #item = {'DisplayName': displayName, 'DnsName': dnsName, 'LoginName':loginName, 'Password':password}
        config = json.loads(open('properties.json').read())
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DisplayName"] = displayName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DnsName"] = dnsName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["LoginName"] = loginName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["Password"] = password

        
        
        with open('properties.json','w') as f:
            f.write(json.dumps(config))
        
        with open('properties.json', 'r') as f:
            config = json.load(f)
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DisplayName"] = displayName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DnsName"] = dnsName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["LoginName"] = loginName
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["Password"] = password

        with open('properties.json','w') as f:
            json.dump(config, f)

        
        t = tk.Toplevel(self)
        a = tk.Label(t, text = "WELCOME " + displayName)
        l = tk.Button(t, text = "Run Conformance Test", command = self._run_btn_clicked)
        m = tk.Button(t, text = "Clear Entries", command = self._clear_btn_clicked)
        
        


        a.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        l.pack()
        m.pack(side = "bottom", padx=50, pady=50)


    def _run_btn_clicked(self):
        os.system('python3.4 rf_client.py')
    
    def _clear_btn_clicked(self):
        config = json.loads(open('properties.json').read())
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DisplayName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DnsName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["LoginName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["Password"] = ""

        
        
        with open('properties.json','w') as f:
            f.write(json.dumps(config))
        
        with open('properties.json', 'r') as f:
            config = json.load(f)
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DisplayName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["DnsName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["LoginName"] = ""
        config["RedfishServiceCheckTool_SUTConfiguration"]["SUTs"][0]["Password"] = ""

        with open('properties.json','w') as f:
            json.dump(config, f)



root = Tk()
lf = LoginFrame(root)
root.title("Redfish Conformance Test Tool")
path = os.getcwd()+ '/image.jpg'
img = ImageTk.PhotoImage(Image.open(path))
panel = tk.Label(root, image = img)
panel.pack(side = "bottom", fill = "both", expand = "yes")
root.mainloop()


