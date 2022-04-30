from hashlib import md5
from datetime import datetime

class Odd:

    def __init__(self, bookmaker="", id=-1, odd=-1.0, timestamp=-1):
        '''
        Odd object
        :param bookmaker: str
        :param id: int
        :param odd: float
        :param timestamp: int
        '''
        self.id = id
        self.bookmaker = bookmaker
        self.odd = float(odd)
        self.timestamp = timestamp
        self.change_time = self.strftime(timestamp)
        self.hashing()

    def hashing(self):
        '''
        Turn object string into a hash
        '''
        self.hash = md5(bytes(self.__str__(), encoding='utf-8')).hexdigest()

    def strftime(self, timestamp):
        '''
        Format timestamp as a string date
        :param timestamp: int
        :return:
        '''
        try:
            timestamp = datetime.fromtimestamp(timestamp)
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return timestamp
        except:
            return None

    def to_dict(self):
        '''
        Return object as a dictionary
        '''
        return dict(
            id=self.id,
            bookmaker=self.bookmaker,
            odd=self.odd,
            change_time=self.change_time
        )

    def __str__(self):
        '''
        Return object as a string
        '''
        list = [
            self.id,
            self.bookmaker,
            self.odd,
            self.timestamp
        ]
        return ",".join([str(i) for i in list])