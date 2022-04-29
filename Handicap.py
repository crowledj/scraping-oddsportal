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
        list = [
            self.name,
            self.value,
            self.code
        ]
        return ",".join([str(i) for i in list])

    # def to_dict(self):
    #     items = []
    #     for item in self.items:
    #         items.append(item.to_dict())
    #     items = sorted(items, key=lambda x: x['change_time'])
    #     items = sorted(items, key=lambda x: x['bookmaker'])

    #     bookmakers = {}
    #     for item in items:
    #         o = item['odd']
    #         b = item['bookmaker']
    #         try:
    #             bookmakers[b].append(o)
    #         except:
    #             bookmakers.update({b: [o]})
    #     return bookmakers