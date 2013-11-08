from html5.widget import Widget
from html5.html5Attr.cite import Cite,Datetime

class Ins( Widget ,Cite,Datetime):
    _baseClass = "ins"

    def __init__(self, *args, **kwargs):
        super(Ins,self).__init__( *args, **kwargs )
