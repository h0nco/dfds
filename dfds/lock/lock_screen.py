import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from .usbkey import verify_key, load_backup, KEY_FILENAME

class USBBlocker:
    def __init__(self, expected_key, rescue_password):
        self.expected_key = expected_key
        self.rescue_password = rescue_password
        self.unlocked = False
        self.root = None

    def check_usb(self):
        while not self.unlocked:
            for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                usb_path = f"{drive_letter}:\\"
                if Path(usb_path).exists() and verify_key(self.expected_key, usb_path):
                    self.unlocked = True
                    return
            time.sleep(2)

    def on_rescue(self, entry, window):
        pwd = entry.get()
        key = load_backup(pwd)
        if key == self.expected_key:
            self.unlocked = True
            window.destroy()
        else:
            messagebox.showerror("Error", "Wrong rescue password")
            entry.delete(0, tk.END)

    def show_screen(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: None)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        label = tk.Label(
            self.root,
            text="SYSTEM LOCKED\n\nInsert USB key containing " + KEY_FILENAME,
            fg='white', bg='black', font=('Arial', 24)
        )
        label.pack(expand=True)

        frame = tk.Frame(self.root, bg='black')
        frame.pack(pady=20)
        tk.Label(frame, text="Rescue password:", fg='white', bg='black').pack(side=tk.LEFT)
        entry = tk.Entry(frame, show='*', width=30)
        entry.pack(side=tk.LEFT, padx=10)
        btn = tk.Button(frame, text="Unlock", command=lambda: self.on_rescue(entry, self.root))
        btn.pack(side=tk.LEFT)

        t = threading.Thread(target=self.check_usb, daemon=True)
        t.start()

        def check_unlock():
            if self.unlocked:
                self.root.destroy()
            else:
                self.root.after(500, check_unlock)
        self.root.after(500, check_unlock)

        self.root.mainloop()

def run_usb_lock(expected_key, rescue_password):
    blocker = USBBlocker(expected_key, rescue_password)
    blocker.show_screen()