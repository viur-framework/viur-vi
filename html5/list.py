from html5.widget import Widget

class Ul( Widget ):
    _baseClass = "ul"

    def __init__(self, *args, **kwargs):
        super(Ul,self).__init__( *args, **kwargs )

class Ol( Widget ):
    _baseClass = "ol"

    def __init__(self, *args, **kwargs):
        super(Ol,self).__init__( *args, **kwargs )

class Li( Widget ):
    _baseClass = "li"

    def __init__(self, *args, **kwargs):
        super(Li,self).__init__( *args, **kwargs )

class Dl( Widget ):
    _baseClass = "dl"

    def __init__(self, *args, **kwargs):
        super(Dl,self).__init__( *args, **kwargs )

class Dt( Widget ):
    _baseClass = "dt"

    def __init__(self, *args, **kwargs):
        super(Dt,self).__init__( *args, **kwargs )

class Dd( Widget ):
    _baseClass = "dd"

    def __init__(self, *args, **kwargs):
        super(Dd,self).__init__( *args, **kwargs )