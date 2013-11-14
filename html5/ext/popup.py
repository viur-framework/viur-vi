import html5
from html5.ext.Button import Button

class Popup( html5.Div ):
	def __init__(self, *args, **kwargs ):
		super( Popup, self ).__init__(*args, **kwargs)

		self["class"] = "alertbox"

		#self["style"]["left"] = "50%"
		#self["style"]["top"] = "50%"
		#self["style"]["width"] = "400px"
		#self["style"]["height"] = "200px"

		self.frameDiv = html5.Div()
		self.frameDiv["class"] = "popup"

		#self.frameDiv["style"]["position"] = "absolute"
		#self.frameDiv["style"]["z-index"] = "99"
		#self.frameDiv["style"]["width"] = "100%"
		#self.frameDiv["style"]["height"] = "100%"
		#self.frameDiv["style"]["background-color"] = "rgba( 100,100,100,100)"

		self.frameDiv.appendChild( self )
		html5.Body().appendChild( self.frameDiv )

	def close(self):
		html5.Body().removeChild( self.frameDiv )
		self.frameDiv = None

