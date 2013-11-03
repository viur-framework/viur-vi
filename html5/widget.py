from html5 import document

class ClassWrapper( list ):
    def __init__( self, targetWidget ):
        super( ClassWrapper, self ).__init__( )
        self.targetWidget = targetWidget
        clsStr = targetWidget.element.getAttribute("class")
        if clsStr:
            for c in clsStr.split(" "):
                list.append( self, c )

    def _updateElem(self):
        self.targetWidget.element.setAttribute("class", " ".join( self ) )

    def append(self, p_object):
        list.append( self, p_object )
        self._updateElem()

    def clear(self):
        list.clear( self )
        self._updateElem()

    def remove(self, value):
        list.remove( self, value )
        self._updateElem()

    def extend(self, iterable):
        list.extend( self, iterable )
        self._updateElem()

    def insert(self, index, p_object):
        list.insert( self, index, p_object )
        self._updateElem()

    def pop(self, index=None):
        list.pop( self, index )
        self._updateElem()


class StyleWrapper( dict ):
    def __init__( self, targetWidget ):
        super( StyleWrapper, self ).__init__( )
        self.targetWidget = targetWidget
        targetWidget.element.style.border = "1px solid black"
        style = targetWidget.element.style
        for key in dir(style):
            # Convert JS-Style-Syntax to CSS Syntax (ie borderTop -> border-top)
            realKey = ""
            for currChar in key:
                if currChar.isupper():
                    realKey += "-"
                realKey += currChar.lower()
            val = style.getPropertyValue(realKey)
            if val:
                dict.__setitem__(self,realKey,val)

    def __setitem__(self, key, value):
        dict.__setitem__( self, key, value )
        self.targetWidget.element.style.setProperty( key, value )

    def update(self, E=None, **F):
        dict.update( self, E, **F)
        if E is not None and "keys" in dir(E):
            for key in E:
                self.targetWidget.element.style.setProperty( key, E[key] )
        elif E:
            for (key, val) in E:
                self.targetWidget.element.style.setProperty( key, val )
        for key in F:
            self.targetWidget.element.style.setProperty( key, F[key] )



class Widget( object ):
    _baseClass = None

    def __init__(self, *args, **kwargs ):
        if "_wrapElem" in kwargs.keys():
            self.element = kwargs["_wrapElem"]
        else:
            assert self._baseClass is not None
            self.element = document.createElement( self._baseClass )
        super( Widget, self ).__init__( *args, **kwargs )
        self._children = []
        self._catchedEvents = []
        self._disabledState = None

    def sinkEvent(self, *args):
        for eventName in args:
            if eventName in self._catchedEvents or eventName.lower in ["onattach","ondetach"]:
                continue
            assert eventName in dir( self ), "%s must provide a %s method" % (str(self),eventName)
            self._catchedEvents.append( eventName )
            setattr( self.element, eventName.lower(), getattr(self, eventName))

    def unsinkEvent(self, *args ):
        for eventName in args:
            if not eventName in self._catchedEvents:
                continue
            self._catchedEvents.remove( eventName )
            setattr( self.element, eventName.lower(), None )

    def getDisabled(self):
        return( self._disabledState is not None )

    def setDisabled(self, disable):
        if disable:
            if self._disabledState is not None:
                return
            else:
                self._disabledState = { "events": self._catchedEvents[:] }
                self.unsinkEvent( *self._catchedEvents[:] )
        else:
            if self._disabledState is None:
                return
            else:
                self.sinkEvent( *self._disabledState["events"] )
                self._disabledState = None

    def _getTargetFuncName(self, key, type):
        assert type in ["get","set"]
        return( "%s%s" % (type,(key[0].upper()+key[1:])))

    def __getitem__(self, key):
        funcName = self._getTargetFuncName( key, "get" )
        if funcName in dir( self ):
            return( getattr( self, funcName)() )
        return( None )

    def __setitem__(self, key, value):
        funcName = self._getTargetFuncName( key, "set" )
        if funcName in dir( self ):
            return( getattr( self, funcName )( value ) )

    def getId(self):
        return( self.element.id )

    def setId( self, val ):
        self.element.id = val

    def getClass( self ):
        return( ClassWrapper( self ) )

    def setClass(self, value):
        if value is None:
            self.element.setAttribute("class", " " )
        elif isinstance( value, str ):
            self.element.setAttribute("class", value )
        elif isinstance( value, list ):
            self.element.setAttribute("class", " ".join(value) )
        else:
            raise ValueError("Class must be a String, a List or None")

    def getStyle(self):
        return( StyleWrapper( self ) )

    def onAttach(self):
        pass

    def onDetach(self):
        pass

    def appendChild(self, child):
        self._children.append( child )
        self.element.appendChild( child.element )
        child.onAttach()

    def removeChild(self, child):
        assert child in self._children, "%s is not a child of %s" % (child, self)
        child.onDetach()
        self.element.removeChild( child.element )
        self._children.remove( child )

    def onBlur(self, event):
        pass
    def onChange(self, event):
        pass
    def onContextMenu(self, event):
        pass
    def onFocus(self,event):
        pass
    def onFormChange(self,event):
        pass
    def onFormInput(self, event):
        pass
    def onInput(self, event):
        pass
    def onInvalid(self, event):
        pass
    def onReset(self, event):
        pass
    def onSelect(self, event):
        pass
    def onSubmit(self, event):
        pass
    def onKeyDown(self, event):
        pass
    def onKeyPress(self, event):
        pass
    def onKeyUp(self, event):
        pass
    def onClick(self, event):
        pass
    def onDblClick(self, event):
        pass
    def onDrag(self, event):
        pass
    def onDragEnd(self, event):
        pass
    def onDragEnter(self, event):
        pass
    def onDragLeave(self, event):
        pass
    def onDragOver(self, event):
        pass
    def onDragStart(self, event):
        pass
    def onDrop(self, event):
        pass
    def onMouseDown(self, event):
        pass
    def onMouseMove(self, event):
        pass
    def onMouseOut(self, event):
        pass
    def onMouseOver(self, event):
        pass
    def onMouseUp(self, event):
        pass
    def onMouseWheel(self, event):
        pass
    def onScroll(self, event):
        pass


    def _getEventMap(self):
        res = { "onblur": "onBlur",
                "onchange":"onChange",
                "oncontextmenu":"onContextMenu",
                "onfocus":"onFocus",
                "onformchange":"onFormChange",
                "onforminput":"onFormInput",
                "oninput":"onInput",
                "oninvalid":"onInvalid",
                "onreset":"onReset",
                "onselect":"onSelect",
                "onsubmit":"onSubmit",
                "onkeydown":"onKeyDown",
                "onkeypress":"onKeyPress",
                "onkeyup":"onKeyUp",
                "onclick":"onClick",
                "ondblclick":"onDblClick",
                "ondrag":"onDrag",
                "ondragend":"onDragEnd",
                "ondragenter":"onDragEnter",
                "ondragleave":"onDragLeave",
                "ondragover":"onDragOver",
                "ondragstart":"onDragStart",
                "ondrop":"onDrop",
                "onmousedown":"onMouseDown",
                "onmousemove":"onMouseMove",
                "onmouseout":"onMouseOut",
                "onmouseover":"onMouseOver",
                "onmouseup":"onMouseUp",
                "onmousewheel":"onMouseWheel",
                "onscroll":"onScroll"
        }
        return( res )












