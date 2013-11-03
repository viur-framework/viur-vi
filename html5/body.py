from html5.widget import Widget
from html5 import document

class Body( Widget ):
    def __init__( self, *args, **kwargs ):
        elem = document
        super( Body, self ).__init__( _wrapElem=document.getElementsByTagName("body")[0] )
