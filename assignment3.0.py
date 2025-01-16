import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox
import threading
from pygame import mixer  
import os
from tkcalendar import DateEntry
import time
import winsound


ALARM_FILE = "alarms.txt"
SOUNDS_FILE = "sounds.txt"

COLOR1 = "#F5EFFF"  
COLOR2 = "#E5D9F2"  
COLOR3 = "#CDC1FF"  
COLOR4 = "#A294F9"  

class APP(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("MY APP")
        self.geometry("600x500")

        mixer.init()

        container = tk.Frame(self, bg = COLOR1)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, NewAlarm, EditAlarmWindow):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        self.check_alarms()

    def show_frame(self, cont): 
        frame = self.frames[cont]
        frame.tkraise()

    def trigger_alarm(self, sound_file):
        try:
            if not os.path.exists(sound_file):
                raise FileNotFoundError(f"Sound file not found: {sound_file}")

            mixer.music.load(sound_file)
            mixer.music.play(-1)  
            messagebox.showinfo("Alarm!", "It's time!")  
            mixer.music.stop()  
        except FileNotFoundError as fnf_error:
            messagebox.showerror("File Not Found", str(fnf_error))
        except Exception as e:
            messagebox.showerror("Error", f"Could not play sound: {e}")

    def check_alarms(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        alarms = load_alarms()
        for alarm_time, sound_file in alarms:
            if alarm_time.strip() == current_time:
                self.trigger_alarm(sound_file.strip())
                break   
        self.after(60000, self.check_alarms) 

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=COLOR1) 
        label = tk.Label(self, text="MY APP", font=("Times New Roman", 36, "bold"), fg="black", bg=COLOR1)
        label.place(relx=0.5, rely=0.2, anchor="center")

        self.time_label = tk.Label(self, font=("Times New Roman", 16, "italic"), fg="black", bg=COLOR1)
        self.time_label.place(relx=1.0, rely=0.0, anchor="ne") 

        self.update_time()

        button1 = tk.Button(self, text="Visit Reminder App", command=lambda: controller.show_frame(PageOne), bg=COLOR2, fg="black")
        button1.place(relx=0.5, rely=0.5, anchor="center", y=-20)

        button2 = tk.Button(self, text="Visit Alarm App", command=lambda: controller.show_frame(PageTwo), bg=COLOR2, fg="black")
        button2.place(relx=0.5, rely=0.5, anchor="center", y=20)

    def update_time(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.after(1000, self.update_time)

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#add8e6")

        self.reminders = []
        self.current_edit_index = None
        self.file_path = "reminders.txt"

        self.load_reminders()
        self.create_widgets()

        self.alarm_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.alarm_thread.start()

    def create_widgets(self):
        title_label = tk.Label(self, text="Reminder App", font=("Verdana", 16), bg="#add8e6", fg="black")
        title_label.pack(pady=10)

        entry_frame = tk.Frame(self, bg="#add8e6")
        entry_frame.pack(pady=10)

        tk.Label(entry_frame, text="Title:", font=("Verdana", 12), bg="#add8e6").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.title_entry = tk.Entry(entry_frame, width=40, font=("Verdana", 10))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(entry_frame, text="Date:", font=("Verdana", 12), bg="#add8e6").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = DateEntry(entry_frame, width=20, font=("Verdana", 10), date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(entry_frame, text="Time (HH:MM):", font=("Verdana", 12), bg="#add8e6").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.time_entry = tk.Entry(entry_frame, width=15, font=("Verdana", 10))
        self.time_entry.grid(row=2, column=1, padx=5, pady=5)

        self.am_pm_var = tk.StringVar(value="AM")
        am_pm_options = ["AM", "PM"]
        self.am_pm_dropdown = ttk.Combobox(entry_frame, textvariable=self.am_pm_var, values=am_pm_options, width=5, font=("Verdana", 10))
        self.am_pm_dropdown.grid(row=2, column=2, padx=5, pady=5)

        tk.Label(entry_frame, text="Category:", font=("Verdana", 12), bg="#add8e6").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        category_options = ["Task", "Appointment", "Important Event"]
        self.category_dropdown = ttk.Combobox(entry_frame, textvariable=self.category_var, values=category_options, state="readonly", width=20, font=("Verdana", 10))
        self.category_dropdown.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self, text="Description (Optional):", font=("Verdana", 12), bg="#add8e6").pack(pady=5)
        self.description_text = tk.Text(self, height=5, width=50, font=("Verdana", 10))
        self.description_text.pack(pady=10)

        buttons_frame = tk.Frame(self, bg="#add8e6")
        buttons_frame.pack(pady=10)

        add_button = tk.Button(buttons_frame, text="Add Reminder", command=self.add_reminder, bg="green", fg="white", font=("Verdana", 12))
        add_button.grid(row=0, column=0, padx=5)

        edit_button = tk.Button(buttons_frame, text="Edit Selected", command=self.edit_reminder, bg="blue", fg="white", font=("Verdana", 12))
        edit_button.grid(row=0, column=1, padx=5)

        delete_button = tk.Button(buttons_frame, text="Delete Selected", command=self.delete_reminder, bg="red", fg="white", font=("Verdana", 12))
        delete_button.grid(row=0, column=2, padx=5)

        self.reminder_listbox = tk.Listbox(self, font=("Verdana", 12), width=50, height=10)
        self.reminder_listbox.pack(pady=10)
        self.reminder_listbox.bind("<ButtonRelease-1>", self.show_reminder_details)
        self.update_reminder_listbox()

        button = tk.Button(self, text="Back to Home", command=lambda: self.controller.show_frame(StartPage), bg=COLOR4, fg="black")
        button.pack()


    def add_reminder(self):
        title = self.title_entry.get()
        date = self.date_entry.get()
        time = self.time_entry.get()
        am_pm = self.am_pm_var.get()
        category = self.category_var.get()
        description = self.description_text.get("1.0", "end-1c").strip()

        if not title or not date or not time or not am_pm or not category:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        try:
            reminder_datetime = f"{date} {time} {am_pm}"
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid time format. Please enter in HH:MM AM/PM format.")
            return

        reminder = f"{title}|{reminder_datetime}|{category}|{description}\n"
        self.reminders.append(reminder)
        self.save_reminders()
        self.update_reminder_listbox()
        self.clear_entries()

    def load_reminders(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.reminders = file.readlines()

    def save_reminders(self):
        with open(self.file_path, "w") as file:
            file.writelines(self.reminders)

    def update_reminder_listbox(self):
        self.reminder_listbox.delete(0, tk.END)
        for reminder in self.reminders:
            title, datetime_str, category, _ = reminder.split("|")
            self.reminder_listbox.insert(tk.END, f"{title} - {datetime_str} - {category}")

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.date_entry.set_date(datetime.datetime.now())
        self.time_entry.delete(0, tk.END)
        self.am_pm_var.set("AM")
        self.category_var.set("")
        self.description_text.delete("1.0", "end")

    def edit_reminder(self):
        selected_index = self.reminder_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a reminder to edit.")
            return

        self.current_edit_index = selected_index[0]
        reminder = self.reminders[self.current_edit_index]
        title, datetime_str, category, description = reminder.split("|")

        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        date, time, am_pm = datetime_str.split(" ")
        self.date_entry.set_date(datetime.datetime.strptime(date, "%d/%m/%Y"))
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, time)
        self.am_pm_var.set(am_pm)

        self.category_var.set(category)
        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", description.strip())

    def delete_reminder(self):
        selected_index = self.reminder_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Selection Error", "Please select a reminder to delete.")
            return

        self.reminders.pop(selected_index[0])
        self.save_reminders()
        self.update_reminder_listbox()

    def show_reminder_details(self, event):
        selected_index = self.reminder_listbox.curselection()
        if not selected_index:
            return

        reminder = self.reminders[selected_index[0]]
        title, datetime_str, category, description = reminder.split("|")

        detail_window = tk.Toplevel(self)
        detail_window.title("Reminder Details")
        detail_window.geometry("400x300")
        detail_window.configure(bg="#add8e6")

        tk.Label(detail_window, text=f"Title: {title}", font=("Verdana", 12), bg="#add8e6").pack(pady=10)
        tk.Label(detail_window, text=f"Date: {datetime_str.split(' ')[0]}", font=("Verdana", 12), bg="#add8e6").pack(pady=5)
        tk.Label(detail_window, text=f"Time: {datetime_str.split(' ')[1]} {datetime_str.split(' ')[2]}", font=("Verdana", 12), bg="#add8e6").pack(pady=5)
        tk.Label(detail_window, text=f"Category: {category}", font=("Verdana", 12), bg="#add8e6").pack(pady=5)
        tk.Label(detail_window, text="Description:", font=("Verdana", 12), bg="#add8e6").pack(pady=5)
        tk.Label(detail_window, text=description.strip(), font=("Verdana", 10), bg="#add8e6").pack(pady=5)

        tk.Button(detail_window, text="Close", command=detail_window.destroy, bg="gray", fg="white", font=("Verdana", 12)).pack(pady=10)

    def check_alarms(self):
        while True:
            now = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
            for reminder in self.reminders:
                title, datetime_str, category, description = reminder.split("|")
                if now == datetime_str and not hasattr(reminder, "triggered"):
                    self.trigger_alarm(title, datetime_str, category)
                    reminder.triggered = True
            time.sleep(30)

    def trigger_alarm(self, title, datetime_str, category):
        winsound.Beep(440, 1000)
        messagebox.showinfo("Reminder", f"Title: {title}\nTime: {datetime_str}\nCategory: {category}")



def load_alarms():
    try:
        with open(ALARM_FILE, "r") as file:
            return [line.strip().split("|") for line in file.readlines()]
    except FileNotFoundError:
        return []


def save_alarm(alarm_time, sound_file):
    alarms = load_alarms()
    for existing_time, _ in alarms:
        if existing_time == alarm_time:
            messagebox.showwarning("Duplicate Alarm", f"An alarm for {alarm_time} already exists.")
            return
    with open(ALARM_FILE, "a") as file:
        file.write(f"{alarm_time}|{sound_file}\n")

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Alarm Page", font=("Verdana", 12))
        label.pack(pady=10, padx=10)

        self.alarm_listbox = tk.Listbox(self, height=10, width=50)
        self.alarm_listbox.pack(pady=10)

        refresh_button = tk.Button(self, text="Refresh Alarms", command=self.display_alarms)
        refresh_button.pack(pady=5)

        delete_button = tk.Button(self, text="Delete Selected Alarm", command=self.delete_alarm)
        delete_button.pack(pady=5)

        edit_button = tk.Button(self, text="Edit Selected Alarm", command=self.edit_alarm)
        edit_button.pack(pady=5)

        new_alarm_button = tk.Button(self, text="Add New Alarm",
                                      command=lambda: controller.show_frame(NewAlarm))
        new_alarm_button.pack(pady=5)

        home_button = tk.Button(self, text="Back to Home",
                                command=lambda: controller.show_frame(StartPage))
        home_button.pack(pady=5)

        self.display_alarms()

    def display_alarms(self):
        alarms = load_alarms()
        self.alarm_listbox.delete(0, tk.END)
        if alarms:
            for alarm_time, sound_file in alarms:
                self.alarm_listbox.insert(tk.END, f"{alarm_time} - {os.path.basename(sound_file)}")
        else:
            self.alarm_listbox.insert(tk.END, "No alarms set yet.")

    def delete_alarm(self):
        selected_alarm_index = self.alarm_listbox.curselection()
        if selected_alarm_index:
            alarm_line = self.alarm_listbox.get(selected_alarm_index)
            alarm_time = alarm_line.split(" - ")[0]
            self.remove_alarm_from_file(alarm_time.strip())
            self.display_alarms()
        else:
            messagebox.showwarning("Warning", "No alarm selected to delete.")

    def remove_alarm_from_file(self, alarm_to_remove):
        alarms = load_alarms()
        with open(ALARM_FILE, "w") as file:
            for alarm_time, sound_file in alarms:
                if alarm_time != alarm_to_remove:
                    file.write(f"{alarm_time}|{sound_file}\n")

    def edit_alarm(self):
        selected_alarm_index = self.alarm_listbox.curselection()
        if not selected_alarm_index:
            messagebox.showwarning("Warning", "No alarm selected to edit.")
            return

        alarm_line = self.alarm_listbox.get(selected_alarm_index)
        alarm_time, sound_file = alarm_line.split(" - ")[0], alarm_line.split(" - ")[1]

        controller = self.master.master  
        edit_frame = controller.frames[EditAlarmWindow]
        edit_frame.set_alarm_data(alarm_time.strip(), sound_file.strip())
        controller.show_frame(EditAlarmWindow)



class NewAlarm(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.sound_file = tk.StringVar(self)

        label = tk.Label(self, text="Set a New Alarm", font=("Verdana", 12))
        label.pack(pady=10, padx=10)

        self.hour = tk.StringVar(self)
        self.minute = tk.StringVar(self)

        tk.Label(self, text="Hour:").pack()
        hours = ttk.Combobox(self, textvariable=self.hour, width=5)
        hours.pack()
        hours['values'] = [str(i).zfill(2) for i in range(24)]

        tk.Label(self, text="Minute:").pack()
        minutes = ttk.Combobox(self, textvariable=self.minute, width=5)
        minutes.pack()
        minutes['values'] = [str(i).zfill(2) for i in range(60)]

        self.folder = os.path.join(os.getcwd(), 'alarm')  
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
        self.filelist = [fname for fname in os.listdir(self.folder) if fname.endswith('.mp3')]

        tk.Label(self, text="Choose Ringtone:").pack()
        self.sound_selector = ttk.Combobox(self, value=self.filelist, width=30)
        self.sound_selector.pack()

        save_button = tk.Button(self, text="Save Alarm", command=self.save_alarm)
        save_button.pack(pady=5)

        back_button = tk.Button(self, text="Back to Alarm Page",
                                command=lambda: controller.show_frame(PageTwo))
        back_button.pack(pady=5)
    

    def refresh_sound_list(self):
        self.filelist = [fname for fname in os.listdir(self.folder) if fname.endswith('.mp3')]
        self.sound_selector['values'] = self.filelist

    def save_alarm(self):
        selected_hour = self.hour.get()
        selected_minute = self.minute.get()
        selected_sound = self.sound_selector.get()
        if selected_hour and selected_minute and selected_sound:
            alarm_time = f"{selected_hour}:{selected_minute}"
            save_alarm(alarm_time, os.path.join(self.folder, selected_sound))
            messagebox.showinfo("Success", f"Alarm set for {alarm_time} ")
            self.controller.show_frame(PageTwo)
        else:
            messagebox.showerror("Error", "Please select a valid time and Ringtone.")


class EditAlarmWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.alarm_time = None
        self.sound_file = None

        tk.Label(self, text="Edit Time:").pack(pady=5)
        self.hour = tk.StringVar()
        self.minute = tk.StringVar()

        hours = ttk.Combobox(self, textvariable=self.hour, width=5)
        hours.pack()
        hours['values'] = [str(i).zfill(2) for i in range(24)]

        minutes = ttk.Combobox(self, textvariable=self.minute, width=5)
        minutes.pack()
        minutes['values'] = [str(i).zfill(2) for i in range(60)]

        tk.Label(self, text="Change Ringtone:").pack(pady=5)
        self.sound_selector = ttk.Combobox(self, width=30)
        self.sound_selector.pack()

        tk.Button(self, text="Save Changes", command=self.save_changes).pack(pady=10)
        tk.Button(self, text="Cancel", command=lambda: controller.show_frame(PageTwo)).pack(pady=10)

    def refresh_sound_list(self):
        folder = os.path.join(os.getcwd(), 'alarm')  
        if not os.path.exists(folder):
            os.makedirs(folder)
        filelist = [fname for fname in os.listdir(folder) if fname.endswith('.mp3')]
        self.sound_selector['values'] = filelist

    def set_alarm_data(self, alarm_time, sound_file):
        self.alarm_time = alarm_time
        self.sound_file = sound_file
        self.hour.set(alarm_time.split(":")[0])
        self.minute.set(alarm_time.split(":")[1])
        self.refresh_sound_list()
        self.sound_selector.set(os.path.basename(sound_file))

class EditAlarmWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.alarm_time = None
        self.sound_file = None

        label_time = tk.Label(self, text="Edit Time:")
        label_time.pack(pady=5)

        self.hour = tk.StringVar()
        self.minute = tk.StringVar()

        hours = ttk.Combobox(self, textvariable=self.hour, width=5)
        hours.pack()
        hours['values'] = [str(i).zfill(2) for i in range(24)]

        minutes = ttk.Combobox(self, textvariable=self.minute, width=5)
        minutes.pack()
        minutes['values'] = [str(i).zfill(2) for i in range(60)]

        label_sound = tk.Label(self, text="Change Ringtone:")
        label_sound.pack(pady=5)

        self.sound_selector = ttk.Combobox(self, width=30)
        self.sound_selector.pack()

        save_button = tk.Button(self, text="Save Changes", command=self.save_changes)
        save_button.pack(pady=10)
        
        cancel_button = tk.Button(self, text="Cancel", command=lambda: controller.show_frame(PageTwo))
        cancel_button.pack(pady=10)

    def refresh_sound_list(self):
        folder = os.path.join(os.getcwd(), 'alarm') 
        filelist = [fname for fname in os.listdir(folder) if fname.endswith('.mp3')]
        self.sound_selector['values'] = filelist

    def set_alarm_data(self, alarm_time, sound_file):
        self.alarm_time = alarm_time
        self.sound_file = sound_file
        self.hour.set(alarm_time.split(":")[0])
        self.minute.set(alarm_time.split(":")[1])
        self.refresh_sound_list()
        self.sound_selector.set(os.path.basename(sound_file))  

    def save_changes(self):
        new_hour = self.hour.get()
        new_minute = self.minute.get()
        new_sound = self.sound_selector.get()

        if not new_hour or not new_minute or not new_sound:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        new_time = f"{new_hour}:{new_minute}"
        alarms = load_alarms()  
        folder = os.path.join(os.getcwd(), 'alarm') 
        new_sound_path = os.path.join(folder, new_sound)

        updated_alarms = []
        alarm_found = False

        print("Existing alarms:", alarms)
        print(f"Editing alarm: {self.alarm_time}, {self.sound_file.strip()}")

        for time, sound in alarms:
            print(f"Checking alarm: {time}, {sound.strip()}")
            if time == self.alarm_time and os.path.basename(sound.strip()) == os.path.basename(self.sound_file.strip()):
                updated_alarms.append((new_time, new_sound_path))
                alarm_found = True
            else:
                updated_alarms.append((time, sound))

        if not alarm_found:
            messagebox.showerror("Error", "Original alarm not found.")
            print("Failed to find and match the alarm.")
            return

        with open(ALARM_FILE, "w") as file:
            for time, sound in updated_alarms:
                file.write(f"{time}|{sound}\n")

        messagebox.showinfo("Success", "Alarm updated successfully!")
        self.controller.frames[PageTwo].display_alarms()  
        self.controller.show_frame(PageTwo)

if __name__ == "__main__":
    app = APP()
    app.mainloop()

