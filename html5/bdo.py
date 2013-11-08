from html5.widget import Widget

class Bdo( Widget ):
    _baseClass = "bdo"

    def __init__(self, *args, **kwargs):
        super(Bdo,self).__init__( *args, **kwargs )