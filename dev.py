# import oddsportal object
from Handicap import Handicap
from Odd import Odd

import json
import os

from pprint import pprint

os.system("cls")

# define functions
def collect_value(data: list, index: int) -> dict:
    result = {int(k):-1 for k in range(3)}
    for i,idx in enumerate(index):
        result[i] = data[idx]
    return result

# read json file
data = json.load(open('data/Over-Under (2nd Half).json',encoding='utf-8'))

# define odds variable
bookmakers = json.load(open('data/bookmakers.json',encoding='utf-8'))
oddsdata = data['d']['oddsdata']['back']
history = data['d']['history']['back']

# collect odds
for h in oddsdata:
    odds = Handicap(
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
                    odds.append(odd)

    # collecting handicap odds
    handicapOdds = oddsdata[h]['odds']
    handicapChangeTime = oddsdata[h]['changeTime']
    for bookies_id in handicapOdds:
        if act[bookies_id]:
            ods = collect_value(data=handicapOdds[bookies_id], index=idx) # odds value
            tms = collect_value(data=handicapChangeTime[bookies_id], index=idx) # timestamps
            for i,_id in enumerate(ids.values()):
                if _id != -1:
                    odd = Odd(
                        id=_id,
                        odd=ods[i],
                        timestamp=tms[i],
                        bookmaker=bookmakers[bookies_id]['WebName']
                    )
                    odds.append(odd)

    # collecting history data
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
                        odds.append(odd)

    # calculate the final summary
    print(odds.value, end=": ")
    results = odds.summary()

    # filter the results
    keyword = "bet365"
    for k in results:
        for b in results[k]:
            results[k] = {p:results[k][p] for p in results[k] if p == keyword}
    
    print(results)