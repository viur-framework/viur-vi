from html5.widget import Widget

class Nav( Widget ):
    _baseClass = "nav"

    def __init__(self, *args, **kwargs):
        super(Nav,self).__init__( *args, **kwargs )
