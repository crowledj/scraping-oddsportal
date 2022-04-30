from Handicap import Handicap
from Odd import Odd
import json

def collect_odds(data: dict, bookmakers: dict, labels: list, bet_keyword: str) -> dict:
    
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
    output = {}

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
        # for k in results:
        #     results[k] = {p:results[k][p] for p in results[k] if p == bet_keyword}

        output.update({handicap.code: results})

    return output


if __name__ == "__main__":

    from pprint import pprint
    import os

    os.system("cls")

    tabs = [
        {"file_path": "data/1X2 (Full Time).json", "labels": ['1','X','2']},
        {"file_path": "data/1X2 (1st Half).json", "labels": ['1','X','2']},
        {"file_path": "data/1X2 (2nd Half).json", "labels": ['1','X','2']},
        {"file_path": "data/Asian Handicap (Full Time).json", "labels": ['1','2']},
        {"file_path": "data/Asian Handicap (1st Half).json", "labels": ['1','2']},
        {"file_path": "data/Asian Handicap (2nd Half).json", "labels": ['1','2']},
        {"file_path": "data/Both Teams To Score (Full Time).json", "labels": ['Yes','No']},
        {"file_path": "data/Both Teams To Score (1st Half).json", "labels": ['Yes','No']},
        {"file_path": "data/Both Teams To Score (2nd Half).json", "labels": ['Yes','No']},
        {"file_path": "data/Correct Score (Full Time).json", "labels": ['Odds']},
        {"file_path": "data/Correct Score (1st Half).json", "labels": ['Odds']},
        {"file_path": "data/Correct Score (2nd Half).json", "labels": ['Odds']},
        {"file_path": "data/Double Chance (Full Time).json", "labels": ['1X','12','X2']},
        {"file_path": "data/Double Chance (1st Half).json", "labels": ['1X','12','X2']},
        {"file_path": "data/Half Time - Full Time.json", "labels": ['Odds']},
        {"file_path": "data/Over-Under (Full Time).json", "labels": ['Over','Under']},
        {"file_path": "data/Over-Under (1st Half).json", "labels": ['Over','Under']},
        {"file_path": "data/Over-Under (2nd Half).json", "labels": ['Over','Under']}
    ]

    for tab in tabs:

        # read json files
        data = json.load(open(tab['file_path'],encoding='utf-8'))
        bookmakers = json.load(open('data/bookmakers.json',encoding='utf-8'))

        # collecting the odds
        bet = "bet365"
        result = collect_odds(
            data=data,
            bookmakers=bookmakers,
            labels=tab['labels'],
            bet_keyword=bet
        )

        # dump the results
        # file_name = tab['file_path'].replace('data/','output/')
        # json.dump(result,open(file_name,'w',encoding='utf-8'),indent=4)

        # printout the result
        print(tab['file_path'])
        pprint(result)
        print()