from html5.widget import Widget

class Button( Widget):
	_baseClass = "button"

	def __init__(self, *args, **kwargs):
		super(Button,self).__init__( *args, **kwargs )

	def _getAutofocus(self):
		return( True if self.element.hasAttribute("autofocus") else False )
	def _setAutofocus(self,val):
		if val==True:
			self.element.setAttribute("autofocus","")
		else:
			self.element.removeAttribute("autofocus")

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

	def _getFormnovalidate(self):
		return( True if self.element.hasAttribute("formnovalidate") else False )
	def _setFormnovalidate(self,val):
		if val==True:
			self.element.setAttribute("formnovalidate","")
		else:
			self.element.removeAttribute("formnovalidate")

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val

	def _getFormaction(self):
		return self.element.formaction
	def _setFormaction(self,val):
		self.element.formaction=val

	def _getFormenctype(self):
		return self.element.formenctype
	def _setFormenctype(self,val):
		self.element.formenctype=val

	def _getFormmethod(self):
		return self.element.formmethod
	def _setFormmethod(self,val):
		self.element.formmethod=val

	def _getFormtarget(self):
		return self.element.formtarget
	def _setFormtarget(self,val):
		self.element.formtarget=val

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val

	def _getValue(self):
		return self.element.value
	def _setValue(self,val):
		self.element.value=val

class Fieldset(Widget):
	_baseClass = "fieldset"

	def __init__(self, *args, **kwargs):
		super(Fieldset,self).__init__( *args, **kwargs )

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

class Form(Widget):
	_baseClass = "form"

	def __init__(self, *args, **kwargs):
		super(Form,self).__init__( *args, **kwargs )

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

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


	def _getAutocomplete(self):
		return True if self.element.autocomplete=="on" else False
	def _setAutocomplete(self,val):
		self.element.autocomplete="on" if val==True else "off"


	'''
	def _getAcceptCharset(self):
		return self.element.accept-charset
	def _setAcceptCharset(self,val):
		self.element.accept-charset=val
	'''

	def _getTarget(self):
		return self.element.target
	def _setTarget(self,val):
		self.element.target=val

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

class Input(Widget):
	_baseClass = "input"

	def __init__(self, *args, **kwargs):
		super(Input,self).__init__( *args, **kwargs )

	def _getAccept(self):
		return self.element.accept
	def _setAccept(self,val):
		self.element.accept=val

	def _getAlt(self):
		return self.element.alt
	def _setAlt(self,val):
		self.element.alt=val

	def _getAutocomplete(self):
		return True if self.element.autocomplete=="on" else False
	def _setAutocomplete(self,val):
		self.element.autocomplete="on" if val==True else "off"

	def _getAutofocus(self):
		return( True if self.element.hasAttribute("autofocus") else False )
	def _setAutofocus(self,val):
		if val==True:
			self.element.setAttribute("autofocus","")
		else:
			self.element.removeAttribute("autofocus")

	def _getChecked(self):
		return( True if self.element.hasAttribute("checked") else False )
	def _setChecked(self,val):
		if val==True:
			self.element.setAttribute("checked","")
		else:
			self.element.removeAttribute("checked")

	def _getDisabled(self):
		return( True if self.element.hasAttribute("disabled") else False )
	def _setDisabled(self,val):
		if val==True:
			self.element.setAttribute("disabled","")
		else:
			self.element.removeAttribute("disabled")

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val


	def _getFormaction(self):
		return self.element.formaction
	def _setFormaction(self,val):
		self.element.formaction=val

	def _getFormenctype(self):
		return self.element.formenctype
	def _setFormenctype(self,val):
		self.element.formenctype=val

	def _getFormmethod(self):
		return self.element.formmethod
	def _setFormmethod(self,val):
		self.element.formmethod=val

	def _getFormtarget(self):
		return self.element.formtarget
	def _setFormtarget(self,val):
		self.element.formtarget=val

	def _getFormnovalidate(self):
		return( True if self.element.hasAttribute("formnovalidate") else False )
	def _setFormnovalidate(self,val):
		if val==True:
			self.element.setAttribute("formnovalidate","")
		else:
			self.element.removeAttribute("formnovalidate")

	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.width=val

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.height=val

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

	def _getMaxlength(self):
		return self.element.maxlength
	def _setMaxlength(self,val):
		self.element.maxlength=val

	def _getMultiple(self):
		return( True if self.element.hasAttribute("multiple") else False )
	def _setMultiple(self,val):
		if val==True:
			self.element.setAttribute("multiple","")
		else:
			self.element.removeAttribute("multiple")

	def _getName(self):
		return self.element.name
	def _setName(self,val):
		self.element.name=val

	def _getPattern(self):
		return self.element.pattern
	def _setPattern(self,val):
		self.element.pattern=val

	def _getPlaceholder(self):
		return self.element.placeholder
	def _setPlaceholder(self,val):
		self.element.placeholder=val

	def _getReadonly(self):
		return( True if self.element.hasAttribute("readonly") else False )
	def _setReadonly(self,val):
		if val==True:
			self.element.setAttribute("readonly","")
		else:
			self.element.removeAttribute("readonly")

	def _getRequired(self):
		return( True if self.element.hasAttribute("required") else False )
	def _setRequired(self,val):
		if val==True:
			self.element.setAttribute("required","")
		else:
			self.element.removeAttribute("required")

	def _getSize(self):
		return self.element.size
	def _setSize(self,val):
		self.element.size=val

	def _getSrc(self):
		return self.element.src
	def _setSrc(self,val):
		self.element.src=val

	def _getType(self):
		return self.element.type
	def _setType(self,val):
		self.element.type=val

	def _getStep(self):
		return self.element.step
	def _setStep(self,val):
		self.element.step=val

	def _getValue(self):
		return self.element.value
	def _setValue(self,val):
		self.element.value=val

class Label( Widget ):
	_baseClass = "label"

	def __init__(self, *args, **kwargs):
		super(Label,self).__init__( *args, **kwargs )

	print "Label attribute For dont work!"
	'''

	def _getFor(self):
		return self.element.for
	def _setFor(self,val):
		self.element.for=val
	'''

	def _getForm(self):
		return self.element.form
	def _setForm(self,val):
		self.element.form=val





