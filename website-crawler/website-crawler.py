from requests import get, exceptions
from sys import exit as ext
from re import findall
from urllib.parse import urljoin


def get_urls(url):
    with open('./directories.txt', 'r') as file:
        for line in file:
            try:
                new_url = url + '/' + line.strip()
                response = get(new_url)
                if response:
                    print('\t[!]-----> Url found: ' + new_url)
                    get_links(new_url, response.content)
            except exceptions.ConnectionError:
                pass


def get_website_info(url):
    with open('./domains.txt', 'r') as file:
        for line in file:
            try:
                domain_url = 'https://' + line.strip() + "." + url
                response = get(domain_url)
                if response:
                    print("\n[+] Subdomain Discovered: " + domain_url)
                    get_urls(domain_url)

            except exceptions.ConnectionError:
                pass
            except KeyboardInterrupt:
                ext()


def get_links(url, content):
    links = set(findall('(?:href=")(.*?)"', content.decode()))
    for link in links:
        link = urljoin(url, link)
        if url in link:
            print("\t\t[*]-----> Link found: " + link)


get_website_info("facebook.com")
