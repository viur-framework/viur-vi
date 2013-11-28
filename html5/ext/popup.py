import html5

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


class YesNoDialog( Popup ):
	def __init__(self, question, title=None, yesCallback=None, noCallback=None, *args, **kwargs):
		super( YesNoDialog, self ).__init__( *args, **kwargs )
		self["class"].append("yesnodialog")
		self.yesCallback = yesCallback
		self.noCallback = noCallback
		lbl = html5.Span()
		lbl["class"].append("yesnodialog")
		lbl["class"].append("question")
		lbl.appendChild( html5.TextNode( question ) )
		self.appendChild( lbl )
		btnYes = html5.ext.Button("Yes", callback=self.onYesClicked )
		btnYes["class"].append("yesnodialog")
		btnYes["class"].append("btn_yes")
		self.appendChild(btnYes)
		btnNo = html5.ext.Button("No", callback=self.onNoClicked )
		btnNo["class"].append("yesnodialog")
		btnNo["class"].append("btn_no")
		self.appendChild(btnNo)

	def onYesClicked(self, *args, **kwargs ):
		if self.yesCallback:
			self.yesCallback( self )
		self.yesCallback = None
		self.noCallback = None
		self.close()


	def onNoClicked(self, *args, **kwargs ):
		if self.noCallback:
			self.noCallback( self )
		self.yesCallback = None
		self.noCallback = None
		self.close()