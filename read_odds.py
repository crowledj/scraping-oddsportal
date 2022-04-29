from odd import Odd, Odds

import statistics
import json
import os

from datetime import datetime
from pprint import pprint

os.system("cls")

bookmaker = json.load(open('data/bookmakers.json',encoding='utf-8'))
data = json.load(open('data/Half Time - Full Time.json',encoding='utf-8'))
oddsdata = data['d']['oddsdata']['back']
history = data['d']['history']['back']

for h in oddsdata:
    mp = oddsdata[h]['mixedParameterName']
    hv = oddsdata[h]['handicapValue']
    odds = Odds(h,hv,mp)
    m = mp.split("/")[0]
    p = mp.split("/")[1]
    if m == p:
        # print(h,mp)

        # collect all opening odds and it's change time
        handicapOdds = oddsdata[h]['odds']
        changeTime = oddsdata[h]['changeTime']
        openingOdd = oddsdata[h]['openingOdd']
        openingChangeTime = oddsdata[h]['openingChangeTime']
        
        for bookies_id in openingOdd:
            odd = Odd(
                bookmaker=bookmaker[bookies_id]['WebName'],
                odd=openingOdd[bookies_id][0],
                timestamp=openingChangeTime[bookies_id][0]
            )
            odds.append(odd)

        for bookies_id in handicapOdds:
            odd = Odd(
                bookmaker=bookmaker[bookies_id]['WebName'],
                odd=handicapOdds[bookies_id][0],
                timestamp=changeTime[bookies_id][0]
            )
            odds.append(odd)

        outcomes = oddsdata[h]['outcomeId']
        for bookies_id in history[outcomes[0]]:
            for odd_history in history[outcomes[0]][bookies_id]:
                odd = Odd(
                    bookmaker=bookmaker[bookies_id]['WebName'],
                    odd=odd_history[0],
                    timestamp=odd_history[-1]
                )
                odds.append(odd)

        items = odds.to_dict()
        closes = []
        for i in items:
            closes.append(items[i][-1])
        mean = sum(closes)/len(closes)
        mean = round(mean,2)
        print(h,mp,mean)

# find opening odds for bet365

# find closing odds for bet365