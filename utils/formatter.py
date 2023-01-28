from datetime import datetime
from humanfriendly import parse_date
from time import mktime
from typing import Union


class Formatter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def unix_formatter(date: Union[int, datetime]) -> int:
        if isinstance(date, str):
            date = datetime(*parse_date(date))
            date = int(mktime(date.timetuple()))
        elif isinstance(date, datetime):
            date = int(mktime(date.timetuple()))
        return date
        
    @property
    def prefix(self) -> str:
        return '```'
    
    @property
    def suffix(self) -> str:
        return '```'