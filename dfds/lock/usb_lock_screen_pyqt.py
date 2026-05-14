import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from dfds.lock.usbkey import verify_key, load_backup
from dfds.usb_detector import find_usb_with_key
from dfds.config_loader import load_config

config = load_config()
USB_KEY_FILENAME = config['usb_key_filename']

class USBBlocker(QWidget):
    def __init__(self, expected_key, rescue_password):
        super().__init__()
        self.expected_key = expected_key
        self.rescue_password = rescue_password
        self.unlocked = False
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
        label = QLabel(f"SYSTEM LOCKED\n\nInsert USB key containing {USB_KEY_FILENAME}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(label)
        hbox = QHBoxLayout()
        pwd_label = QLabel("Rescue password:")
        pwd_label.setStyleSheet("color: white;")
        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.Password)
        self.entry.returnPressed.connect(self.try_unlock)
        unlock_btn = QPushButton("Unlock")
        unlock_btn.clicked.connect(self.try_unlock)
        hbox.addWidget(pwd_label)
        hbox.addWidget(self.entry)
        hbox.addWidget(unlock_btn)
        layout.addLayout(hbox)
        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_usb)
        self.timer.start(2000)
        self.check_usb_thread = threading.Thread(target=self.check_usb_loop, daemon=True)
        self.check_usb_thread.start()

    def check_usb_loop(self):
        while not self.unlocked:
            usb_path = find_usb_with_key()
            if usb_path and verify_key(self.expected_key, usb_path):
                self.unlocked = True
                QApplication.quit()
            time.sleep(2)

    def check_usb(self):
        if self.unlocked:
            QApplication.quit()

    def try_unlock(self):
        pwd = self.entry.text()
        if load_backup(pwd) == self.expected_key:
            self.unlocked = True
            QApplication.quit()
        else:
            self.entry.clear()
            self.entry.setPlaceholderText("Wrong password")

def run_usb_lock(expected_key, rescue_password):
    app = QApplication(sys.argv)
    blocker = USBBlocker(expected_key, rescue_password)
    sys.exit(app.exec_())