import html5
from html5.ext.Button import Button

class InputDialog( html5.Div ):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, *args, **kwargs ):
		super( InputDialog, self ).__init__(*args, **kwargs)
		self.successHandler = successHandler
		self.abortHandler = abortHandler
		self["style"]["position"] = "absolute"
		self["style"]["z-index"] = "99"
		self["style"]["width"] = "100%"
		self["style"]["height"] = "100%"
		self["style"]["background-color"] = "rgba( 100,100,100,100)"

		frameDiv = html5.Div()
		self.appendChild(frameDiv)

		span = html5.Span()
		span.element.innerHTML = text
		frameDiv.appendChild(span)
		self.inputElem = html5.Input()
		self.inputElem["type"] = "text"
		self.inputElem["value"] = value
		frameDiv.appendChild( self.inputElem )
		okayBtn = Button("Okay", self.onOkay)
		frameDiv.appendChild(okayBtn)
		cancelBtn = Button("Cancel", self.onCancel)
		frameDiv.appendChild(cancelBtn)

		#frameDiv["style"]["position"] = "absolute"
		#frameDiv["style"]["z-index"] = "99"
		frameDiv["style"]["left"] = "50%"
		frameDiv["style"]["top"] = "50%"
		frameDiv["style"]["width"] = "400px"
		frameDiv["style"]["height"] = "200px"
		html5.Body().appendChild( self )

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler( self, self.inputElem["value"] )
		html5.Body().removeChild( self )

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler( self, self.inputElem["value"] )
		html5.Body().removeChild( self )
