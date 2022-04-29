import base64
from datetime import datetime

class Odd:

    def __init__(self, bookmaker="", odd=-1, timestamp=-1):
        self.bookmaker = bookmaker
        self.odd = float(odd)
        self.timestamp = timestamp
        self.hashing()

    def strftime(self, timestamp):
        try:
            timestamp = datetime.fromtimestamp(timestamp)
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return timestamp
        except Exception as exception:
            print(exception)

    def hashing(self):
        text = ",".join([str(i) for i in [self.bookmaker,self.odd,self.timestamp]])
        self.hash = base64.b64encode(bytes(text, encoding='utf-8')).decode()

    def to_dict(self):
        return dict(
            bookmaker=self.bookmaker,
            odd=self.odd,
            change_time=self.strftime(self.timestamp)
        )

class Odds:

    def __init__(self, handicap_code, handicap_value, name):
        self.items = []
        self.hashes = []
        self.handicap_code = handicap_code
        self.handicap_value = handicap_value
        self.name = name

    def append(self, item):
        if item.hash not in self.hashes:
            self.items.append(item)
            self.hashes.append(item.hash)

    def to_dict(self):
        items = []
        for item in self.items:
            items.append(item.to_dict())
        items = sorted(items, key=lambda x: x['change_time'])
        items = sorted(items, key=lambda x: x['bookmaker'])

        bookmakers = {}
        for item in items:
            o = item['odd']
            b = item['bookmaker']
            try:
                bookmakers[b].append(o)
            except:
                bookmakers.update({b: [o]})
        return bookmakers