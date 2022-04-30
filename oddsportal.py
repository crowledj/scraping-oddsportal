import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import time
import json
import re

# define the functions
def get(url, method="default"):
    '''
    GET request functions
    :param url: str
    :param method: str, {"default","oddsportal"}
    :return soup/response_text: bs4 object or str
    '''
    if method == "default":
        h = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Safari/537.36'}
        r = requests.get(url, headers=h)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
    elif method == "oddsportal":
        h = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,pl;q=0.8",
            "referer": "https://www.oddsportal.com/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Safari/537.36"
        }
        r = requests.get(url, headers=h)
        if r.status_code == 200:
            return r.text
    return None

def find_bookmakers(soup):
    '''
    Execute oddsportal bookmakers JavaScript file
    :param response_text: str, oddsportal landing page for a match
    :return bookies: dict
    '''
    ref = "https://www.oddsportal.com"
    for script in soup.find_all("script",{"type":"text/javascript"}):
        try:
            link = script['src']
            if ref not in link:
                link = ref + link
            if "/bookies" in link:
                d = re.findall("\d+",link)[-1]
                bookies_js = link.replace(d,"{}").format(int(time.time()))
                bookies = json.loads(
                    re.findall(r'bookmakersData=({.*});var',
                    get(url=bookies_js, method="oddsportal"))[0]
                )
                return bookies
        except: pass

def find_page_event(text: str) -> dict:
    '''
    Find PageEvent inside html using Regular Expression
    :param text: str
    :return data: dict
    '''
    variable = re.search("(?<=PageEvent\()(.*?)(?=\)\;)",text)
    if variable != None:
        return json.loads(variable.group())

class OddsURL:

    def __init__(self, params: list, live: bool) -> str:
        self.url = "https://fb.oddsportal.com/feed/"
        if live:
            self.url += "live/"
        else:
            self.url += "match/"
        self.url += "-".join([str(i) for i in params])
        self.url += ".dat?_="

    def __str__(self):
        return self.time()

    def time(self):
        timestamp = int(time.time())
        self.url += str(timestamp)
        return self.url

class OddsPortal:

    def __init__(self, tabs: list):
        self.tabs = tabs

    def get(self, url):

        # make a requests
        self.html = get(url)
        for script in self.html.find_all("script",{"type":"text/javascript"}):
            if "PageEvent" in script.text:
                try:

                    # construct the url
                    urls = []
                    data = find_page_event(script.text)
                    for tab in self.tabs:
                        url = OddsURL(
                            live=data['isLive'],
                            params=[
                                data['versionId'],
                                data['sportId'],
                                data['id'],
                                tab['bettingType'],
                                tab['scopeId'],
                                unquote(data['xhash'])
                            ]
                        )
                        urls.append(url)
                    return urls

                except:
                    pass    

        return None


if __name__ == "__main__":

    tabs = [
        {"name": "1X2 (Full Time)", "bettingType": 1,"scopeId": 2},
        {"name": "1X2 (1st Half)", "bettingType": 1,"scopeId": 3},
        {"name": "1X2 (2nd Half)", "bettingType": 1,"scopeId": 4},
        {"name": "Asian Handicap (Full Time)", "bettingType": 5, "scopeId": 2},
        {"name": "Asian Handicap (1st Half)", "bettingType": 5, "scopeId": 3},
        {"name": "Asian Handicap (2nd Half)", "bettingType": 5, "scopeId": 4},
        {"name": "Both Teams To Score (Full Time)", "bettingType": 13, "scopeId": 2},
        {"name": "Both Teams To Score (1st Half)", "bettingType": 13, "scopeId": 3},
        {"name": "Both Teams To Score (2nd Half)", "bettingType": 13, "scopeId": 4},
        {"name": "Over/Under (Full Time)", "bettingType": 2, "scopeId": 2},
        {"name": "Over/Under (1st Half)", "bettingType": 2, "scopeId": 3},
        {"name": "Over/Under (2nd Half)", "bettingType": 2, "scopeId": 4},
        {"name": "Double Chance (Full Time)", "bettingType": 4, "scopeId": 2},
        {"name": "Double Chance (1st Half)", "bettingType": 4, "scopeId": 3},
        {"name": "Half Time / Full Time", "bettingType": 9, "scopeId": 2},
        {"name": "Correct Score (Full Time)", "bettingType": 8, "scopeId": 2},
        {"name": "Correct Score (1st Half)", "bettingType": 8, "scopeId": 3},
        {"name": "Correct Score (2nd Half)", "bettingType": 8, "scopeId": 4}
    ]

    oddsportal = OddsPortal(tabs)

    url = "https://www.oddsportal.com/soccer/england/premier-league-2020-2021/arsenal-brighton-2qsbaz5A"
    oddurls = oddsportal.get(url)
    bookmakers = find_bookmakers(oddsportal.html)
    for url in oddurls:
        print(url)