from collections import defaultdict

class Handicap:

    def __init__(self, name="", code="", value=-1.0):
        '''
        Collection of odds
        :param name: str
        :param code: str
        :param value: float
        '''
        self.code = code
        self.value = float(value)
        self.name = name
        self.items = []
        self.hashes = []

    def append(self, odd):
        '''
        Append new unique odd object into odds
        :param odd: Odd object
        '''
        if odd.hash not in self.hashes:
            self.hashes.append(odd.hash)
            self.items.append(odd)

    def __str__(self):
        '''Represent object as a string on print'''
        list = [
            self.name,
            self.value,
            self.code
        ]
        return ",".join([str(i) for i in list])

    def to_dict(self):
        '''Reformat collected odds into one single dictionary'''
        
        # turn odd object into a list
        items = []
        for item in self.items:
            items.append(item.to_dict())
        items = sorted(items, key=lambda x: x['change_time'])
        items = sorted(items, key=lambda x: x['bookmaker'])
        items = sorted(items, key=lambda x: x['id'])

        # turn odd list into dictionary
        odd_dict = {}
        for i in items:
            d, b = i['id'], i['bookmaker']
            if i['id'] not in odd_dict:
                odd_dict.setdefault(d,{})
            if i['bookmaker'] not in odd_dict[d]:
                odd_dict[d].setdefault(b,[])
            odd_dict[d][b].append(i['odd'])
        return odd_dict

    def summary(self):
        '''Filter and calculate the odds data to find bet opening, bet closing, odds highest, and odds average'''

        # find the opening and closing value
        temp = {}
        odds = self.to_dict()
        for d,data in odds.items():
            if d not in temp:
                temp.setdefault(d,[])
            for b,odd in data.items():
                odds[d][b] = {
                    'opening': odd[0],
                    'closing': odd[-1]
                }
                temp[d].append(odd[-1])

        # calculate the highest and the average odds based on it's column
        self.highest = {k:max(temp[k]) for k in temp}
        self.average = {k:round(sum(temp[k])/len(temp[k]),2) for k in temp}
        return odds