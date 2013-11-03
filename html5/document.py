
def createAttribute( tag ):
    """
        Creates a new HTML attribute
    """
    return( eval( "window.top.document.createAttribute( \"%s\" )" % tag ) )


def createElement( element ):
    """
        Creates a new HTML tag
    """
    return( eval( "window.top.document.createElement( \"%s\" )" % element ) )


def getElementById( idTag ):
    return( eval( "window.top.document.getElementById( \"%s\" )" % idTag ) )

def getElementsByTagName( tagName ):
    doc = eval("window.top.document");
    res = []
    htmlCol = doc.getElementsByTagName( tagName )
    for x in range( 0, htmlCol.length ):
        res.append( htmlCol.item(x) )
    return( res )
