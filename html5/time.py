from html5.widget import Widget
from html5.html5Attr.cite import Datetime
class Time( Widget ,Datetime):
    _baseClass = "time"

    def __init__(self, *args, **kwargs):
        super(Time,self).__init__( *args, **kwargs )
