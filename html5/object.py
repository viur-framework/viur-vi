from html5.widget import Widget
from html5.html5Attr.media import Type,Dimensions,Usemap
from html5.html5Attr.form import _Form as Form,Name
class Object( Widget,Type,Form,Name,Dimensions,Usemap ):
    _baseClass = "object"

    def __init__(self, *args, **kwargs):
        super(Object,self).__init__( *args, **kwargs )





