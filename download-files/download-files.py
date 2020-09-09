import requests


def download(url):
    filename = url.split('/')[-1]
    get_response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(get_response.content)


download("https://raw.githubusercontent.com/Webins/python-ethical-hacking/master/packet-sniffer/packet-sniffer.py")
