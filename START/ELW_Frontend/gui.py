#!/usr/bin/env python
# -*- coding: utf-8 -*-

#GUI v 1.0
# Here we define everything that has to do with the gui, also a lot of the
# data processing is done here. This probably should be in a different class
# but having it here is convenient since some tests are done by checking the
# existence of objects in the gui
# The code is not beautiful, I should have introduced basic window classes to make
# the code shorter an better readable -> do it in the future.


#Copyright Philipp Scior philipp.scior@drk-forum.de

import Tkinter
import ttk
import datetime
from ELW_Backend.database import Database
from ELW_Backend.database import Database_error
from Autocomplete import Autocomplete
import Queue
import time
import sys
import re

class GUI(Tkinter.Frame):
    '''
    classdocs
    '''
    # globally defined buffers and lists for data processing
    puffer= ["","","","","","","","","","","","","","","","","","","","","","","","","","",""]
    #contact_array=["","","","",""]
    upstart_buffer=[]
    einheiten_dict={}
    hiorgs=("RD", "Rettungdienst", "DRK", "Johanniter", "Maltester", "ASB", "JUH", "MHD")
    fws=("FW", "Feuerwehr", "FFW", "WF", "BF", "Berufsfeuerwehr", "Werkfeuerwehr", "Werksfeuerwehr", "FF")
    br=""
    rd_types={"RTW" : 0, "KTW" : 0, "NEF" : 0, "GW-San" : 0}
    fw_types={"LF" : 0, "TLF" : 0, "RW" : 0, "DL" : 0}
    helfer=0
    agt=0
    fahrz_num=0
    # constructor of the main window, need the parent window, the database, the queues and the IP
    # of the computer as input
    def __init__(self, parent, Bereitstellungsraum, read_queue, send_queue, ip, small):
        '''
        Constructor
        '''

        Tkinter.Frame.__init__(self, parent)
        self.parent=parent
        self.Bereitstellungsraum=Bereitstellungsraum
        self.newname=""
        

        #this constructs the window, where we have to choose what kind of BSR we want to have
        self.kind_of()
        print(self.Bereitstellungsraum.br_name)

        if self.Bereitstellungsraum.br_name=="":
            self.name_it()
            print(self.Bereitstellungsraum.br_name)
            self.Bereitstellungsraum.set_name(self.newname)

        # time stuff for the clock
        self.the_time=Tkinter.StringVar()
        self.start_time=time.strftime("%H:%M", time.localtime())
        self.the_time=''

        # define several frames to make a nicer layout
        self.tree_frame = Tkinter.Frame(self.parent)
        self.aux_frame = Tkinter.Frame(self.parent)
        self.empty_frame = Tkinter.Frame(self.aux_frame)
        self.side_frame = Tkinter.Frame(self.aux_frame)
        self.top_frame = Tkinter.Frame(self.aux_frame)
        
        # the couter of the number of people in the BSR
        self.persons= Tkinter.StringVar()

        self.agt_num=Tkinter.StringVar()

        self.fahrz=Tkinter.StringVar()

        self.rtw_num= Tkinter.StringVar()
        self.ktw_num= Tkinter.StringVar()
        self.nef_num= Tkinter.StringVar()
        self.gw_num= Tkinter.StringVar()

        self.lf_num= Tkinter.StringVar()
        self.tlf_num= Tkinter.StringVar()
        self.rw_num= Tkinter.StringVar()
        self.dl_num= Tkinter.StringVar()
        
        self.small=small

        self.ip=ip

        # this actually constructs the main window
        self.initialize_user_interface()
        print("before read database")
        # read the database
        self.read_database()
        print("after read database")
        #print(self.Bereitstellungsraum.type_querry())

        self.update_type_lists()
        self.helfer=self.Bereitstellungsraum.get_persons()
        self.agt=self.Bereitstellungsraum.get_agt()

        self.r_queue=read_queue
        self.s_queue=send_queue



        
    # here the main window is build
    def initialize_user_interface(self):
        
        #self.parent.title("START Vorführversion für den hessischen KatS-Preis")

        # set the images for the buttons in top row
        self.plus=Tkinter.PhotoImage(file="ELW_Frontend/images/plus.gif")
        self.pen=Tkinter.PhotoImage(file="ELW_Frontend/images/pen.gif")
        self.group=Tkinter.PhotoImage(file="ELW_Frontend/images/group.gif")
        self.ungroup=Tkinter.PhotoImage(file="ELW_Frontend/images/ungroup.gif")

        if self.small:
            self.plus=self.plus.subsample(2)
            self.pen=self.pen.subsample(2)
            self.group=self.group.subsample(2)
            self.ungroup=self.ungroup.subsample(2)
            self.clock_size=30
            padxx=5
        else:
            self.clock_size=60
            padxx=50



        # set the background colors
        self.parent.config(background="gray26")
        self.top_frame.config(background="gray26")
        self.tree_frame.config(background="gray26")
        self.side_frame.config(background="gray26")
        self.aux_frame.config(background="gray26")
        self.empty_frame.config(background="gray26")

       
        #print(self.br)
        self.parent.focus()
        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)

        # Define the different GUI widgets

        #define stuff in the top frame
        if self.br == "rd":
            self.add_button = Tkinter.Button(self.top_frame, image=self.plus, command=self.add_window_rd, relief=Tkinter.FLAT, bd=0, bg="gray26")
        elif self.br == "fw":
            self.add_button = Tkinter.Button(self.top_frame, image=self.plus, command=self.add_window_fw, relief=Tkinter.FLAT, bd=0, bg="gray26")
        else:
            self.add_button = Tkinter.Button(self.top_frame, image=self.plus, command=self.add_window, relief=Tkinter.FLAT, bd=0, bg="gray26")
        
        self.add_label = Tkinter.Label(self.top_frame, text="Hinzufügen", bg="gray26", fg="white", font=("Calibri", 12))
        self.update_label = Tkinter.Label(self.top_frame, text="Bearbeiten", bg="gray26", fg="white", font=("Calibri", 12))
        self.group_label = Tkinter.Label(self.top_frame, text="Gruppieren", bg="gray26", fg="white", font=("Calibri", 12))
        self.release_label= Tkinter.Label(self.top_frame, text="Auflösen", bg="gray26", fg="white", font=("Calibri", 12))

        self.persons_label= Tkinter.Label(self.top_frame, text= "Einsatzkräfte in Bereitstellung:", bg="gray26", fg="white", font=("Calibri", 12))
        self.persons_count= Tkinter.Message(self.top_frame, textvariable=self.persons, relief=Tkinter.RAISED)
            
        self.up_button = Tkinter.Button(self.top_frame, image=self.pen,command=self.update_window, relief=Tkinter.FLAT, bd=0, bg="gray26")
        self.group_button = Tkinter.Button(self.top_frame, image=self.group, command=self.group_window, relief=Tkinter.FLAT, bd=0, bg="gray26")
        self.release_button = Tkinter.Button(self.top_frame, image=self.ungroup, command=self.release, relief=Tkinter.FLAT, bd=0, bg="gray26")

        self.add_label.grid(row=0, column=0, padx=(10,5))
        self.update_label.grid(row=0, column=1, padx=(5,35))
        self.group_label.grid(row=0,column=2, padx=5)
        self.release_label.grid(row=0, column=3, padx=5)

        self.add_button.grid(row=1, rowspan=4, column=0, padx=(10,5), pady=(0,30))
        self.up_button.grid(row=1,  rowspan=4, column=1, padx=(5,35), pady=(0,30))
        self.group_button.grid(row=1, rowspan=4, column=2, padx=5, pady=(0,30))
        self.release_button.grid(row=1, rowspan=4, column=3, padx=5, pady=(0,30))

        #self.time_label = Tkinter.Label(self.top_frame, text=self.start_time, bg="white", fg="black", font=("Calibri", 60))
        self.time_label = Tkinter.Label(self.top_frame, text=self.start_time, bg="white", fg="black", font=("Calibri", self.clock_size))
        self.time_label.grid(row=1, rowspan=4, column=4, padx=padxx, sticky="n")

        #self.persons_label.grid(row=1, column=5, padx=(50,5), sticky="ne")
        self.persons_label.grid(row=1, column=5, padx=(5,5), sticky="ne")
        self.persons_count.grid(row=1, column=6, sticky="ne")

        self.fahrz_label= Tkinter.Label(self.top_frame, text="Fahrzeuge in Bereitstellung", bg="gray26", fg="white", font=("Calibri", 12))
        self.fahrz_count= Tkinter.Message(self.top_frame, textvariable=self.fahrz, relief=Tkinter.RAISED)

        self.fahrz_label.grid(row=3, column=5, padx=(5,5), sticky="ne")
        self.fahrz_count.grid(row=3, column=6, sticky="ne")

        if not self.br == "rd":
            self.agt_label = Tkinter.Label(self.top_frame, text = "AGT in Bereitstellung", bg="gray26", fg="white", font=("Calibri", 12))
            self.agt_count = Tkinter.Message(self.top_frame, textvariable=self.agt_num, relief=Tkinter.RAISED)

            self.agt_label.grid(row=2, column=5, padx=(5,5), sticky="ne")
            self.agt_count.grid(row=2, column=6, sticky="ne")


        if self.br == "rd" or self.br == "gm":
            self.rtw_label= Tkinter.Label(self.top_frame, text= "RTW:", bg="gray26", fg="white", font=("Calibri", 12))
            self.rtw_count= Tkinter.Message(self.top_frame, textvariable=self.rtw_num, relief=Tkinter.RAISED)
            self.rtw_label.grid(row=1, column=7, padx=(padxx,5), sticky="ne")
            self.rtw_count.grid(row=1, column=8, sticky="ne")


            self.ktw_label= Tkinter.Label(self.top_frame, text= "KTW:", bg="gray26", fg="white", font=("Calibri", 12))
            self.ktw_count= Tkinter.Message(self.top_frame, textvariable=self.ktw_num, relief=Tkinter.RAISED)
            self.ktw_label.grid(row=2, column=7, padx=(padxx,5), sticky="ne")
            self.ktw_count.grid(row=2, column=8, sticky="ne")

            self.nef_label= Tkinter.Label(self.top_frame, text= "NEF:", bg="gray26", fg="white", font=("Calibri", 12))
            self.nef_count= Tkinter.Message(self.top_frame, textvariable=self.nef_num, relief=Tkinter.RAISED)
            self.nef_label.grid(row=3, column=7, padx=(padxx,5), sticky="ne")
            self.nef_count.grid(row=3, column=8, sticky="ne")

            self.gw_label= Tkinter.Label(self.top_frame, text= "GW-San:", bg="gray26", fg="white", font=("Calibri", 12))
            self.gw_count= Tkinter.Message(self.top_frame, textvariable=self.gw_num, relief=Tkinter.RAISED)
            self.gw_label.grid(row=4, column=7, padx=(padxx,5), sticky="ne")
            self.gw_count.grid(row=4, column=8, sticky="ne")

        if self.br == "fw" or self.br == "gm":
            self.lf_label= Tkinter.Label(self.top_frame, text= "LF:", bg="gray26", fg="white", font=("Calibri", 12))
            self.lf_count= Tkinter.Message(self.top_frame, textvariable=self.lf_num, relief=Tkinter.RAISED)
            self.lf_label.grid(row=1, column=9, padx=(padxx,5), sticky="ne")
            self.lf_count.grid(row=1, column=10, sticky="ne")


            self.tlf_label= Tkinter.Label(self.top_frame, text= "TLF:", bg="gray26", fg="white", font=("Calibri", 12))
            self.tlf_count= Tkinter.Message(self.top_frame, textvariable=self.tlf_num, relief=Tkinter.RAISED)
            self.tlf_label.grid(row=2, column=9, padx=(padxx,5), sticky="ne")
            self.tlf_count.grid(row=2, column=10, sticky="ne")

            self.rw_label= Tkinter.Label(self.top_frame, text= "RW:", bg="gray26", fg="white", font=("Calibri", 12))
            self.rw_count= Tkinter.Message(self.top_frame, textvariable=self.rw_num, relief=Tkinter.RAISED)
            self.rw_label.grid(row=3, column=9, padx=(padxx,5), sticky="ne")
            self.rw_count.grid(row=3, column=10, sticky="ne")

            self.dl_label= Tkinter.Label(self.top_frame, text= "DL:", bg="gray26", fg="white", font=("Calibri", 12))
            self.dl_count= Tkinter.Message(self.top_frame, textvariable=self.dl_num, relief=Tkinter.RAISED)
            self.dl_label.grid(row=4, column=9, padx=(padxx,5), sticky="ne")
            self.dl_count.grid(row=4, column=10, sticky="ne")


        self.print_button = Tkinter.Button(self.side_frame, text="Lagemeldung", command=self.print_to_file, relief=Tkinter.FLAT, bd=0, bg="yellow", font=("Calibri", 12))
        self.print_button.grid(row =0, column=2, sticky="e", padx=(padxx,5), pady=(5,5))

        self.help_button = Tkinter.Button(self.side_frame, text="Hilfe", command=self.help_window, relief=Tkinter.FLAT, bd=0, bg="yellow", font=("Calibri", 12))
        self.help_button.grid(row =1, column=2, sticky="e", padx=(padxx,5), pady=(5,5))

        self.hist_print_button = Tkinter.Button(self.side_frame, text="Protokoll", command=self.print_history, relief=Tkinter.FLAT, bd=0, bg="yellow", font=("Calibri", 12))
        self.hist_print_button.grid(row =2, column = 2, sticky="e", padx=(padxx,5), pady=(5,0))


        # define stuff in the tree frame
        self.tree_frame.grid_rowconfigure(5, weight=1)


        for x in xrange(0,6):
            self.tree_frame.grid_columnconfigure(x, uniform='fred', weight=1)

        self.tree_frame.grid_rowconfigure(1, weight=3)
 
        self.br_label = Tkinter.Label(self.tree_frame, text = "Fahrzeuge in Bereitstellung:", bg="gray26", fg="white", font=("Calibri", 16, "bold"))
        self.br_label.grid(row = 0, column = 0, columnspan=2, sticky = Tkinter.W)
        
        if self.br == "fw" or self.br == "gm":
            columns=('Funkrufname', 'Organisation', 'Fahrzeugtyp', 'Atemschutz', 'CSA', 'Bemerkungen')
        else:
            columns=('Funkrufname', 'Organisation', 'Fahrzeugtyp', 'Bemerkungen')
        # Set the br_treeview
        self.br_tree = ttk.Treeview( self.tree_frame, columns=columns)

        self.br_tree.heading('#0', text='')
        self.br_tree.heading('Funkrufname', text='Funkrufname',command=lambda: self.treeview_sort_column(self.br_tree, 'Funkrufname', False))
        self.br_tree.heading('Organisation', text='Organisation',command=lambda: self.treeview_sort_column(self.br_tree, 'Organisation', False))
        self.br_tree.heading('Fahrzeugtyp', text='Fahrzeugtyp',command=lambda: self.treeview_sort_column(self.br_tree, 'Fahrzeugtyp', False))
        if self.br == "fw" or self.br == "gm":
            self.br_tree.heading('Atemschutz', text='AGT', command=lambda: self.treeview_sort_column(self.br_tree, 'Atemschutz', False))
            self.br_tree.heading('CSA', text='CSA', command=lambda: self.treeview_sort_column(self.br_tree, 'CSA', False)) 

        self.br_tree.heading('Bemerkungen', text='Bemerkungen',command=lambda: self.treeview_sort_column(self.br_tree, 'Bemerkungen', False))
        
        self.br_tree.column('Organisation', stretch=Tkinter.YES)
        self.br_tree.column('Fahrzeugtyp', stretch=Tkinter.YES)
        self.br_tree.column('Funkrufname', stretch=Tkinter.YES)
        if self.br == "fw" or self.br == "gm":
            self.br_tree.column('Atemschutz', width=70, stretch=Tkinter.YES)
            self.br_tree.column('CSA', width=70, stretch=Tkinter.YES)
        self.br_tree.column('Bemerkungen', stretch=Tkinter.YES)
        self.br_tree.column('#0',width=50, stretch=Tkinter.NO)
        self.br_tree.grid(row=1, columnspan=6, sticky='nsew')
        self.br_treeview = self.br_tree
        self.br_treeScroll = ttk.Scrollbar(self.tree_frame)

        self.br_treeScroll.configure(command=self.br_treeview.yview)
        self.br_treeview.configure(yscrollcommand=self.br_treeScroll.set)
        self.br_treeScroll.grid(row=1,column=6,sticky=Tkinter.N+Tkinter.S+Tkinter.W)

        self.br_treeview.tag_configure('leader', background='grey')

        self.auftrag_button = Tkinter.Button(self.tree_frame, text = "Auftrag", command=self.auftrag_window, relief=Tkinter.FLAT, bd=0, bg="yellow", font=("Calibri", 12))
        self.auftrag_button.grid(row=3, column =5 , sticky=Tkinter.E)


        # define stuff in the issued_tree frame
        self.issued_label = Tkinter.Label(self.tree_frame, text = "Erteilte Aufträge:", bg="gray26", fg="white", font=("Calibri", 16, "bold"))
        self.issued_label.grid(row = 4, column = 0, sticky = Tkinter.W)

        
        columns_i=('Funkrufname', 'Ziel', 'Fahrzeugtyp', 'Bemerkungen')
        self.issued_tree = ttk.Treeview( self.tree_frame, columns=columns_i)
        self.issued_tree.heading('#0', text='')
        self.issued_tree.heading('Funkrufname', text='Funkrufname',command=lambda: self.treeview_sort_column(self.issued_tree, 'Funkrufname', False))
        self.issued_tree.heading('Ziel', text='Ziel',command=lambda: self.treeview_sort_column(self.issued_tree, 'Ziel', False))
        self.issued_tree.heading('Fahrzeugtyp', text='Fahrzeugtyp',command=lambda: self.treeview_sort_column(self.issued_tree, 'Fahrzeugtyp', False))
        self.issued_tree.heading('Bemerkungen', text='Bemerkungen',command=lambda: self.treeview_sort_column(self.issued_tree, 'Bemerkungen', False))
        self.issued_tree.column('#0',width=50, stretch=Tkinter.NO)
        self.issued_tree.grid(row=5, columnspan=6, sticky='nsew')
        self.issued_treeview = self.issued_tree
        self.issued_treeScroll = ttk.Scrollbar(self.tree_frame)

        self.issued_treeScroll.configure(command=self.issued_treeview.yview)
        self.issued_treeview.configure(yscrollcommand=self.issued_treeScroll.set)
        self.issued_treeScroll.grid(row=5,column=6,sticky=Tkinter.N+Tkinter.S+Tkinter.W)
        
        self.leave_button=Tkinter.Button(self.tree_frame, text="Verlassen", command=self.leave_window, relief=Tkinter.FLAT, bd=0, bg="yellow", font=("Calibri", 12))
        self.leave_button.grid(row=6, column=5, sticky=Tkinter.E)
        self.ip_label=Tkinter.Text(self.tree_frame, bg="gray26", fg="white",font=("Calibri", 12), height=1, borderwidth=0)
        self.ip_label.insert(1.0, "IP Adresse: {}".format(self.ip))
        self.ip_label.grid(row=6, column=0, columnspan=2, sticky="w")
        self.ip_label.configure(state="disabled")
        #Tkinter.Label(self.tree_frame, text="Vorführversion für den hessischen KatS-Preis",bg="gray26", fg="white",font=("Calibri", 12, "bold"), height=1, borderwidth=0).grid(row=6, column=2, columnspan=3)

        #and pack the frames
        self.top_frame.pack(side=Tkinter.LEFT, expand=1, anchor=Tkinter.W)

        self.aux_frame.pack(fill=Tkinter.X)
        self.side_frame.pack(fill=Tkinter.X, expand=1, anchor="w")

        
        self.tree_frame.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)


        #handle to open the update window
        def update_event(event):
            self.update_window()
        
        #handle to change to background color of the clock back to white
        def update_time(event):
            self.time_label.configure(bg="white")

        self.br_treeview.bind("<Double-Button-1>", update_event)
        self.time_label.bind("<Double-Button-1>", update_time)

    #  handle to call the print to csv method
    def print_to_file(self):
        self.Bereitstellungsraum.print_to_file()

    def print_history(self):
        self.Bereitstellungsraum.print_history()

    # listens to modifications of what is shown in the gui and corrects the gui
    def listen(self):
        self.modify_api()
        #self.persons.set(self.Bereitstellungsraum.get_persons())
        #self.agt_num.set(self.Bereitstellungsraum.get_agt())
        self.persons.set(self.helfer)
        self.agt_num.set(self.agt)

        self.rtw_num.set(self.rd_types["RTW"])
        #print(self.rd_types["RTW"])
        self.ktw_num.set(self.rd_types["KTW"])
        self.nef_num.set(self.rd_types["NEF"])
        self.gw_num.set(self.rd_types["GW-San"])

        self.lf_num.set(self.fw_types["LF"])
        self.tlf_num.set(self.fw_types["TLF"])
        self.rw_num.set(self.fw_types["RW"])
        self.dl_num.set(self.fw_types["DL"])
        self.fahrz.set(self.fahrz_num)

        #self.the_time.set(time.strftime("%H:%M", time.localtime()))
        self.the_time=time.strftime("%H:%M", time.localtime())
        self.time_label.configure(text=self.the_time)
        if time.strftime("%M:%S", time.localtime())=="00:00" or  time.strftime("%M:%S", time.localtime())=="15:00" or  time.strftime("%M:%S", time.localtime())=="30:00" or  time.strftime("%M:%S", time.localtime())=="45:00":
            print("now")
            self.time_label.configure(bg="red")
        self.after(100, self.listen)

    # debrecated!
    def whatis(self):
        try:
            selected_item = self.br_treeview.selection()
            for x in selected_item:
                print(self.br_treeview.item(x))
        except IndexError as ex:
            pass

    # clear the contact information in the buffer
    def clear_contacts(self):
        for i in xrange(22,27):
            self.puffer[i]=""
    
    # define the window to enter contact informations
    def contact_window(self):
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.wm_title("Kontaktdaten")
        t.grab_set()

        tel_label = Tkinter.Label(t, text="Telefon")
        tel_entry = Tkinter.Entry(t, width=50)
        tel_entry.insert(0,self.puffer[22])

        fax_label = Tkinter.Label(t, text="Fax")
        fax_entry = Tkinter.Entry(t, width=50)
        fax_entry.insert(0,self.puffer[23])

        mail_label = Tkinter.Label(t, text="E-Mail")
        mail_entry = Tkinter.Entry(t, width=50)
        mail_entry.insert(0,self.puffer[24])

        issi_label = Tkinter.Label(t, text="ISSI")

        mrt_label = Tkinter.Label(t, text="MRT")
        mrt_entry = Tkinter.Entry(t, width=50)
        mrt_entry.insert(0,self.puffer[25])

        hrt_label = Tkinter.Label(t, text="HRT")
        hrt_entry = Tkinter.Entry(t, width=50)
        hrt_entry.insert(0,self.puffer[26])

        tel_label.grid(row =0, column=0, columnspan=2)
        tel_entry.grid(row=0, column=2)

        fax_label.grid(row=1, column=0, columnspan=2)
        fax_entry.grid(row=1, column=2)

        mail_label.grid(row=2, column=0, columnspan=2)
        mail_entry.grid(row=2, column=2)

        issi_label.grid(row=3, rowspan=2, column=0)
        mrt_label.grid(row=3, column=1)
        hrt_label.grid(row=4, column=1)
        mrt_entry.grid(row=3, column=2)
        hrt_entry.grid(row=4, column=2)

        def submit(event=None):
            self.puffer[22]=tel_entry.get()
            self.puffer[23]=fax_entry.get()
            self.puffer[24]=mail_entry.get()
            self.puffer[25]=mrt_entry.get()
            self.puffer[26]=hrt_entry.get()
            t.destroy()

        submit_button = Tkinter.Button(t, text="OK", command=submit)
        submit_button.grid(row=5, column=2, sticky=Tkinter.E)
            
        
        

    # define the window to manually add vehicles to the BSR <- only used in mixed BSR
    def add_window(self):
        w = Tkinter.Toplevel(self)
        w.wm_title("Manuelles Hinzufügen von Fahrzeugen")
        if sys.platform =="win32":
            w.iconbitmap("ELW_Frontend/images/Logo.ico")
        def open_add_rd():
            w.destroy()
            self.add_window_rd()
        def open_add_fw():
            w.destroy()
            self.add_window_fw()
        def open_add_sonst():
            w.destroy()
            self.add_window_sonst()
        rd_button = Tkinter.Button(w, text = "Rettungsdienst", command=open_add_rd, default=Tkinter.ACTIVE)
        rd_button.pack()
        fw_button = Tkinter.Button(w, text = "Feuerwehr", command=open_add_fw, default=Tkinter.ACTIVE)
        fw_button.pack()
        sonst_button = Tkinter.Button(w, text = "andere Organisation", command=open_add_sonst, default=Tkinter.ACTIVE)
        sonst_button.pack()


    # define the window to add a RD vehicle to the BSR   
    def add_window_rd(self):
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.config(bg="white")
        frame1=Tkinter.Frame(t)
        frame2=Tkinter.Frame(t)
        frame3=Tkinter.Frame(t)
        frame4=Tkinter.Frame(t)
        frame5=Tkinter.Frame(t)
        t.wm_title("Manuelles Hinzufügen von Fahrzeugen")
        self.clear_contacts()
        #l = Tkinter.Label(t, text="This is window")
        #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
        #organisation_label.config(bg="white")
        organisation_entry = Tkinter.Entry(frame1, width=60)
        organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)
        organisation_entry.insert(0,"RD")
        organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        organisation_entry.grid(row = 0, column=1, columnspan = 3)


        f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
        #f_name_label.config(bg="white")
        f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_name_entry.focus()
        #if what==1:
        #   f_name_entry.insert(0, selected_item.item(selected_item, )
        f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        f_name_entry.grid(row = 1, column=1, columnspan = 3)



        f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
        #f_typ_label.config(bg="white")
        f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
        f_typ_entry.grid(row = 2, column=1, columnspan = 2)

        kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
        kontakt_button.grid(row=2, column =3)
        

        personal_label = Tkinter.Label(frame2, text = "Besatzung:")
        #personal_label.config(bg="white")
        personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        zf_entry = Tkinter.Entry(frame2, width=3)
        zf_entry.insert(0, 0)
        zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
        gf_entry = Tkinter.Entry(frame2, width=3)
        gf_entry.insert(0, 0)
        gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
        helfer_entry = Tkinter.Entry(frame2, width=3)
        helfer_entry.insert(0, 0)
        helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))

        ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
        #ankunft_label.config(bg="white")
        ankunft_entry = Tkinter.Entry(frame5)
        ankunft_entry.insert(0, datetime.datetime.now())
        ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

        var = Tkinter.IntVar()
        check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
        #check.config(bg="white")
        check.grid(row=0, column=2, sticky=Tkinter.W)

        notarzt_label = Tkinter.Label(frame2, text = "Notarzt:")
        #notarzt_label.config(bg="white")
        notarzt_entry = Tkinter.Entry(frame2, width=3)
        notarzt_entry.insert(0, 0)
        notarzt_label.grid(row = 0, column = 4, sticky = Tkinter.E)
        notarzt_entry.grid(row = 0, column = 5, padx=(0,20))

        arzt_label = Tkinter.Label(frame2, text = "Arzt:")
        #arzt_label.config(bg="white")
        arzt_entry = Tkinter.Entry(frame2, width=3)
        arzt_entry.insert(0, 0)
        arzt_label.grid(row = 0, column = 6, sticky = Tkinter.W)
        arzt_entry.grid(row = 0, column = 7)

        notsan_label = Tkinter.Label(frame2, text = "NotSan + RettAss:")
        #notsan_label.config(bg="white")
        notsan_entry = Tkinter.Entry(frame2, width=3)
        notsan_entry.insert(0, 0)
        notsan_label.grid(row = 1, column = 4, sticky = Tkinter.E)
        notsan_entry.grid(row = 1, column = 5, padx=(0,20))

        rs_label = Tkinter.Label(frame2, text = "RS:")
        #rs_label.config(bg="white")
        rs_entry = Tkinter.Entry(frame2, width=3)
        rs_entry.insert(0, 0)
        rs_label.grid(row = 1, column = 6, sticky = Tkinter.W)
        rs_entry.grid(row = 1, column = 7)

        trapo_label = Tkinter.Label(frame3, text = "Transportkapazität:")
        #trapo_label.config(bg="white")
        trapo_label.grid(row = 0, column = 0, sticky = Tkinter.W, padx=(0,85))

        liegend_label = Tkinter.Label(frame3, text = "liegend:")
        #liegend_label.config(bg="white")
        liegend_entry = Tkinter.Entry(frame3,width=3)
        liegend_entry.insert(0, 0)
        liegend_label.grid(row = 0, column = 1, sticky = Tkinter.E)
        liegend_entry.grid(row = 0, column = 2, padx=(0,3))

        tragestuhl_label = Tkinter.Label(frame3, text = "Tragestuhl:")
        #tragestuhl_label.config(bg="white")
        tragestuhl_entry = Tkinter.Entry(frame3, width=3)
        tragestuhl_entry.insert(0, 0)
        tragestuhl_label.grid(row = 0, column = 3, sticky = Tkinter.E)
        tragestuhl_entry.grid(row = 0, column = 4, padx=(0,4))

        sitzend_label = Tkinter.Label(frame3, text = "sitzend:")
        #sitzend_label.config(bg="white")
        sitzend_entry = Tkinter.Entry(frame3, width=3)
        sitzend_entry.insert(0, 0)
        sitzend_label.grid(row = 0, column = 5, sticky = Tkinter.E)
        sitzend_entry.grid(row = 0, column = 6)       

        sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
        #sonderbeladung_label.config(bg="white")
        sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
        sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W)

        bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
        #bemerkung_label.config(bg="white")
        bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
        bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



        frame1.config(pady=5, padx=10)
        frame2.config(width=200, pady=5, padx=10)
        frame3.config(pady=5, padx=10)
        frame4.config(pady=5, padx=10)
        frame5.config(pady=5, padx=10)

        add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"))
        add_label.config(bg="white")
        #add_label.grid(row=0, column=2, sticky=Tkinter.W)

        add_label.grid(row=0, column=0, columnspan=4)
        frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
        frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
        frame3.grid(row=4, column=0, columnspan=4, pady=5, sticky="we")
        frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")
       
        # method to create the gui object refering to the vehicle and for creating 
        # the database entry   
        def insert_data(event=None):
            """
            Insertion method.
            """
            self.puffer[0]=f_name_entry.get()
            self.puffer[1]=organisation_entry.get()
            self.puffer[2]=f_typ_entry.get()
            self.puffer[3]=zf_entry.get()
            self.puffer[4]=gf_entry.get()
            self.puffer[5]=helfer_entry.get()
            self.puffer[6]=var.get()
            self.puffer[7]=ankunft_entry.get()
            self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
            self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
            self.puffer[10]=notarzt_entry.get()
            self.puffer[11]=arzt_entry.get()
            self.puffer[12]=notsan_entry.get()
            self.puffer[13]=rs_entry.get()
            self.puffer[14]=liegend_entry.get()
            self.puffer[15]=tragestuhl_entry.get()
            self.puffer[16]=sitzend_entry.get()
            for i in xrange(17,22):
                self.puffer[i]=""

            #old_name=(self.puffer[0],)
            try:
                for i in xrange(0,17):
                    if self.puffer[i]=="" and (not i in (8,9)):
                        raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                
                print(self.puffer)              
                self.Bereitstellungsraum.add((self.puffer))
                t.destroy()
                if self.br == "rd":
                    self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[8]))
                else:
                    self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]))
            except Database_error as e:
                print("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except Input_error as g:
                print("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1=Tkinter.Toplevel(t)
                error1.wm_title("FEHLER")
                error1.focus()
                error1_label=Tkinter.Label(error1, text="FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1_label.pack()
                error1_button=Tkinter.Button(error1, text="OK", command=error1.destroy)
                error1_button.pack()
                t.wait_window(error1)

            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()

        submit_button = Tkinter.Button(t, text = "Hinzufügen", command=insert_data, default=Tkinter.ACTIVE)
        submit_button.grid(row = 6, column = 3, sticky = Tkinter.E)

        t.bind("<Return>", insert_data)

        t.grab_set()
        self.parent.wait_window(t)

############# end add_wind_rd()

    #same as for the add_rd window but for fw
    def add_window_fw(self):
        t = Tkinter.Toplevel(self)
        t.config(bg="red")
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        self.clear_contacts()
        
        frame1=Tkinter.Frame(t)
        frame2=Tkinter.Frame(t)
        frame3=Tkinter.Frame(t)
        frame4=Tkinter.Frame(t)
        frame5=Tkinter.Frame(t)
        t.wm_title("Manuelles Hinzufügen von Fahrzeugen")
        #l = Tkinter.Label(t, text="This is window")
        #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
        #organisation_label.config(bg="white")
        organisation_entry = Tkinter.Entry(frame1, width=60)
        organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)
        organisation_entry.insert(0,"FW")
        organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        organisation_entry.grid(row = 0, column=1, columnspan = 3)

        f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
        #f_name_label.config(bg="white")
        f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_name_entry.focus()
        #if what==1:
        #   f_name_entry.insert(0, selected_item.item(selected_item, )
        f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
        #f_name_label.config(bg="white")
        f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_name_entry.focus()
        #if what==1:
        #   f_name_entry.insert(0, selected_item.item(selected_item, )
        f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        f_name_entry.grid(row = 1, column=1, columnspan = 3)



        f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
        #f_typ_label.config(bg="white")
        f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
        f_typ_entry.grid(row = 2, column=1, columnspan = 2)

        kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
        kontakt_button.grid(row=2, column =3)
        

        personal_label = Tkinter.Label(frame2, text = "Besatzung:")
        #personal_label.config(bg="white")
        personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        zf_entry = Tkinter.Entry(frame2, width=3)
        zf_entry.insert(0, 0)
        zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
        gf_entry = Tkinter.Entry(frame2, width=3)
        gf_entry.insert(0, 0)
        gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
        helfer_entry = Tkinter.Entry(frame2, width=3)
        helfer_entry.insert(0, 0)
        helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))
    
        ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
        #ankunft_label.config(bg="white")
        ankunft_entry = Tkinter.Entry(frame5)
        ankunft_entry.insert(0, datetime.datetime.now())
        ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

        var = Tkinter.IntVar()
        check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
        #check.config(bg="white")
        check.grid(row=0, column=2, sticky=Tkinter.W)

        atemschutz_label = Tkinter.Label(frame2, text = "Atemschutz:")
        #notarzt_label.config(bg="white")
        atemschutz_entry = Tkinter.Entry(frame2, width=3)
        atemschutz_entry.insert(0, 0)
        atemschutz_label.grid(row = 0, column = 4, sticky = Tkinter.E)
        atemschutz_entry.grid(row = 0, column = 5, padx=(0,20))

        csa_label = Tkinter.Label(frame2, text = "CSA:")
        #arzt_label.config(bg="white")
        csa_entry = Tkinter.Entry(frame2, width=3)
        csa_entry.insert(0, 0)
        csa_label.grid(row = 0, column = 6, sticky = Tkinter.W)
        csa_entry.grid(row = 0, column = 7)


        sanitaeter_label = Tkinter.Label(frame2, text = "Sanitäter:")
        #rs_label.config(bg="white")
        sanitaeter_entry = Tkinter.Entry(frame2, width=3)
        sanitaeter_entry.insert(0, 0)
        sanitaeter_label.grid(row = 1, column = 6, sticky = Tkinter.W)
        sanitaeter_entry.grid(row = 1, column = 7)

        loeschwasser_label = Tkinter.Label(frame3, text = "Löschwasser:")
        #trapo_label.config(bg="white")
        loeschwasser_label.grid(row = 0, column = 0, sticky = Tkinter.W)

        loeschwasser_entry = Tkinter.Entry(frame3,width=15)
        loeschwasser_entry.insert(0, 0)

        loeschwasser_entry.grid(row = 0, column = 1, padx=(0,74))

        schaummittel_label = Tkinter.Label(frame3, text = "Schaummittel:")
        #tragestuhl_label.config(bg="white")
        schaummittel_entry = Tkinter.Entry(frame3, width=15)
        schaummittel_entry.insert(0, 0)
        schaummittel_label.grid(row = 0, column = 2, sticky = Tkinter.E)
        schaummittel_entry.grid(row = 0, column = 3, padx=(0,4))

        sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
        #sonderbeladung_label.config(bg="white")
        sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
        sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W) 


        bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
        #bemerkung_label.config(bg="white")
        bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
        bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



        frame1.config(pady=5, padx=10)
        frame2.config(width=200, pady=5, padx=10)
        frame3.config(pady=5, padx=10)
        frame4.config(pady=5, padx=10)
        frame5.config(pady=5, padx=10)

        add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"), fg="white")
        add_label.config(bg="red")
        #add_label.grid(row=0, column=2, sticky=Tkinter.W)

        add_label.grid(row=0, column=0, columnspan=4)
        frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
        frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
        frame3.grid(row=4, column=0, columnspan=4, pady=5, sticky="we")
        frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")
       

       
            
        def insert_data(event=None):
            """
            Insertion method.
            """
            self.puffer[0]=f_name_entry.get()
            self.puffer[1]=organisation_entry.get()
            self.puffer[2]=f_typ_entry.get()
            self.puffer[3]=zf_entry.get()
            self.puffer[4]=gf_entry.get()
            self.puffer[5]=helfer_entry.get()
            self.puffer[6]=var.get()
            self.puffer[7]=ankunft_entry.get()
            self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
            self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
            for i in xrange(10,17):
                self.puffer[i]=""
            self.puffer[17]=atemschutz_entry.get()
            self.puffer[18]=csa_entry.get()
            self.puffer[19]=sanitaeter_entry.get()
            self.puffer[20]=loeschwasser_entry.get()
            self.puffer[21]=schaummittel_entry.get()

            #old_name=(self.puffer[0],)
            try:
                for i in xrange(0,10):
                    if self.puffer[i]=="" and (not i in (8,9)):
                        raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                for i in xrange(17,22):
                    if self.puffer[i]=="":
                        raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                print(self.puffer)              
                self.Bereitstellungsraum.add(self.puffer)
                t.destroy()
                #self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[8]))
                self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]))
            except Database_error as e:
                print("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except Input_error as g:
                print("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1=Tkinter.Toplevel(t)
                error1.wm_title("FEHLER")
                error1.focus()
                error1_label=Tkinter.Label(error1, text="FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1_label.pack()
                error1_button=Tkinter.Button(error1, text="OK", command=error1.destroy)
                error1_button.pack()
                t.wait_window(error1)

            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()

        submit_button = Tkinter.Button(t, text = "Hinzufügen", command=insert_data, default=Tkinter.ACTIVE)
        submit_button.grid(row = 13, column = 3, sticky = Tkinter.E)

        t.bind("<Return>", insert_data)

        t.grab_set()
        self.parent.wait_window(t)

############# end add_wind_fw()

    #same as for the add_rd window but for sonst
    def add_window_sonst(self):
        t = Tkinter.Toplevel(self)
        t.config(bg="deep sky blue")
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        self.clear_contacts()
        
        frame1=Tkinter.Frame(t)
        frame2=Tkinter.Frame(t)
        frame3=Tkinter.Frame(t)
        frame4=Tkinter.Frame(t)
        frame5=Tkinter.Frame(t)
        t.wm_title("Manuelles Hinzufügen von Fahrzeugen")
        #l = Tkinter.Label(t, text="This is window")
        #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
        #organisation_label.config(bg="white")
        organisation_entry = Tkinter.Entry(frame1, width=60)
        organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)

        organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        organisation_entry.grid(row = 0, column=1, columnspan = 3)        
        f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
        #f_name_label.config(bg="white")
        f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_name_entry.focus()
        #if what==1:
        #   f_name_entry.insert(0, selected_item.item(selected_item, )
        f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
        #f_name_label.config(bg="white")
        f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_name_entry.focus()
        #if what==1:
        #   f_name_entry.insert(0, selected_item.item(selected_item, )
        f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        f_name_entry.grid(row = 1, column=1, columnspan = 3)



        f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
        #f_typ_label.config(bg="white")
        f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
        f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
        f_typ_entry.grid(row = 2, column=1, columnspan = 2)

        kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
        kontakt_button.grid(row=2, column =3)
        

        personal_label = Tkinter.Label(frame2, text = "Besatzung:")
        #personal_label.config(bg="white")
        personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        zf_entry = Tkinter.Entry(frame2, width=3)
        zf_entry.insert(0, 0)
        zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
        gf_entry = Tkinter.Entry(frame2, width=3)
        gf_entry.insert(0, 0)
        gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
        helfer_entry = Tkinter.Entry(frame2, width=3)
        helfer_entry.insert(0, 0)
        helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))

        ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
        #ankunft_label.config(bg="white")
        ankunft_entry = Tkinter.Entry(frame5)
        ankunft_entry.insert(0, datetime.datetime.now())
        ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

        var = Tkinter.IntVar()
        check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
        #check.config(bg="white")
        check.grid(row=0, column=2, sticky=Tkinter.W) 

        sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
        #sonderbeladung_label.config(bg="white")
        sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
        sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W)

        bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
        #bemerkung_label.config(bg="white")
        bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
        bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



        frame1.config(pady=5, padx=10)
        frame2.config(width=200, pady=5, padx=10)
        frame3.config(pady=5, padx=10)
        frame4.config(pady=5, padx=10)
        frame5.config(pady=5, padx=10)

        add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"), fg="white")
        add_label.config(bg="deep sky blue")
        #add_label.grid(row=0, column=2, sticky=Tkinter.W)

        add_label.grid(row=0, column=0, columnspan=4)
        frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
        frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
        frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")

       

       
            
        def insert_data(event=None):
            """
            Insertion method.
            """
            self.puffer[0]=f_name_entry.get()
            self.puffer[1]=organisation_entry.get()
            self.puffer[2]=f_typ_entry.get()
            self.puffer[3]=zf_entry.get()
            self.puffer[4]=gf_entry.get()
            self.puffer[5]=helfer_entry.get()
            self.puffer[6]=var.get()
            self.puffer[7]=ankunft_entry.get()
            self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
            self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
            for i in xrange(10,22):
                self.puffer[i]=""

            try:
                for i in xrange(0,10):
                    if self.puffer[i]=="" and (not i in (8,9)):
                        raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                print(self.puffer)              
                self.Bereitstellungsraum.add(self.puffer)
                t.destroy()
                #self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[8]))
                self.br_treeview.insert('', 'end', values=(self.puffer[0],self.puffer[1], self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]))
            except Database_error as e:
                print("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except Input_error as g:
                print("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1=Tkinter.Toplevel(t)
                error1.wm_title("FEHLER")
                error1.focus()
                error1_label=Tkinter.Label(error1, text="FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1_label.pack()
                error1_button=Tkinter.Button(error1, text="OK", command=error1.destroy)
                error1_button.pack()
                t.wait_window(error1)

            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()

        submit_button = Tkinter.Button(t, text = "Hinzufügen", command=insert_data, default=Tkinter.ACTIVE)
        submit_button.grid(row = 13, column = 3, sticky = Tkinter.E)

        t.bind("<Return>", insert_data)

        t.grab_set()
        self.parent.wait_window(t)

############# end add_wind_sonst()
    
    # window for updating information of some given vehicle
    def update_window(self):
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.wm_title("Update von gewähltem Fahzeug")
        #l = Tkinter.Label(t, text="This is window")
        #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
        t.focus()
        # nested try/ excepts to make sure that exactly one vehicle is being updated
        try:
            selected_item = self.br_treeview.selection()
            try:
                print(self.br_treeview.item(selected_item[1]))
                print("FEHLER: Zu viele Fahrzeuge ausgewaehlt")
                fehler_label = Tkinter.Label(t, text= "FEHLER, zu viel Fahrzeuge ausgewählt!")
                fehler_label.pack()
                fehler_button = Tkinter.Button(t, text="OK", command=t.destroy)
                fehler_button.pack()
                return
            except Exception as e:
                print(self.br_treeview.item(selected_item[0])) #even though this is in an except block this is what happens if there is no error!!!!
        except IndexError as ex:
            print("FEHLER, kein Fahrzeug aus Liste gewaehlt")
            fehler_label = Tkinter.Label(t, text= "FEHLER, kein Fahrzeug aus Liste gewählt!")
            fehler_label.pack()
            fehler_button = Tkinter.Button(t, text="OK", command=t.destroy)
            fehler_button.pack()
            return
        
        # now we make the database querry to get the info on the vehicle
        p=self.Bereitstellungsraum.single((self.br_treeview.item(selected_item[0])['values'][0],))
        for i in xrange(22,27):
            self.puffer[i]=p[i+1]
        
        # try/except to make sure that we have a physical vehicle and not some kind of unit!
        try:
            
            # if/else to determine if rd/fw/sonst and what to show
            if p[2] in self.hiorgs:

                t.config(bg="white")
                frame1=Tkinter.Frame(t)
                frame2=Tkinter.Frame(t)
                frame3=Tkinter.Frame(t)
                frame4=Tkinter.Frame(t)
                frame5=Tkinter.Frame(t)

                organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
                #organisation_label.config(bg="white")
                organisation_entry = Tkinter.Entry(frame1, width=60)
                organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)

                organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                organisation_entry.grid(row = 0, column=1, columnspan = 3)


                f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
                #f_name_label.config(bg="white")
                f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_name_entry.focus()
                #if what==1:
                #   f_name_entry.insert(0, selected_item.item(selected_item, )
                f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                f_name_entry.grid(row = 1, column=1, columnspan = 3)


                f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
                #f_typ_label.config(bg="white")
                f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
                f_typ_entry.grid(row = 2, column=1, columnspan = 2)

                kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
                kontakt_button.grid(row=2, column =3)
                

                personal_label = Tkinter.Label(frame2, text = "Besatzung:")
                #personal_label.config(bg="white")
                personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                zf_entry = Tkinter.Entry(frame2, width=3)
                zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
                gf_entry = Tkinter.Entry(frame2, width=3)
                gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
                helfer_entry = Tkinter.Entry(frame2, width=3)
                helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))

                ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
                #ankunft_label.config(bg="white")
                ankunft_entry = Tkinter.Entry(frame5)
                #ankunft_entry.insert(0, datetime.datetime.now())
                ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

                var = Tkinter.IntVar()
                check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
                #check.config(bg="white")
                check.grid(row=0, column=2, sticky=Tkinter.W)

                notarzt_label = Tkinter.Label(frame2, text = "Notarzt:")
                #notarzt_label.config(bg="white")
                notarzt_entry = Tkinter.Entry(frame2, width=3)
                notarzt_label.grid(row = 0, column = 4, sticky = Tkinter.E)
                notarzt_entry.grid(row = 0, column = 5, padx=(0,20))

                arzt_label = Tkinter.Label(frame2, text = "Arzt:")
                #arzt_label.config(bg="white")
                arzt_entry = Tkinter.Entry(frame2, width=3)
                arzt_label.grid(row = 0, column = 6, sticky = Tkinter.W)
                arzt_entry.grid(row = 0, column = 7)

                notsan_label = Tkinter.Label(frame2, text = "NotSan + RettAss:")
                #notsan_label.config(bg="white")
                notsan_entry = Tkinter.Entry(frame2, width=3)
                notsan_label.grid(row = 1, column = 4, sticky = Tkinter.E)
                notsan_entry.grid(row = 1, column = 5, padx=(0,20))

                rs_label = Tkinter.Label(frame2, text = "RS:")
                #rs_label.config(bg="white")
                rs_entry = Tkinter.Entry(frame2, width=3)
                rs_label.grid(row = 1, column = 6, sticky = Tkinter.W)
                rs_entry.grid(row = 1, column = 7)

                trapo_label = Tkinter.Label(frame3, text = "Transportkapazität:")
                #trapo_label.config(bg="white")
                trapo_label.grid(row = 0, column = 0, sticky = Tkinter.W, padx=(0,85))

                liegend_label = Tkinter.Label(frame3, text = "liegend:")
                #liegend_label.config(bg="white")
                liegend_entry = Tkinter.Entry(frame3,width=3)
                liegend_label.grid(row = 0, column = 1, sticky = Tkinter.E)
                liegend_entry.grid(row = 0, column = 2, padx=(0,3))

                tragestuhl_label = Tkinter.Label(frame3, text = "Tragestuhl:")
                #tragestuhl_label.config(bg="white")
                tragestuhl_entry = Tkinter.Entry(frame3, width=3)
                tragestuhl_label.grid(row = 0, column = 3, sticky = Tkinter.E)
                tragestuhl_entry.grid(row = 0, column = 4, padx=(0,4))

                sitzend_label = Tkinter.Label(frame3, text = "sitzend:")
                #sitzend_label.config(bg="white")
                sitzend_entry = Tkinter.Entry(frame3, width=3)
                sitzend_label.grid(row = 0, column = 5, sticky = Tkinter.E)
                sitzend_entry.grid(row = 0, column = 6)       

                sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
                #sonderbeladung_label.config(bg="white")
                sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
                sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W)

                bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
                #bemerkung_label.config(bg="white")
                bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
                bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



                frame1.config(pady=5, padx=10)
                frame2.config(width=200, pady=5, padx=10)
                frame3.config(pady=5, padx=10)
                frame4.config(pady=5, padx=10)
                frame5.config(pady=5, padx=10)

                add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"))
                add_label.config(bg="white")
                #add_label.grid(row=0, column=2, sticky=Tkinter.W)

                add_label.grid(row=0, column=0, columnspan=4)
                frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
                frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
                frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
                frame3.grid(row=4, column=0, columnspan=4, pady=5, sticky="we")
                frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")

                f_name_entry.insert(0, p[1])
                organisation_entry.insert(0, p[2])
                f_typ_entry.insert(0,p[3])
                zf_entry.insert(0, p[4])
                gf_entry.insert(0,p[5])
                helfer_entry.insert(0,p[6])
                ankunft_entry.insert(0, p[8])
                notarzt_entry.insert(0,p[11])
                arzt_entry.insert(0,p[12])
                notsan_entry.insert(0,p[13])
                rs_entry.insert(0,p[14])
                liegend_entry.insert(0,p[15])
                tragestuhl_entry.insert(0,p[16])
                sitzend_entry.insert(0,p[17]) 
                bemerkung_entry.insert(Tkinter.INSERT,p[9])
                sonderbeladung_entry.insert(Tkinter.INSERT,p[10])
                var.set(p[7])     

            elif p[2] in self.fws:

                t.config(bg="red")
                frame1=Tkinter.Frame(t)
                frame2=Tkinter.Frame(t)
                frame3=Tkinter.Frame(t)
                frame4=Tkinter.Frame(t)
                frame5=Tkinter.Frame(t)

                #l = Tkinter.Label(t, text="This is window")
                #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
                organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
                #organisation_label.config(bg="white")
                organisation_entry = Tkinter.Entry(frame1, width=60)
                organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)
                organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                organisation_entry.grid(row = 0, column=1, columnspan = 3)


                f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
                #f_name_label.config(bg="white")
                f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_name_entry.focus()
                #if what==1:
                #   f_name_entry.insert(0, selected_item.item(selected_item, )
                f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
                #f_name_label.config(bg="white")
                f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_name_entry.focus()
                #if what==1:
                #   f_name_entry.insert(0, selected_item.item(selected_item, )
                f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                f_name_entry.grid(row = 1, column=1, columnspan = 3)




                f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
                #f_typ_label.config(bg="white")
                f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
                f_typ_entry.grid(row = 2, column=1, columnspan = 2)

                kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
                kontakt_button.grid(row=2, column =3)
                

                personal_label = Tkinter.Label(frame2, text = "Besatzung:")
                #personal_label.config(bg="white")
                personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                zf_entry = Tkinter.Entry(frame2, width=3)
                zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
                gf_entry = Tkinter.Entry(frame2, width=3)
                gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
                helfer_entry = Tkinter.Entry(frame2, width=3)
                helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))

                ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
                #ankunft_label.config(bg="white")
                ankunft_entry = Tkinter.Entry(frame5)
                #ankunft_entry.insert(0, datetime.datetime.now())
                ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

                var = Tkinter.IntVar()
                check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
                #check.config(bg="white")
                check.grid(row=0, column=2, sticky=Tkinter.W)

                atemschutz_label = Tkinter.Label(frame2, text = "Atemschutz:")
                #notarzt_label.config(bg="white")
                atemschutz_entry = Tkinter.Entry(frame2, width=3)
                atemschutz_label.grid(row = 0, column = 4, sticky = Tkinter.E)
                atemschutz_entry.grid(row = 0, column = 5, padx=(0,20))

                csa_label = Tkinter.Label(frame2, text = "CSA:")
                #arzt_label.config(bg="white")
                csa_entry = Tkinter.Entry(frame2, width=3)
                csa_label.grid(row = 0, column = 6, sticky = Tkinter.W)
                csa_entry.grid(row = 0, column = 7)


                sanitaeter_label = Tkinter.Label(frame2, text = "Sanitäter:")
                #rs_label.config(bg="white")
                sanitaeter_entry = Tkinter.Entry(frame2, width=3)
                sanitaeter_label.grid(row = 1, column = 6, sticky = Tkinter.W)
                sanitaeter_entry.grid(row = 1, column = 7)

                loeschwasser_label = Tkinter.Label(frame3, text = "Löschwasser:")
                #trapo_label.config(bg="white")
                loeschwasser_label.grid(row = 0, column = 0, sticky = Tkinter.W)

                loeschwasser_entry = Tkinter.Entry(frame3,width=15)

                loeschwasser_entry.grid(row = 0, column = 1, padx=(0,74))

                schaummittel_label = Tkinter.Label(frame3, text = "Schaummittel:")
                #tragestuhl_label.config(bg="white")
                schaummittel_entry = Tkinter.Entry(frame3, width=15)
                schaummittel_label.grid(row = 0, column = 2, sticky = Tkinter.E)
                schaummittel_entry.grid(row = 0, column = 3, padx=(0,4))
          
                sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
                #sonderbeladung_label.config(bg="white")
                sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
                sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W)

                bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
                #bemerkung_label.config(bg="white")
                bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
                bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



                frame1.config(pady=5, padx=10)
                frame2.config(width=200, pady=5, padx=10)
                frame3.config(pady=5, padx=10)
                frame4.config(pady=5, padx=10)
                frame5.config(pady=5, padx=10)

                add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"), fg="white")
                add_label.config(bg="red")
                #add_label.grid(row=0, column=2, sticky=Tkinter.W)

                add_label.grid(row=0, column=0, columnspan=4)
                frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
                frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
                frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
                frame3.grid(row=4, column=0, columnspan=4, pady=5, sticky="we")
                frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")
               
                f_name_entry.insert(0, p[1])
                organisation_entry.insert(0, p[2])
                f_typ_entry.insert(0,p[3])
                zf_entry.insert(0, p[4])
                gf_entry.insert(0,p[5])
                helfer_entry.insert(0,p[6])
                ankunft_entry.insert(0, p[8])
                atemschutz_entry.insert(0, p[18])
                csa_entry.insert(0, p[19])
                loeschwasser_entry.insert(0, p[21])
                schaummittel_entry.insert(0, p[22])
                sanitaeter_entry.insert(0, p[20])
                bemerkung_entry.insert(Tkinter.INSERT,p[9])
                sonderbeladung_entry.insert(Tkinter.INSERT,p[10])
                var.set(p[7])

            else:

                t.config(bg="deep sky blue")
                frame1=Tkinter.Frame(t)
                frame2=Tkinter.Frame(t)
                frame3=Tkinter.Frame(t)
                frame4=Tkinter.Frame(t)
                frame5=Tkinter.Frame(t)

                #l = Tkinter.Label(t, text="This is window")
                #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)
                organisation_label = Tkinter.Label(frame1, text = "Organisation:", font=("Arial", 12, "bold"))
                #organisation_label.config(bg="white")
                organisation_entry = Tkinter.Entry(frame1, width=60)
                organisation_entry.config(bg="lemon chiffon",relief=Tkinter.RIDGE)

                organisation_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                organisation_entry.grid(row = 0, column=1, columnspan = 3)   

                f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
                #f_name_label.config(bg="white")
                f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_name_entry.focus()
                #if what==1:
                #   f_name_entry.insert(0, selected_item.item(selected_item, )
                f_name_label = Tkinter.Label(frame1, text = "Funkrufname:", font=("Arial", 12, "bold"))
                #f_name_label.config(bg="white")
                f_name_entry = Tkinter.Entry(frame1, width=60,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_name_entry.focus()
                #if what==1:
                #   f_name_entry.insert(0, selected_item.item(selected_item, )
                f_name_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                f_name_entry.grid(row = 1, column=1, columnspan = 3)



                f_typ_label = Tkinter.Label(frame1, text = "Fahrzeugtyp:", font=("Arial", 12, "bold"))
                #f_typ_label.config(bg="white")
                f_typ_entry = Tkinter.Entry(frame1, width=45,bg="lemon chiffon",relief=Tkinter.RIDGE)
                f_typ_label.grid(row = 2, column = 0, sticky = Tkinter.W)
                f_typ_entry.grid(row = 2, column=1, columnspan = 2)

                kontakt_button = Tkinter.Button(frame1, text="Kontaktdaten", command=self.contact_window)
                kontakt_button.grid(row=2, column =3)
                

                personal_label = Tkinter.Label(frame2, text = "Besatzung:")
                #personal_label.config(bg="white")
                personal_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                zf_entry = Tkinter.Entry(frame2, width=3)
                zf_entry.grid(row = 0, column = 1, sticky= Tkinter.W)
                gf_entry = Tkinter.Entry(frame2, width=3)
                gf_entry.grid(row = 0, column = 2, sticky= Tkinter.W)
                helfer_entry = Tkinter.Entry(frame2, width=3)
                helfer_entry.grid(row = 0, column = 3, sticky= Tkinter.W, padx=(0,100))

                ankunft_label = Tkinter.Label(frame5, text = "Ankunftzeit:")
                #ankunft_label.config(bg="white")
                ankunft_entry = Tkinter.Entry(frame5)
                #ankunft_entry.insert(0, datetime.datetime.now())
                ankunft_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                ankunft_entry.grid(row = 0, column = 1, padx=(0,100))

                var = Tkinter.IntVar()
                check=Tkinter.Checkbutton(frame5, text="Führung", variable=var)
                #check.config(bg="white")
                check.grid(row=0, column=2, sticky=Tkinter.W) 

                sonderbeladung_label = Tkinter.Label(frame4, text = "Sonderbeladung:")
                #sonderbeladung_label.config(bg="white")
                sonderbeladung_entry = Tkinter.Text(frame4, height=5, width=40)
                sonderbeladung_label.grid(row = 0, column = 0, sticky = Tkinter.W)
                sonderbeladung_entry.grid(row = 0, column = 1, columnspan=7, sticky=Tkinter.W)

                bemerkung_label = Tkinter.Label(frame4, text = "Bemerkungen:")
                #bemerkung_label.config(bg="white")
                bemerkung_entry = Tkinter.Text(frame4, height=5, width=40)
                bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
                bemerkung_entry.grid(row = 1, column = 1, columnspan=7, sticky=Tkinter.W)



                frame1.config(pady=5, padx=10)
                frame2.config(width=200, pady=5, padx=10)
                frame3.config(pady=5, padx=10)
                frame4.config(pady=5, padx=10)
                frame5.config(pady=5, padx=10)

                add_label= Tkinter.Label(t, text="E-VISITENKARTE", font=("Arial", 20, "bold"), fg="white")
                add_label.config(bg="deep sky blue")
                #add_label.grid(row=0, column=2, sticky=Tkinter.W)

                add_label.grid(row=0, column=0, columnspan=4)
                frame1.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
                frame5.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")
                frame2.grid(row=3, column=0, columnspan=4, pady=5, sticky="we")
                frame4.grid(row=5, column=0, columnspan=4, pady=5, sticky="we")

                f_name_entry.insert(0, p[1])
                organisation_entry.insert(0, p[2])
                f_typ_entry.insert(0,p[3])
                zf_entry.insert(0, p[4])
                gf_entry.insert(0,p[5])
                helfer_entry.insert(0,p[6])
                ankunft_entry.insert(0, p[8])
                bemerkung_entry.insert(Tkinter.INSERT,p[9])
                sonderbeladung_entry.insert(Tkinter.INSERT,p[10])
                var.set(p[7])

                     


                
        except TypeError as e: # This happens if we do not have a physical vehicle but a unit!
            f_name_label = Tkinter.Label(t, text = "Funkrufname:")
            f_name_entry = Tkinter.Entry(t)
            f_name_label.grid(row = 0, column = 0, sticky = Tkinter.W)
            f_name_entry.grid(row = 0, column = 1)
            f_name_entry.insert(0, self.br_treeview.item(selected_item[0])['values'][0])

        # method to write the data into the database
        def insert_data(event=None):
            """
            Insertion method.
            """
            try:
                if organisation_entry.get() in self.hiorgs:
                    #print("in hiorgs?")
                    self.puffer[0]=f_name_entry.get()
                    self.puffer[1]=organisation_entry.get()
                    self.puffer[2]=f_typ_entry.get()
                    self.puffer[3]=zf_entry.get()
                    self.puffer[4]=gf_entry.get()
                    self.puffer[5]=helfer_entry.get()
                    self.puffer[6]=var.get()
                    self.puffer[7]=ankunft_entry.get()
                    self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
                    self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
                    self.puffer[10]=notarzt_entry.get()
                    self.puffer[11]=arzt_entry.get()
                    self.puffer[12]=notsan_entry.get()
                    self.puffer[13]=rs_entry.get()
                    self.puffer[14]=liegend_entry.get()
                    self.puffer[15]=tragestuhl_entry.get()
                    self.puffer[16]=sitzend_entry.get()
                    for i in xrange(17,22):
                        self.puffer[i]=""
                    for i in xrange(0,17):
                        if self.puffer[i]=="" and (not i in (8,9)):
                            self.puffer[i]=0
                    print(self.puffer)
                    self.Bereitstellungsraum.update(self.puffer,[p[1]])
                    t.destroy()
                    if not (self.br_treeview.parent(selected_item[0]) == '') and self.puffer[6]==1:
                        if self.br == "rd": 
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]),tags=('leader',))
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=('leader',))  
                    else:
                        if self.br == "rd":
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]), tags=())
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=())  

                elif organisation_entry.get() in self.fws:
                    self.puffer[0]=f_name_entry.get()
                    self.puffer[1]=organisation_entry.get()
                    self.puffer[2]=f_typ_entry.get()
                    self.puffer[3]=zf_entry.get()
                    self.puffer[4]=gf_entry.get()
                    self.puffer[5]=helfer_entry.get()
                    self.puffer[6]=var.get()
                    self.puffer[7]=ankunft_entry.get()
                    self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
                    self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
                    for i in xrange(10,16):
                        self.puffer[i]=""
                    self.puffer[17]=atemschutz_entry.get()
                    self.puffer[18]=csa_entry.get()
                    self.puffer[19]=sanitaeter_entry.get()
                    self.puffer[20]=loeschwasser_entry.get()
                    self.puffer[21]=schaummittel_entry.get()
                    #print("update vor Fehler suche")
                    for i in xrange(0,10):
                        if self.puffer[i]=="" and (not i in (8,9)):
                            raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                    for i in xrange(17,22):
                        if self.puffer[i]=="":
                            self.puffer[i]=0
                            #raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                    print(self.puffer)
                    self.Bereitstellungsraum.update(self.puffer,[p[1]])
                    t.destroy()
                    if not (self.br_treeview.parent(selected_item[0]) == '') and self.puffer[6]==1: 
                        if self.br == "rd": 
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]),tags=('leader',))
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=('leader',))  
                    else:
                        if self.br == "rd":
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]), tags=())
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=())  

                else:
                    self.puffer[0]=f_name_entry.get()
                    self.puffer[1]=organisation_entry.get()
                    self.puffer[2]=f_typ_entry.get()
                    self.puffer[3]=zf_entry.get()
                    self.puffer[4]=gf_entry.get()
                    self.puffer[5]=helfer_entry.get()
                    self.puffer[6]=var.get()
                    self.puffer[7]=ankunft_entry.get()
                    self.puffer[8]=bemerkung_entry.get("1.0",'end-1c')
                    self.puffer[9]=sonderbeladung_entry.get("1.0",'end-1c')
                    for i in xrange(10,22):
                        self.puffer[i]=""
                    for i in xrange(0,10):
                        if self.puffer[i]=="" and (not i in (8,9)):
                            self.puffer[i]=0
                            #raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                    print(self.puffer)
                    self.Bereitstellungsraum.update(self.puffer,[p[1]])
                    t.destroy()
                    if not (self.br_treeview.parent(selected_item[0]) == '') and self.puffer[6]==1: 
                        if self.br == "rd": 
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]),tags=('leader',))
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=('leader',))  
                    else:
                        if self.br == "rd":
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[8]), tags=())
                        else:
                            self.br_treeview.item(selected_item[0], values=(self.puffer[0],self.puffer[1],self.puffer[2], self.puffer[17], self.puffer[18], self.puffer[8]),tags=())  

                        
            except NameError as e:
            	
            	if (not f_name_entry.get()) or f_name_entry.get()=='':
                    pass
                else:    
                    self.br_treeview.item(selected_item[0], values=(f_name_entry.get(),'','', ''), tags=())
                    t.destroy()
            except Database_error as f:
                print("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im BR vorhanden \n Kontaktieren Sie die EAL!")
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except Input_error as g:
                print("FEHLER: Alle Felder, bis auf Bemerkungen müssen ausgefüllt werden!")
                error1=Tkinter.Toplevel(t)
                error1.wm_title("FEHLER")
                error1.focus()
                error1_label=Tkinter.Label(error1, text="FEHLER: Alle Felder, bis auf Bemerkungen, müssen ausgefüllt werden!")
                error1_label.pack()
                error1_button=Tkinter.Button(error1, text="OK", command=error1.destroy)
                error1_button.pack()
                t.wait_window(error1)

            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()
                
           
        submit_button = Tkinter.Button(t, text = "Übernehmen", command=insert_data)
        submit_button.grid(row = 13, column = 3, sticky = Tkinter.E)

        t.bind("<Return>", insert_data)
        t.grab_set()
        self.parent.wait_window(t)

    def auftrag_window(self):
        t = Tkinter.Toplevel(self)
        t.focus()
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.wm_title("Auftrag für gewählte Fahzeuge")
        #l = Tkinter.Label(t, text="This is window")
        #l.pack(side="top", fill="both", expand=True, padx=100, pady=100)

        try:
            selected_item = self.br_treeview.selection()
            print(self.br_treeview.item(selected_item[0]))
        except IndexError as ex:
            print("FEHLER, kein Fahrzeug aus Liste gewählt")
            fehler_label = Tkinter.Label(t, text= "FEHLER, kein Fahrzeug aus Liste gewählt")
            fehler_label.pack()
            fehler_button = Tkinter.Button(t, text="OK", command=t.destroy)
            fehler_button.pack()
            return
        print(selected_item)
        ziel_label = Tkinter.Label(t, text = "Ziel:")
        ziel_entry = Tkinter.Entry(t)
        ziel_entry.focus()
        ziel_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        ziel_entry.grid(row = 0, column = 1, sticky = Tkinter.W)
        bemerkung_label = Tkinter.Label(t, text = "Bemerkungen:")
        bemerkung_entry = Tkinter.Text(t, height=5, width=40)
        bemerkung_label.grid(row = 1, column = 0, sticky = Tkinter.W)
        bemerkung_entry.grid(row = 1, column = 1, columnspan=2)

        var = Tkinter.IntVar()
        Tkinter.Checkbutton(t, text="Direkt entsenden", variable=var).grid(row=2, column=1, sticky=Tkinter.W)

        def up_and_del(item):
            up=self.br_treeview.parent(item)
            try:
                if self.br_treeview.item(item)['values'][0] in self.einheiten_dict and not self.br_treeview.get_children(item): 
                    del self.einheiten_dict[self.br_treeview.item(item)['values'][0]]
                    self.br_treeview.delete(item)
                    up_and_del(up)
            except IndexError as e:
                pass

        def auftrag_erteilen(event=None):
            try:
                if (not ziel_entry.get()) or ziel_entry.get()=="":
                    raise Input_error("FEHLER: Ziel angeben!")
                else:
                
                    for x in self.br_treeview.selection():
                        try:
                            upper=self.br_treeview.parent(x)
                        except:
                            pass
                        #print(self.br_treeview.item(x))
                        if var.get()==0:
                        #self.issued_treeview.insert('', 'end', values=(self.br_treeview.item(x)['values'][0],ziel_entry.get(), self.br_treeview.item(x)['values'][1], bemerkung_entry.get()))
                    	    move(x,'')
                        else:
                            try:
                                del self.einheiten_dict[self.br_treeview.item(x)['values'][0]]
                            except KeyError as e:
                                pass
                            direct_move(x)
                        try:
                            self.br_treeview.delete(x)
                        except:
                            pass
                        up_and_del(upper)
                    t.destroy()
            except Input_error as e:
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Ziel angeben!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
                
        submit_button = Tkinter.Button(t, text = "Auftrag erteilen", command=auftrag_erteilen)
        submit_button.grid(row = 2, column = 2, sticky = Tkinter.W)

        def move(item,parent): #is recursive
            try:
                x=self.br_treeview.get_children(item)
                y=self.issued_treeview.insert(parent, 'end', values=(self.br_treeview.item(item)['values'][0],ziel_entry.get(), self.br_treeview.item(item)['values'][2], bemerkung_entry.get("1.0",'end-1c')))
                self.Bereitstellungsraum.set_assignment(self.br_treeview.item(item)['values'][0])
                for k in x:
                    move(k,y)
            except:
                pass
        def direct_move(item): #is recursive
            try:
                x=self.br_treeview.get_children(item)
                for k in x:
                    direct_move(k)
                    #self.Bereitstellungsraum.remove((self.br_treeview.item(k)['values'][0],datetime.datetime.now(), ziel_entry.get(), bemerkung_entry.get("1.0",'end-1c')))        		
                self.Bereitstellungsraum.remove((self.br_treeview.item(item)['values'][0],datetime.datetime.now(), ziel_entry.get(), bemerkung_entry.get("1.0",'end-1c')))
                try:
                    del self.einheiten_dict[self.br_treeview.item(item)['values'][0]]
                except KeyError as e:
                    pass
            except:
                pass

            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()
        t.bind("<Return>", auftrag_erteilen)
        t.grab_set()
        self.parent.wait_window(t)

    def group_window(self):
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.wm_title("Einheiten gruppieren")
        t.focus()

        try:
            selected_item = self.br_treeview.selection()
            #print(self.br_treeview.item(selected_item[0]))
        except IndexError as ex:
            print("FEHLER, kein Fahrzeug aus Liste gewählt")
            fehler_label = Tkinter.Label(t, text= "FEHLER, kein Fahrzeug aus Liste gewählt")
            fehler_label.pack()
            fehler_button = Tkinter.Button(t, text="OK", command=t.destroy)
            fehler_button.pack()
            return
        einheiten_liste=self.einheiten_dict.values()
        einheit_label = Tkinter.Label(t, text="zu Einheit hinzufügen")
        einheit_label.grid(row = 0, column = 0, sticky = Tkinter.W)
        print(einheiten_liste)
		
        einheit_entry = Autocomplete(t)
        einheit_entry.grid(row = 0, column = 1)
        einheit_entry.set_verv_liste(einheiten_liste)
        einheit_entry.focus()

        def group(event=None):
            try:
                if (not einheit_entry.get()) or einheit_entry.get()=="":
                    print("FEHLER: Einheit angeben werden!")
                    raise Input_error("FEHLER: Einheit angeben werden!")
                else:
                    if not (einheit_entry.get() in einheiten_liste):
                        self.einheiten_dict.update({einheit_entry.get():einheit_entry.get()})
                        print(self.einheiten_dict)
                        self.br_treeview.insert('', 'end', einheit_entry.get(), values=(einheit_entry.get(),"", "", ""),open=1)
                    #print("Auswahl:", selected_item)
                    for k in selected_item:
                        #print("Children:", self.br_treeview.get_children(k))
                        for child in self.br_treeview.get_children(k):
                            if child in selected_item:
                                #print("Warum passiert das hier nicht?")
                                raise Group_error("FEHLER: Wählen Sie nur Einheiten und nicht-gruppierte Fahrzeuge aus!")
                        try:    
                            if self.Bereitstellungsraum.single((self.br_treeview.item(k)['values'][0],))[7]==1 : # Abfrage, ob Fahrzeug ein Führungsfahrzeug ist
                                self.br_treeview.item(k,tags=('leader',))
                                self.br_treeview.move(k, einheit_entry.get(), '0')
                            else:
                                self.br_treeview.move(k, einheit_entry.get(), 'end')
                        except TypeError as e:
                            try:
                                self.br_treeview.move(k, einheit_entry.get(), 'end')
                            except TclError as e:
                                pass
                    t.destroy()
            except Input_error as e:
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Keine Einheit angegeben!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except Group_error as f:
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Wählen Sie nur Einheiten und nicht-gruppierte Fahrzeuge aus!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            except NameError as g:
                error=Tkinter.Toplevel(t)
                error.wm_title("FEHLER")
                error.focus()
                error_label=Tkinter.Label(error, text="FEHLER: Einheit kann sich nicht selbst enthalten!")
                error_label.pack()
                error_button=Tkinter.Button(error, text="OK", command=error.destroy)
                error_button.pack()
                t.wait_window(error)
            
        group_button=Tkinter.Button(t, text='Hinzufügen', command=group)
        group_button.grid(row = 2, column = 1)
        

        t.bind("<Return>", group)
        t.grab_set()
        self.parent.wait_window(t)




    def release(self):
        def up_and_del(item):
            up=self.br_treeview.parent(item)
            try:
                if self.br_treeview.item(item)['values'][0] in self.einheiten_dict and not self.br_treeview.get_children(item): 
                    del self.einheiten_dict[self.br_treeview.item(item)['values'][0]]
                    self.br_treeview.delete(item)
                    up_and_del(up)
            except IndexError as e:
                pass
        def do_release(item):
            upper=self.br_treeview.parent(item)
            #print(upper)
            for i in self.br_treeview.get_children(item):
                do_release(i)
                
            if not (upper==''):
                print("hello, upper isnot root")
                try:
                    if self.Bereitstellungsraum.single((self.br_treeview.item(item)['values'][0],))[7]==1 : # Abfrage, ob Fahrzeug ein Führungsfahrzeug ist
                        self.br_treeview.item(item,tags=('',))
                    self.br_treeview.move(item, '', 0)
                    up_and_del(upper)
                except:
                    pass
        selected_item = self.br_treeview.selection()
        for k in selected_item:
            print(k)
            do_release(k)


    def read_database(self):
        for x in self.Bereitstellungsraum.read_current(True):
            self.upstart_buffer.append(x)
            if self.br == "rd":
                self.br_treeview.insert('', 'end', text='', values=(x[1],x[2], x[3],x[9]))
            else:
                self.br_treeview.insert('', 'end', text='', values=(x[1],x[2], x[3], x[18], x[19], x[9]))
        print(self.upstart_buffer)


    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
               self.treeview_sort_column(tv, col, not reverse))

    def leave_window(self):
        t= Tkinter.Toplevel(self)
        t.wm_title("Einheiten verlassen Bereitstellungsraum")
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        t.focus()
        try:
            selected_item = self.issued_treeview.selection()
            print(self.issued_treeview.item(selected_item[0]))
        except IndexError as ex:
            print("FEHLER, kein Fahrzeug aus Warteschlange gewählt")
            fehler_label = Tkinter.Label(t, text= "FEHLER, kein Fahrzeug aus Warteschlange gewählt")
            fehler_label.pack()
            fehler_button = Tkinter.Button(t, text="OK", command=t.destroy)
            fehler_button.pack()
            return
        leave_label=Tkinter.Label(t, text="Haben die ausgewählten Fahrzeuge den Bereitstellungsraum verlassen?")

        def up_and_del(item):
            up=self.issued_treeview.parent(item)
            try:
                if self.issued_treeview.item(item)['values'][0] in self.einheiten_dict and not self.issued_treeview.get_children(item): 
                    del self.einheiten_dict[self.issued_treeview.item(item)['values'][0]]
                    self.issued_treeview.delete(item)
                    up_and_del(up)
            except IndexError as e:
                pass

        def do_leave(item):
            try:
                del self.einheiten_dict[self.issued_treeview.item(item)['values'][0]]
                print(self.einheiten_dict)
            except KeyError as e:
                pass
            x=self.issued_treeview.get_children(item)
            for i in x:
                do_leave(i)
            self.Bereitstellungsraum.remove((self.issued_treeview.item(item)['values'][0],datetime.datetime.now(), self.issued_treeview.item(item)['values'][1], self.issued_treeview.item(item)['values'][3]))
            self.issued_treeview.delete(item)

        def leave(event=None): # is recursive
            print("HELLO from leave")
            for k in selected_item:
                try:
                    upper=self.issued_treeview.parent(k)
                except:
                    pass
                do_leave(k)
                up_and_del(upper)
            t.destroy()
            self.update_type_lists()
            self.helfer=self.Bereitstellungsraum.get_persons()
            self.agt=self.Bereitstellungsraum.get_agt()

        leave_yes = Tkinter.Button(t, text="JA", command=leave)
        leave_no = Tkinter.Button(t, text="NEIN", command=t.destroy)

        leave_label.grid(row=0,column=0,columnspan=2)
        leave_yes.grid(row=1, column=0)
        leave_no.grid(row=1, column=1)

    def modify_api(self): #expects a tuple with 8 entries as input
        self.is_true=False;
        self.parent_of_del=""
        def up_and_del(item):
            up=self.issued_treeview.parent(item)
            try:
                if self.issued_treeview.item(item)['values'][0] in self.einheiten_dict and not self.issued_treeview.get_children(item): 
                    del self.einheiten_dict[self.issued_treeview.item(item)['values'][0]]
                    self.issued_treeview.delete(item)
                    up_and_del(up)
            except IndexError as e:
                pass

        def do_leave(item, string): 

            if self.issued_treeview.item(item)['values'][0]==string:
                self.Bereitstellungsraum.remove((self.issued_treeview.item(item)['values'][0],datetime.datetime.now(), self.issued_treeview.item(item)['values'][1], self.issued_treeview.item(item)['values'][3]))
                self.parent_of_del=self.issued_treeview.parent(item)
                self.issued_treeview.delete(item)
                self.is_true=True 
                
                
            else:
                print("does this happen?") 
                children=self.issued_treeview.get_children(item)
                for y in children:
                    do_leave(y, string)
            # try:
            #     del self.einheiten_dict[self.issued_treeview.item(item)['values'][0]]
            #     print(self.einheiten_dict)

            # except KeyError as e:
            #     pass
            # x=self.issued_treeview.get_children(item)
            # for i in x:
            #     do_leave(i)
            # self.Bereitstellungsraum.remove((self.issued_treeview.item(item)['values'][0],datetime.datetime.now(), self.issued_treeview.item(item)['values'][1], self.issued_treeview.item(item)['values'][3]))
            # self.issued_treeview.delete(item)


  

        #print("add_api is called")
        if self.r_queue.full():
            print("recieving queue!")
            tupel=self.r_queue.get_nowait()
            #print(tupel)
            tupell=[]
            is_true=False
            for i in xrange(0,7):
                tupell.append(tupel[i])
            tupell.append(unicode(datetime.datetime.now()))
            for i in xrange(7,26):
                tupell.append(tupel[i])
            #tupell= (tupel[0], tupel[1], tupel[2], tupel[3], tupel[4], tupel[5], tupel[6], unicode(datetime.datetime.now()), tupel[7])
            
            print(tupell)
            
            
            if not self.Bereitstellungsraum.single((tupel[0],)) == None:
                print("Fahrzeug in Database")

                issued=self.issued_treeview.get_children("")
                print(issued)
                for x in issued:
                    do_leave(x,tupel[0])
                    print("do leave finished")
                    print(self.parent_of_del) 
                    up_and_del(self.parent_of_del)
                    print(self.is_true)


                # issued=self.issued_treeview.get_children("")
                # print(issued)
                # for x in issued:
                #     print("looping durch issued")
                #     if self.issued_treeview.item(x)['values'][0] == tupel[0]: 
                #         upper=self.issued_treeview.parent(x)
                #         do_leave(x)
                #         up_and_del(upper)
                #         is_true=True
    
                if self.is_true is False:
                    print("FEHLER: Fahrzeug mit diesem Rufnamen ist bereits im Bereitstellungsraum vorhanden!")
                    self.s_queue.put_nowait("Error2")
                    return False
                else:
                    self.s_queue.put_nowait("Success")
                    self.update_type_lists()    
                    self.helfer=self.Bereitstellungsraum.get_persons()
                    self.agt=self.Bereitstellungsraum.get_agt()           
                    return True


            try:
                if tupel[1] in self.hiorgs:
                    for i in xrange(0,6):
                        if tupel[i]=="" :
                            self.s_queue.put_nowait("Error1")
                            raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, muessen ausgefuellt werden!")
                elif tupel[2] in self.fws:
                    for i in xrange(0,6):
                        if tupel[i]=="" :
                            self.s_queue.put_nowait("Error1")
                            raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, muessen ausgefuellt werden!")
                    # for i in xrange(16,21):
                    #     if tupel[i]=="" :
                    #         self.s_queue.put_nowait("Error1")
                    #         raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, muessen ausgefuellt werden!")
                else:
                    for i in xrange(0,6):
                        if tupel[i]=="" :
                            self.s_queue.put_nowait("Error1")
                            raise Input_error("FEHLER: Alle Felder, bis auf Bemerkungen, muessen ausgefuellt werden!")
         
                self.Bereitstellungsraum.add(tupell)
                if self.br == "rd":
                    self.br_treeview.insert('', 'end', values=(tupell[0],tupell[1], tupell[2], tupell[8]))
                else:
                    self.br_treeview.insert('', 'end', values=(tupell[0],tupell[1], tupell[2], tupell[17], tupell[18], tupell[8]))
                self.s_queue.put_nowait("Success")
                self.update_type_lists()
                self.helfer=self.Bereitstellungsraum.get_persons()
                self.agt=self.Bereitstellungsraum.get_agt()
                return True
                            
            except Input_error as g:
                print("FEHLER: Alle Felder, bis auf Bemerkungen, muessen ausgefuellt werden!")
                #print(datetime.datetime.now)
                return False
            

    def kind_of(self):
        def set_rd():
            self.br="rd"
            t.destroy()
        def set_fw():
            self.br="fw"
            t.destroy()
        def set_gm():
            self.br="gm"
            t.destroy()
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        mid_frame = Tkinter.Frame(t)
        t.focus()
        t.attributes('-topmost', True)
        t.wm_title("Art des Bereitstellungsraums")
        label=Tkinter.Label(mid_frame, text="Welche Art von Bereitstellungsraum wollen Sie führen?")
        rd = Tkinter.Button(mid_frame, text="Rettungsdienst", command=set_rd)
        fw = Tkinter.Button(mid_frame, text="Feuerwehr", command=set_fw)
        gm = Tkinter.Button(mid_frame, text="Gemischt", command=set_gm)


        w = 500 # width for the Tk root
        h = 200 # height for the Tk root
        # get screen width and height
        ws = t.winfo_screenwidth() # width of the screen
        hs = t.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        t.geometry('%dx%d+%d+%d' % (w, h, x, y))


        label.pack()
        rd.pack()
        fw.pack()
        gm.pack()

        mid_frame.pack(expand=1)

        self.parent.wait_window(t)

    def name_it(self):
        def ok(event=None):
            if not name_entry.get()=="":
                self.newname=name_entry.get()
                t.destroy()

        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        mid_frame = Tkinter.Frame(t)
        t.focus()
        t.attributes('-topmost', True)
        t.wm_title("Name des Bereitstellungsraums")
        label=Tkinter.Label(mid_frame, text="Bennenen Sie den Bereitstellungsraum")
        name_entry = Tkinter.Entry(mid_frame)
        ok_button=Tkinter.Button(mid_frame, text="OK", command=ok)

        w = 500 # width for the Tk root
        h = 200 # height for the Tk root
        # get screen width and height
        ws = t.winfo_screenwidth() # width of the screen
        hs = t.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        t.geometry('%dx%d+%d+%d' % (w, h, x, y))


        label.pack()
        name_entry.pack()
        ok_button.pack()
 
        mid_frame.pack(expand=1)

        self.parent.wait_window(t)


    def search_tree(self, tree, item, name):
        def up_and_del(iitem):
            up=tree.parent(iitem)
            try:
                if tree.item(iitem)['values'][0] in self.einheiten_dict and not tree.get_children(iitem): 
                    del self.einheiten_dict[tree.item(iitem)['values'][0]]
                    tree.delete(iitem)
                    up_and_del(up)
            except IndexError as e:
                pass


        x = tree.get_children(item)
        for y in x:
            upper=tree.parent(y)
            search_tree(tree, y, name)
            if self.issued_treeview.item(y)['values'][0] == name:
                do_leave(y)
                up_and_del(upper)       
        
    def help_window(self):
        t = Tkinter.Toplevel(self)
        if sys.platform =="win32":
            t.iconbitmap("ELW_Frontend/images/Logo.ico")
        plus_label= Tkinter.Label(t, text="Hinzufügen", font=("Calibri", 12))
        plus_erkl = Tkinter.Label(t, text="Manuelles Hinzufügen von Fahrzeugen zum Bereitstellungsraum", font=("Calibri", 12))
        bearb_label = Tkinter.Label(t, text="Bearbeiten", font=("Calibri", 12))
        bearb_erkl  = Tkinter.Label(t, text="Manuelles Bearbeiten eines Fahrzeugs im Bereitstellungsraum", font=("Calibri", 12))
        group_label = Tkinter.Label(t, text="Gruppieren", font=("Calibri", 12))
        group_erkl = Tkinter.Label(t, text="Zusammenfassen von Fahrzeugen zu einer taktischen Einheit", font=("Calibri", 12))
        aufl_label = Tkinter.Label(t, text="Auflösen", font=("Calibri", 12))
        aufl_erkl = Tkinter.Label(t, text="Auflösen einer taktischen Einheit", font=("Calibri", 12))
        druck_label = Tkinter.Label(t, text="Lagemeldung", font=("Calibri", 12))
        druck_erkl = Tkinter.Label(t, text="Drucken aller im Bereitstellungsraum befindlichen Fahrzeuge in PDF und eine CSV Datei", font=("Calibri", 12))
        prot_label= Tkinter.Label(t, text="Protokoll", font=("Calibri", 12))
        prot_erkl = Tkinter.Label(t, text="Drucken der bisherigen Historie des Bereitstellungsraum in ein PDF und eine CSV Datei", font=("Calibri",12))
        auft_label = Tkinter.Label(t, text="Auftrag", font=("Calibri", 12))
        auft_erkl = Tkinter.Label(t, text="Einem Fahrzeug oder einer Einheit im Bereitstellungsraum einen Auftrag zuweisen", font=("Calibri", 12))
        verl_label = Tkinter.Label(t, text="Verlassen", font=("Calibri", 12))
        verl_erkl = Tkinter.Label(t, text="Manuelles Entfernen eines Fahrzeugs/ einer Einheit aus dem Bereitstellungsraum", font=("Calibri", 12))

        plus_label.grid(row=1, column=0, sticky="w")
        plus_erkl.grid(row=1, column=1, sticky="w")
        bearb_label.grid(row=2, column=0, sticky="w")
        bearb_erkl.grid(row=2, column=1, sticky="w")
        group_label.grid(row=3, column=0, sticky="w")
        group_erkl.grid(row=3, column=1, sticky="w")
        aufl_label.grid(row=4, column=0, sticky="w")
        aufl_erkl.grid(row=4, column=1, sticky="w")
        druck_label.grid(row=5, column=0, sticky="w")
        druck_erkl.grid(row=5, column=1, sticky="w")
        prot_label.grid(row=6, column=0, sticky="w")
        prot_erkl.grid(row=6, column=1, sticky="w")
        auft_label.grid(row=7, column=0, sticky="w")
        auft_erkl.grid(row=7, column=1, sticky="w")
        verl_label.grid(row=8, column=0, sticky="w")
        verl_erkl.grid(row=8, column=1, sticky="w")

    def update_type_lists(self):
        liste=self.Bereitstellungsraum.type_querry()
        self.fahrz_num=self.Bereitstellungsraum.count()

        print(liste)
        
        self.rd_types={"RTW" : 0, "KTW" : 0, "NEF" : 0, "GW-San" : 0}
        self.fw_types={"LF" : 0, "TLF" : 0, "RW" : 0, "DL" : 0}

        for x in liste:
            typ= x[0]

            print(typ)

            rtw = re.search('RTW|MZF', typ)
            ktw = re.search('KTW', typ)
            nef = re.search('NEF', typ)
            gw  = re.search('GW-San', typ)

            rw  = re.search('RW', typ)
            dl  = re.search('DL', typ)

            lf  = re.search('LF', typ)

            if rtw:
                self.rd_types["RTW"]+=1
            elif ktw:
                self.rd_types["KTW"]+=1
            elif nef:
                self.rd_types["NEF"]+=1
            elif gw:
                self.rd_types["GW-San"]+=1
            elif rw:
                self.fw_types["RW"]+=1
            elif dl:
                self.fw_types["DL"]+=1
            elif lf:
                if re.search('TLF', typ):
                    self.fw_types["TLF"]+=1
                else:
                    self.fw_types["LF"]+=1
            else:
                pass
        
        print(self.rd_types)
        print(self.fw_types)


class MyDialog:

    def __init__(self, parent):

        top = self.top = Tkinter.Toplevel(parent)
        if sys.platform =="win32":
            top.iconbitmap("ELW_Frontend/images/Logo.ico")

        mid_frame = Tkinter.Frame(top)

        #Tkinter.Label(mid_frame, text="Vorführversion für den hessischen KatS-Preis", font=("Calibri", 12,"bold")).grid(row=0, column=0, columnspan=3)
        Tkinter.Label(mid_frame, text="Bereitstellungsraum aus Datenbank übernehmen?").grid(row=1, column=0, columnspan=3)
        top.attributes('-topmost', True)
        self.new_datab=0

        y = Tkinter.Button(mid_frame, text="JA", command=self.yes)
        y.grid(row=2, column=0)

        n = Tkinter.Button(mid_frame, text="NEIN", command=self.no)
        n.grid(row=2,column=2)

        mid_frame.pack(expand=1)
        w = 500 # width for the Tk root
        h = 200 # height for the Tk root
        # get screen width and height
        ws = parent.winfo_screenwidth() # width of the screen
        hs = parent.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))



       
    def yes(self):

        self.top.destroy()

    def no(self):
        topper = Tkinter.Toplevel(self.top)
        if sys.platform =="win32":
            topper.iconbitmap("ELW_Frontend/images/Logo.ico")
        topper.attributes('-topmost', True)
        topper.wm_title("Bestätigen")
        topper.focus()
        validate_label=Tkinter.Label(topper, text="Zum Bestätigen bitte LOESCHEN eingeben")
        validate_entry=Tkinter.Entry(topper)
        

        validate_label.pack()
        validate_entry.pack()
        
        
        def validate(event=None):
            if validate_entry.get() == "LOESCHEN":
                self.new_datab=1
            topper.destroy()
            self.top.destroy()

        validate_button=Tkinter.Button(topper, text="OK", command=validate)
        validate_button.pack()

        topper.grab_set()
        self.top.wait_window(topper)


   


class Input_error(Exception):
    pass
class Group_error(Exception):
    pass
