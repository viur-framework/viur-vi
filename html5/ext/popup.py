import html5

class Popup( html5.Div ):
	def __init__(self, title=None, *args, **kwargs ):
		super( Popup, self ).__init__(*args, **kwargs)

		self["class"] = "alertbox"
		if title:
			lbl = html5.Span()
			lbl["class"].append("title")
			lbl.appendChild( html5.TextNode( title ) )
			self.appendChild( lbl )

		self.frameDiv = html5.Div()
		self.frameDiv["class"] = "popup"

		self.frameDiv.appendChild( self )
		html5.Body().appendChild( self.frameDiv )

	def close(self, *args, **kwargs):
		html5.Body().removeChild( self.frameDiv )
		self.frameDiv = None

class YesNoDialog( Popup ):
	def __init__(self, question, title=None, yesCallback=None, noCallback=None, yesLabel="Yes", noLabel="No", *args, **kwargs):
		super( YesNoDialog, self ).__init__( title, *args, **kwargs )
		self["class"].append("yesnodialog")
		self.yesCallback = yesCallback
		self.noCallback = noCallback
		lbl = html5.Span()
		lbl["class"].append("question")
		lbl.appendChild( html5.TextNode( question ) )
		self.appendChild( lbl )
		btnYes = html5.ext.Button(yesLabel, callback=self.onYesClicked )
		btnYes["class"].append("btn_yes")
		self.appendChild(btnYes)
		btnNo = html5.ext.Button(noLabel, callback=self.onNoClicked )
		btnNo["class"].append("btn_no")
		self.appendChild(btnNo)

	def drop(self):
		self.yesCallback = None
		self.noCallback = None
		self.close()

	def onYesClicked(self, *args, **kwargs ):
		if self.yesCallback:
			self.yesCallback( self )

		self.drop()

	def onNoClicked(self, *args, **kwargs ):
		if self.noCallback:
			self.noCallback( self )

		self.drop()

class SelectDialog( Popup ):

	def __init__( self, prompt, items=None, title=None, okBtn="OK", cancelBtn="Cancel", forceSelect=False, *args, **kwargs ):
		super( SelectDialog, self ).__init__( title, *args, **kwargs )
		self["class"].append("selectdialog")

		# Prompt
		if prompt:
			lbl = html5.Span()
			lbl[ "class" ].append( "prompt" )
			lbl.appendChild( html5.TextNode( prompt ) )
			self.appendChild( lbl )

		# Items
		self.items = []

		if not forceSelect and len( items ) <= 3:
			for item in items:
				btn = html5.ext.Button( item.get( "title" ), callback=self.onAnyBtnClick )
				btn._callback = item.get( "callback" )

				if item.get( "class" ):
					btn[ "class" ].extend( item[ "class" ] )

				self.appendChild( btn )
				self.items.append( btn )
		else:
			self.select = html5.Select()
			self.appendChild( self.select )

			for i, item in enumerate( items ):
				opt = html5.Option()

				opt[ "value" ] = str( i )
				opt._callback = item.get( "callback" )
				opt.appendChild( html5.TextNode( item.get( "title" ) ) )

				self.select.appendChild( opt )
				self.items.append( opt )

			if okBtn:
				self.appendChild( html5.ext.Button( okBtn, callback=self.onOkClick ) )

			if cancelBtn:
				self.appendChild( html5.ext.Button( cancelBtn, callback=self.onCancelClick ) )

	def onAnyBtnClick( self, sender = None ):
		for btn in self.items:
			if btn == sender:
				if btn._callback:
					btn._callback( self )
				break

		self.items = None
		self.close()

	def onCancelClick(self, sender = None ):
		self.close()

	def onOkClick(self, sender = None ):
		if self.select[ "selectedIndex" ] < 0:
			return

		item = self.items[ int( self.select[ "options" ].item( self.select[ "selectedIndex" ] ).value ) ]
		if item._callback:
			item._callback( self )

		self.items = None
		self.select = None
		self.close()
