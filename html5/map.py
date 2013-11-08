from html5.widget import Widget
from html5.html5Attr._label import _Label as Label
from html5.html5Attr.media import Type
class Map( Widget ,Label,Type):
    _baseClass = "map"

    def __init__(self, *args, **kwargs):
        super(Map,self).__init__( *args, **kwargs )
