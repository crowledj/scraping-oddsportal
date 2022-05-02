import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
from datetime import datetime
from tqdm import tqdm
import json
import time
import re

from Handicap import Handicap
from Odd import Odd


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

def find_league(html):
    '''
    Collecting sports, country, and league information
    :param html: BeautifulSoup object
    :return league: dict
    '''

    breadcrumb = html.find('div',id='breadcrumb')
    breadcrumb = [a.text.strip() for a in breadcrumb.find_all('a')]
    league = {
        "sport": breadcrumb[1],
        "country": breadcrumb[2],
        "league": breadcrumb[3]
    }
    return league

def find_oddjs(html, config):
    '''
    Find odds data JS
    :param html: BeautifulSoup object
    :param config: dict
    :return urls: OddsURL object
    '''
    for script in html.find_all("script",{"type":"text/javascript"}):
        if "PageEvent" in script.text:
            try:

                # construct the url
                urls = []
                data = find_page_event(script.text)
                for tab in config:
                    url = OddsURL(
                        name=tab['name'],
                        labels=tab['labels'],
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

def collect_odds(data: dict, bookmakers: dict, name:str, labels: list, bet_keyword: str) -> dict:
    
    # define functions
    def collect_value(data: list, index: int) -> dict:
        result = {int(k):-1 for k in range(3)}
        for i,idx in enumerate(index):
            result[i] = data[idx]
        return result

    def relabel(data: dict, labels: list) -> dict:
        new = {}
        for i in data:
            if i not in new:
                new.update({labels[i]: data[i]})
        return new


    # define the output variable
    output = {name:{}}

    # prepare the odds and the history data
    oddsdata = data['d']['oddsdata']['back']
    history = data['d']['history']['back']

    # iterate the handicaps
    for h in oddsdata:
        handicap = Handicap(
            code=h,
            value=oddsdata[h]['handicapValue'],
            name=oddsdata[h]['mixedParameterName']
        )

        # identify outcomeId variable type
        outcomeId = oddsdata[h]['outcomeId']
        if type(outcomeId) == list:
            idx = [i for i in range(len(outcomeId))]
        elif type(outcomeId) == dict:
            idx = [str(i) for i in range(len(outcomeId))]
        ids = collect_value(data=outcomeId, index=idx) # outcome ids

        # define the labels
        names = {ids[i]:l for i,l in zip(ids,labels)} 

        # collecting opening odds
        act = oddsdata[h]['act']
        openingOdd = oddsdata[h]['openingOdd']
        openingChangeTime = oddsdata[h]['openingChangeTime']
        for bookies_id in openingOdd:
            if act[bookies_id]:
                ods = collect_value(data=openingOdd[bookies_id], index=idx) # odds value
                tms = collect_value(data=openingChangeTime[bookies_id], index=idx) # timestamps
                for i,_id in enumerate(ids.values()):
                    if _id != -1:
                        odd = Odd(
                            id=_id,
                            odd=ods[i],
                            timestamp=tms[i],
                            bookmaker=bookmakers[bookies_id]['WebName']
                        )
                        handicap.append(odd)

        # collecting handicap odds
        handicapOdds = oddsdata[h]['odds']
        handicapChangeTime = oddsdata[h]['changeTime']
        for bookies_id in handicapOdds:
            if act[bookies_id]:
                ods = collect_value(data=handicapOdds[bookies_id], index=idx)
                tms = collect_value(data=handicapChangeTime[bookies_id], index=idx)
                for i,_id in enumerate(ids.values()):
                    if _id != -1:
                        odd = Odd(
                            id=_id,
                            odd=ods[i],
                            timestamp=tms[i],
                            bookmaker=bookmakers[bookies_id]['WebName']
                        )
                        handicap.append(odd)

        # collecting history odds
        for _id in ids.values():
            if _id != -1:
                for bookies_id in history[_id]:
                    if act[bookies_id]:
                        for value in history[_id][bookies_id]:
                            odd = Odd(
                                id=_id,
                                odd=value[0],
                                timestamp=value[-1],
                                bookmaker=bookmakers[bookies_id]['WebName']
                            )
                            handicap.append(odd)

        # calculate the final summary and relabel the outcomeId
        results = handicap.summary()
        results = relabel(results,labels=names)

        # filter the results
        for k in results:
            results[k] = {p:results[k][p] for p in results[k] if p == bet_keyword}

        if name == "Half Time / Full Time":
            output[name].update({handicap.name: results})
        else:
            if handicap.name == None:
                output[name].update({handicap.value: results})
            else:
                output[name].update({handicap.name: results})

    return output
    
class OddsURL:

    def __init__(self, name: str, labels: list, params: list, live: bool) -> str:
        self.name = name
        self.labels = labels
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
        timestamp = int(round(time.time() * 1000))
        self.url += str(timestamp)
        return self.url

class OddsPortal:

    sport = ""
    country = ""
    league = ""

    def __init__(self, config: list):
        self.config = config

    def get(self, unit: dict) -> dict:

        # make a requests
        html = get(unit['url'])
        bookmakers = find_bookmakers(html)
        
        # find sport, country, and league from the match information
        l = find_league(html)
        self.sport = l['sport']
        self.country = l['country']
        self.league = l['league']

        # accesss oddsjs
        game = " vs ".join([
            unit['home'].title(),
            unit['away'].title()
        ])
        game += "|" + self.league
        urls = find_oddjs(html,self.config)
        result = {}
        for url in tqdm(urls,game):
            try:
                data = json.loads(
                    re.findall(r"\.dat',\s({.*})",
                    get(url=url.time(), method="oddsportal"))[0]
                )

                # collecting the odds
                bet = "bet365"
                output = collect_odds(
                    data=data,
                    bookmakers=bookmakers,
                    labels=url.labels,
                    name=url.name,
                    bet_keyword=bet
                )
                result.update(output)
            except:
                pass

        # define the result
        date = datetime.fromtimestamp(unit['timestamp'])
        results = {
            "home": unit['home'],
            "away": unit['away'],
            "sport": self.sport,
            "country": self.country,
            "league": self.league,
            "match_time": {
                "time": date.strftime("%H:%M"),
                "day": date.strftime("%d"),
                "month": date.strftime("%b"),
                "year": date.strftime("%y")
            },
            "oddsdata": result
        }

        return results



if __name__ == "__main__":

    from pprint import pprint

    tabs_config = json.load(open("source/tabs.json"))
    units = json.load(open('source/100-matches.json'))
    oddsportal = OddsPortal(tabs_config)

    outcomes = []
    for unit in units:
        results = oddsportal.get(unit)
        outcomes.append(results)
    
    json.dump(outcomes,open('output/results.json','w',encoding='utf-8'),indent=4)