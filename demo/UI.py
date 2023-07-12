# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
import tkinter as tk
from tkinter import ttk
from inspect import stack
import time
from multiprocessing import Pipe
import cv2
from PIL import Image, ImageTk

class UI():
    def __init__(self, pipesend, piperecv):
        self.root = tk.Tk() 
        self.pipesend = pipesend
        self.piperecv = piperecv
        self.exitFlag = False
        self.create()

    def pause_main_loop(self, delay_ms):
        self.root.after(delay_ms, self.root.quit)

    def create(self):
        self.root.geometry("920x300")
        self.root.resizable(0, 0)
        Background = tk.Frame(self.root, background="white")
        Background.pack( fill="both", expand=True)
        self.root.bind('<KeyPress>', self.KeyPressEvent)

        #--------------------------------------------------------------------
        #-----------------------------Camera Frame---------------------------
        #--------------------------------------------------------------------

        self.CameraImg= tk.Label(self.root, image= ImageTk.PhotoImage(Image.open("img.jpg")))
        self.CameraImg.place(x=220,y=130, height=120, width=200, in_=self.root)

        #--------------------------------------------------------------------
        #-----------------------------Speed Freame---------------------------
        #--------------------------------------------------------------------

        slider_label = tk.Label(self.root, text='Speed reference', background="white", borderwidth=0)
        slider_label.place(x=5, y=100, width = 140, height = 20, in_=self.root)
        PlusSpeed=tk.Button(self.root, text="+",command=self.plusSpeed)
        PlusSpeed.place(x=55, y=135, width = 30, height = 20, in_=self.root)
        self.Speedslider=tk.Scale(self.root, from_=5.0, to=-5.0, command=self.slidingSpeed, sliderlength=10, resolution=0.1 )
        self.Speedslider.place(x=45, y=160, width = 50, height = 100, in_=self.root)
        self.Speedslider.set(0.0)
        MinusSpeed=tk.Button(self.root, text="-",command=self.minusSpeed)
        MinusSpeed.place(x=55, y=265, width = 30, height = 20, in_=self.root)
        Brake=tk.Button(self.root, text="Brake",command=self.Brake)
        Brake.place(x=100, y=400, width = 50, height = 20, in_=self.root)

        #--------------------------------------------------------------------
        #-----------------------------Steering Frame-------------------------
        #--------------------------------------------------------------------

        slider_label = tk.Label(self.root, text='Steering reference', background="white", borderwidth=0)
        slider_label.place(x=230, y=5, width = 140, height = 20, in_=self.root)
        MinusSteer=tk.Button(self.root, text="-",command=self.minusSteer)
        MinusSteer.place(x=175, y=45, width = 20, height = 30, in_=self.root)
        self.Steerslider=tk.Scale(self.root,from_=-20, to=+20, orient="horizontal", command=self.slidingSteer)
        self.Steerslider.place(x=200, y=40, width = 200, height = 40, in_=self.root)
        self.Steerslider.set(0)
        PlusSteer=tk.Button(self.root, text="+",command=self.plusSteer)
        PlusSteer.place(x=405, y=45, width = 20, height = 30, in_=self.root)

        #--------------------------------------------------------------------
        #-----------------------------Start engine Frame---------------------
        #--------------------------------------------------------------------

        self.startEngineButton=tk.Button(self.root, text="Start engine", command=self.startEngine, background="red", state="disabled")
        self.startEngineButton.place(x=560, y=260, width = 100, height = 30, in_=self.root)

        #--------------------------------------------------------------------
        #-----------------------------Topics Frame---------------------------
        #--------------------------------------------------------------------

        TopicsBox = tk.Frame(self.root, background="Yellow")
        TopicsBox.place(x=470, y=10, width=425, height=222, in_=self.root)
        
        self.my_game = ttk.Treeview(TopicsBox, selectmode='none')
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.my_game.yview)
        vsb.place(x=895, y=35, height=197)

        self.my_game.configure(yscrollcommand=vsb.set)

        self.my_game['columns'] = ('Package', 'Value')
        self.my_game['show'] = 'headings'

        self.my_game.column("#0", width=0,  stretch=tk.NO)
        self.my_game.column("Package", width=150)
        self.my_game.column("Value",anchor=tk.CENTER,width=320)

        self.my_game.heading("#0",text="",anchor=tk.CENTER)
        self.my_game.heading("Package",text="Package",anchor=tk.CENTER)
        self.my_game.heading("Value",text="Value",anchor=tk.CENTER)

        self.my_game.insert(parent='',index='end', iid=1,    values=('IN_IMU',              'pending'))
        self.my_game.insert(parent='',index='end', iid=2,    values=('IN_LOCSYS_POS',       'pending'))
        self.my_game.insert(parent='',index='end', iid=3,    values=('SYS_INSTANT_CON',     'pending'))
        self.my_game.insert(parent='',index='end', iid=4,    values=('SYS_BATTERY_LVL',     'pending'))
        self.my_game.insert(parent='',index='end', iid=5,    values=('SYS_ENGINE_OPE',      'pending'))
        self.my_game.insert(parent='',index='end', iid=6,    values=('SYS_ENGINE_RUN',      'pending'))
        self.my_game.insert(parent='',index='end', iid=7,    values=('IN_MOBILE_VEH',       'pending'))
        self.my_game.insert(parent='',index='end', iid=8,    values=('IN_SEMAPHORE',        'pending'))         

        self.my_game.pack()

    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    # Speed section. Deals with everything that has to do with speed setup.
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def plusSpeed(self):
        speed = self.Speedslider.get()+0.1
        if speed>5: speed=5
        self.setSpeed(speed)

    def minusSpeed(self):
        speed = self.Speedslider.get()-0.1
        if speed<-5: speed-5
        self.setSpeed(speed)

    def slidingSpeed(self, val):
        self.setSpeed(val)

    def Brake(self):
        self.setSpeed(0.0)

    def setSpeed(self, val):
        if not (stack()[1].function == "plusSpeed" or stack()[1].function =="minusSpeed" or stack()[1].function =="Brake"):
            data = {"aciton": "speed", "value":val}
            self.pipesend.send(data)
        self.Speedslider.set(val)
                
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    # Steering section. Deals with everything that has to do with steering setup.
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def plusSteer(self):
        steer = self.Steerslider.get()+1
        if steer>20: steer=20
        self.setSteer(steer)

    def minusSteer(self):
        steer = self.Steerslider.get()-1
        if steer<-5: steer-5
        self.setSteer(steer)

    def slidingSteer(self, val):
        self.setSteer(val)

    def setSteer(self, val):
        if not (stack()[1].function == "plusSteer" or stack()[1].function =="minusSteer"):
            data = {"aciton": "steer", "value":val}
            self.pipesend.send(data)
        self.Steerslider.set(val)
     
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    # Starts the engine.
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def enableStartEngine(self, value):
        if value == False:
            self.startEngineButton.config(state="disabled")
            self.startEngineButton.config(background="red")
        else:
            self.startEngineButton.config(state="active")
            time.sleep(0.1)
            self.startEngineButton.config(background="red")
            
    def startEngine(self):
        temp = self.startEngineButton.cget('bg')
        if temp =="red": 
            self.startEngineButton.config(background="green")
            started = True
        else: 
            self.startEngineButton.config(background="red")
            started = False

        data = {"aciton": "startEngine", "value":started}
        self.pipesend.send(data)

    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    # Keyboard functions for control.
    #--------------------------------------------------------------------
    #--------------------------------------------------------------------

    def KeyPressEvent(self, e):
        if e.keysym == "Up": 
            self.plusSpeed()
        elif e.keysym == "Down": 
            self.minusSpeed()
        elif e.keysym == "Right": 
            self.plusSteer()
        elif e.keysym == "Left": 
            self.minusSteer()
        elif e.keysym == "space": 
            self.Brake()

    #--------------------------------------------------------------------
    #--------------------------------------------------------------------
    # Data fill.
    #--------------------------------------------------------------------
    #-------------------------------------------------------------------- 

    def emptyAll(self):
        for row_id in self.my_game.get_children():
            i, r = self.my_game.item(row_id)["values"]
            updated_values = (id, "pending")
            self.my_game.item(row_id, values=updated_values)

    def modifyTable(self, data):
        id,value= data
        if self.root.winfo_exists():
            for row_id in self.my_game.get_children():
                i, r = self.my_game.item(row_id)["values"]
                if i == id: 
                    updated_values = (id, value)
                    self.my_game.item(row_id, values=updated_values)
                    break
            else:
                ida = int(row_id)+1
                self.my_game.insert(parent='',index='end' ,iid=ida, values=(id, value))

    def modifyImage(self, img):
        try:
            img_np = cv2.imdecode(img, cv2.IMREAD_COLOR)
            pil_image = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
            tk_image=ImageTk.PhotoImage(pil_image)
            self.CameraImg.config(image=tk_image)
            self.root.update()
        except Exception : 
            print(Exception)

    def continous_update(self):
        if self.piperecv.poll():
            msg = self.piperecv.recv()
            if msg['action'] == 'modImg':
                self.modifyImage(msg['value'])
            elif msg['action'] == "enableStartEngine": 
                self.enableStartEngine(msg['value'])
            elif msg['action'] == "emptyAll": 
                self.emptyAll()
            elif msg['action'] == 'modTable':
                self.modifyTable(msg['value'])
        self.root.after(0,self.continous_update)

if __name__ == "__main__":

    allProcesses = list()
    piperecv, pipesend = Pipe(duplex=False)
    piperecva, pipesenda = Pipe(duplex=False)
    server_thread = UI(pipesend)
    allProcesses.append(server_thread)

    print("Starting the processes!",allProcesses)
    for proc in allProcesses:
        proc.start()

    server_thread.root.mainloop()
    
    for proc in allProcesses:
        if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
            print("Process with stop",proc)
            proc.stop()
            proc.join()
        else:
            print("Process witouth stop",proc)
            proc.terminate()
            proc.join()

    