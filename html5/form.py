from html5.widget import Widget
from html5.html5Attr._label import _Label
from html5.html5Attr.media import Type,Dimensions
from html5.html5Attr.form import _Form,Alt,Autofocus,Disabled,Name,Checked,Indeterminate,Value,Formhead,Autocomplete,Inputs,Required,Multiple,Size,__For
from html5.html5Attr.href import Target
from html5.html5Attr.src import Src
from html5.textnode import TextNode


class Button( Disabled,Widget,Type,_Form,Autofocus,Name,Value,Formhead):
	_baseClass = "button"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		Type.__init__( self, *args, **kwargs )
		_Form.__init__( self, *args, **kwargs )
		Autofocus.__init__( self, *args, **kwargs )
		Name.__init__( self, *args, **kwargs )
		Value.__init__( self, *args, **kwargs )
		Formhead.__init__( self, *args, **kwargs )
		#super(Button,self).__init__( *args, **kwargs )

class Fieldset(Disabled,Widget,_Form,Name):
	_baseClass = "fieldset"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		_Form.__init__( self, *args, **kwargs )
		Name.__init__( self, *args, **kwargs )

class Form(Disabled,Widget,Name,Target,Autocomplete):
	_baseClass = "form"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		Name.__init__( self, *args, **kwargs )
		Target.__init__( self, *args, **kwargs )
		Autocomplete.__init__( self, *args, **kwargs )

	def _getNovalidate(self):
		return( True if self.element.hasAttribute("novalidate") else False )
	def _setNovalidate(self,val):
		if val==True:
			self.element.setAttribute("novalidate","")
		else:
			self.element.removeAttribute("novalidate")

	def _getAction(self):
		return self.element.action
	def _setAction(self,val):
		self.element.action=val

	def _getMethod(self):
		return self.element.method
	def _setMethod(self,val):
		self.element.method=val

	def _getEnctype(self):
		return self.element.enctype
	def _setEnctype(self,val):
		self.element.enctype=val

	def _getAcceptCharset(self):
		return getattr(self.element,"accept-charset")
	def _setAcceptCharset(self,val):
		self.element.setAttribute("accept-charset",val)

class Input(Disabled,Widget,Type,_Form,Alt,Autofocus,Checked,Indeterminate,Name,Dimensions,Value,Formhead,Autocomplete,Inputs,Multiple,Size,Src):
	_baseClass = "input"

	def __init__(self, *args, **kwargs):
		Disabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		Type.__init__(self, *args, **kwargs)
		_Form.__init__(self, *args, **kwargs)
		Alt.__init__(self, *args, **kwargs)
		Autofocus.__init__(self, *args, **kwargs)
		Checked.__init__(self, *args, **kwargs)
		Indeterminate.__init__(self, *args, **kwargs)
		Name.__init__(self, *args, **kwargs)
		Dimensions.__init__(self, *args, **kwargs)
		Value.__init__(self, *args, **kwargs)
		Formhead.__init__(self, *args, **kwargs)
		Autocomplete.__init__(self, *args, **kwargs)
		Inputs.__init__(self, *args, **kwargs)
		Multiple.__init__(self, *args, **kwargs)
		Size.__init__(self, *args, **kwargs)
		Src.__init__(self, *args, **kwargs)
		#super(Input,self).__init__( *args, **kwargs )

	def _getAccept(self):
		return self.element.accept
	def _setAccept(self,val):
		self.element.accept=val

	def _getList(self):
		return self.element.list
	def _setList(self,val):
		self.element.list=val

	def _getMax(self):
		return self.element.max
	def _setMax(self,val):
		self.element.max=val

	def _getMin(self):
		return self.element.min
	def _setMin(self,val):
		self.element.min=val

	def _getPattern(self):
		return self.element.pattern
	def _setPattern(self,val):
		self.element.pattern=val

	def _getStep(self):
		return self.element.step
	def _setStep(self,val):
		self.element.step=val

class Label( Widget,_Form,__For ):
	_baseClass = "label"
	autoIdCounter = 0
	def __init__(self, txt="", forElem=None, *args, **kwargs):
		super(Label,self).__init__( *args, **kwargs )
		if txt:
			self.appendChild(TextNode(txt))
		if forElem:
			if not forElem["id"]:
				idx = Label.autoIdCounter
				Label.autoIdCounter += 1
				forElem["id"] = "label-autoid-for-%s" % idx
			self["for"] = forElem["id"]


class Optgroup( Disabled,Widget,_Label ):
	_baseClass = "optgroup"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		_Label.__init__( self, *args, **kwargs )


class Option( Disabled,Widget,_Label,Value ):
	_baseClass = "option"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		_Label.__init__( self, *args, **kwargs )
		Value.__init__( self, *args, **kwargs )

	def _getSelected(self):
		return( True if self.element.selected else False )
		#return( True if self.element.hasAttribute("selected") else False )
	def _setSelected(self,val):
		if val==True:
			self.element.selected=True
		else:
			self.element.selected=False

class Output( Widget,_Form,Name,__For ):
	_baseClass = "output"

	def __init__(self, *args, **kwargs):
		super(Output,self).__init__( *args, **kwargs )



class Select( Disabled,Widget,_Form,Autofocus,Name,Required,Multiple,Size ):
	_baseClass = "select"

	def __init__(self, *args, **kwargs):
		Disabled.__init__( self, *args, **kwargs )
		Widget.__init__( self, *args, **kwargs )
		_Form.__init__( self, *args, **kwargs )
		Autofocus.__init__( self, *args, **kwargs )
		Name.__init__( self, *args, **kwargs )
		Required.__init__( self, *args, **kwargs )
		Multiple.__init__( self, *args, **kwargs )
		Size.__init__( self, *args, **kwargs )

	def _getSelectedIndex(self):
		return( self.element.selectedIndex )

	def _getOptions(self):
		return( self.element.options )


class Textarea( Disabled, Widget,_Form ,Autofocus,Name,Inputs,Value):
	_baseClass = "textarea"

	def __init__(self, *args, **kwargs):
		Disabled.__init__(self, *args, **kwargs )
		Widget.__init__(self, *args, **kwargs )
		_Form.__init__(self, *args, **kwargs )
		Autofocus.__init__(self, *args, **kwargs )
		Name.__init__(self, *args, **kwargs )
		Inputs.__init__(self, *args, **kwargs )
		Value.__init__(self, *args, **kwargs )

		#super(Textarea,self).__init__( *args, **kwargs )

	def _getCols(self):
		return self.element.cols
	def _setCols(self,val):
		self.element.cols=val

	def _getRows(self):
		return self.element.rows
	def _setRows(self,val):
		self.element.rows=val

	def _getWrap(self):
		return self.element.wrap
	def _setWrap(self,val):
		self.element.wrap=val


