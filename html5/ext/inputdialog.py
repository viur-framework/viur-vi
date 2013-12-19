import html5
from html5.ext.popup import Popup
from html5.ext.button import Button

class InputDialog( Popup ):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, successLbl="Okay", abortLbl="Cancel", *args, **kwargs ):
		super( InputDialog, self ).__init__(*args, **kwargs)
		self["class"].append("inputdialog")
		self.successHandler = successHandler
		self.abortHandler = abortHandler

		span = html5.Span()
		span.element.innerHTML = text
		self.appendChild(span)
		self.inputElem = html5.Input()
		self.inputElem["type"] = "text"
		self.inputElem["value"] = value
		self.appendChild( self.inputElem )
		okayBtn = Button(successLbl, self.onOkay)
		self.appendChild(okayBtn)
		cancelBtn = Button(abortLbl, self.onCancel)
		self.appendChild(cancelBtn)

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler( self, self.inputElem["value"] )
		self.close()

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler( self, self.inputElem["value"] )
		self.close()
