from html5.widget import Widget
from html5.html5Attr.media import Media
from html5.html5Attr.src import Src

class Source( Widget,Media,Src ):
    _baseClass = "source"

    def __init__(self, *args, **kwargs):
        super(Source,self).__init__( *args, **kwargs )





