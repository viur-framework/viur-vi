import html5
from html5.ext.popup import Popup
from html5.ext.Button import Button

class InputDialog( Popup ):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, *args, **kwargs ):
		super( InputDialog, self ).__init__(*args, **kwargs)
		self.successHandler = successHandler
		self.abortHandler = abortHandler

		span = html5.Span()
		span.element.innerHTML = text
		self.appendChild(span)
		self.inputElem = html5.Input()
		self.inputElem["type"] = "text"
		self.inputElem["value"] = value
		self.appendChild( self.inputElem )
		okayBtn = Button("Okay", self.onOkay)
		self.appendChild(okayBtn)
		cancelBtn = Button("Cancel", self.onCancel)
		self.appendChild(cancelBtn)

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler( self, self.inputElem["value"] )
		self.close()

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler( self, self.inputElem["value"] )
		self.close()
