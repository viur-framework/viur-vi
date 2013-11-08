from html5.widget import Widget
from html5.html5Attr.form import Name,Value

class Param( Widget,Name,Value ):
    _baseClass = "param"

    def __init__(self, *args, **kwargs):
        super(Param,self).__init__( *args, **kwargs )





