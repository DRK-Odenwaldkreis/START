#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is the first version of the Software tool START for managing staging areas in
# the Odenwaldkreis with QR Codes scanned by Android Smartphones and a managing application
# in the ELW 1.
# This Software is specifically designed for the German Red Cross KV Odenwaldkreis e. V.

# START v 1.0

#Copyright Philipp Scior philipp.scior@drk-forum.de

import Tkinter
import ttk
from ELW_Backend.database import Database
from ELW_Frontend.gui import GUI, MyDialog
from ELW_Backend.backend import Middleware
from wsgiref.simple_server import make_server
import threading
import Queue
import sys

#redirects all output to a logfile. Necessary for using the .exe in Windows
#without producing error-logs
#sys.stdout = open('logfile.log', 'a')
sys.stderr = open('logfile.log', 'a')

# the queues for communicating between http server and gui
my_queue=Queue.Queue(maxsize=1)
your_queue=Queue.Queue(maxsize=1)


#method to start the server
def run_server(my_queue, your_queue):
    print("make server")
    httpd.serve_forever(poll_interval=0.5)


# method to savely shutdown all threads
def stop_all():
    root.destroy()
    threading.Thread(target=httpd.shutdown).start()

#method to show the ip of the pc in the program. Sofar, this only works for windows

#linux / macOS: look up own IP adress, e.g. using ifconfig and set ip manually inside
# the get_ip() method. Unfortunately this has to be hardcoded.
def get_ip():
    if sys.platform == "linux" or sys.platform == "linux2":
        #ip="ip check for Linux is not implemented yet"

        ip="127.0.0.1"
        print(ip)
    elif sys.platform == "darwin":
        #ip="ip check for MacOs is not implemented yet"
        ip="127.0.0.1"
    elif sys.platform == "win32":
        import wmi
        ip=wmi.WMI().Win32_NetworkAdapterConfiguration (IPEnabled=1)[0].IPAddress[0]
        print ip

    else:
        ip="ip check for this OS is not implemented yet"
        print(ip)
    return ip

ip=get_ip()

root=Tkinter.Tk()
if sys.platform =="win32":
    #root.iconbitmap("Grafiken\\Logo\\Logo.ico")
    root.iconbitmap("ELW_Frontend/images/Logo.ico")



# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

if ws < 1440:
    small=True
    w = 1000 # width for the Tk root
    h = 700 # height for the Tk root
else:
    small=False
    w = 1400 # width for the Tk root
    h = 700 # height for the Tk root



# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

root.title("START v 1.0")


# starting the upstart window
upstart=MyDialog(root)

upstart.top.attributes("-topmost", True)
root.wait_window(upstart.top)

# setting the database 
Bereitstellungsraum=Database(upstart.new_datab)

# starting the gui
d=GUI(root, Bereitstellungsraum, my_queue, your_queue, ip, small)

# starting the http server middleware
_application=Middleware(d, my_queue, your_queue)
application=_application.run
print(ip)
httpd = make_server(ip, 8051, application)
#httpd = make_server("192.168.178.20", 8051, application)

# start the http server in a different thread to avoid blocking
thread= threading.Thread(target=run_server, args=(my_queue, your_queue))
thread.deamon = False
thread.start()
print("what")

# let the gui listen to input from the http server
d.listen()

#method to close the main-window safely
root.protocol("WM_DELETE_WINDOW", stop_all)

#run the gui
root.mainloop()

