import tkinter as tk
from tkinter import *
from tkinter import ttk
import datetime
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk

LARGE_FONT = ("Verdana", 12)
ALARM_FILE ="alarms.txt"

class APP(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, NewAlarm):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)  
        label.pack(pady=10, padx=10)

        self.label = tk.Label(self, font=('arial'))
        self.label.place(relx=1, rely=0, anchor="ne" )

        self.update_time()

        button = tk.Button(self, text="Visit Page 1",
                           command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()

    def update_time(self):
        current_time = datetime.datetime.now()
        currenttime = current_time.strftime('%H:%M:%S %m/%d/%Y')
        self.label.config(text=currenttime)
        self.label.after(1000, self.update_time)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()


def load_file():
    try:
        with open(ALARM_FILE, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        label = tk.Label(self,text = "ALARM")
        label.place(relx = 0.5, rely = 0.5 , anchor = "center")

        button1 = tk.Button(self, text="Back to Home",
                    command=lambda: controller.show_frame(StartPage))
        button1.place(relx=0, rely=0, anchor="nw", x=65, y=0)
        button2 = tk.Button(self, text="Page One",
                    command=lambda: controller.show_frame(PageOne))
        button2.place(relx=0, rely=0, anchor="nw", x=0, y=0)

        photo = Image.open("add.png")
        resized_image = photo.resize((50, 50)) 
        self.resized_image = ImageTk.PhotoImage(resized_image)
        add = Button(self, image=self.resized_image ,command=lambda:controller.show_frame(NewAlarm))
        add.place(relx = 1, rely = 1 , anchor = "se" , x = -100 , y =-100)

        refresh_button = tk.Button(self, text="Refresh Alarms", command=self.display_alarms)
        refresh_button.pack(pady=5)

        self.alarms_display = tk.Text(self, height=10, width=30)
        self.alarms_display.pack(pady=10)
        
        self.display_alarms()

    def display_alarms(self):
        alarms = load_file()
        self.alarms_display.delete(1.0, tk.END)  
        if alarms:
            for alarm in alarms:
                self.alarms_display.insert(tk.END, alarm) 
        else:
            self.alarms_display.insert(tk.END, "No alarms set yet.\n")

def save_file(alarms):
        with open(ALARM_FILE, "a") as file :
            for alarm_time in alarms:
                file.write(alarm_time + "\n")

class NewAlarm(tk.Frame) :
        
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) 
        self.controller = controller

        self.hour = tk.StringVar(self)
        self.minute = tk.StringVar(self)
        
        tk.Label (self , text = "select the time:" ).pack()

        hours = ttk.Combobox(self, textvariable = self.hour)
        hours.pack()
        minutes = ttk.Combobox(self, textvariable = self.minute)
        minutes.pack()

        hours['values']= [str(i).zfill(2) for i in range(24)]
        minutes['values'] = [str(i).zfill(2) for i in range(60)]
        
        submit_button = tk.Button(self, text="Save Alarm", command=self.switch )
        submit_button.pack()

    def switch(self) :
        self.save_alarm()
        self.controller.show_frame(PageTwo)

    def save_alarm(self):
        selected_hour = self.hour.get()
        selected_minute = self.minute.get()

        if selected_hour and selected_minute: 
            alarm_time = f"{selected_hour}:{selected_minute}"
            save_file([alarm_time])  
        else:
            print("press select ")


app = APP()

app.title("Reminders")

app.geometry("500x500")
app.mainloop()
