import html5


class SideBar( html5.Div ):

	def __init__(self, *args, **kwargs):
		super( SideBar, self ).__init__( *args, **kwargs )
		self.isInit = False
		self.currentWidget = None
		self["class"].append("sidebarwidgets")
		self["class"].append("is-empty")

	def onAttach(self):
		super( SideBar, self ).onAttach()
		self.parent()["class"].append("is-fullview")
		self.isInit = True
		if self.currentWidget is not None:
			cw = self.currentWidget
			self.currentWidget = None
			self.setWidget( cw )

	def onDetach(self):
		if self.currentWidget:
			self.removeChild( self.currentWidget )
			self.currentWidget = None
		super( SideBar, self ).onDetach()
		self.isInit = False

	def setWidget(self, widget):
		if not self.isInit:
			self.currentWidget = widget
			return

		if self.currentWidget:
			self.removeChild( self.currentWidget )
			if widget is None:
				self["class"].remove("has-child")
				self["class"].append("is-empty")
				self.parent()["class"].remove("is-splitview")
				self.parent()["class"].append("is-fullview")

		elif widget is not None:
			self["class"].append("has-child")
			self["class"].remove("is-empty")
			self.parent()["class"].append("is-splitview")
			self.parent()["class"].remove("is-fullview")

		self.currentWidget = widget

		if widget is not None:
			self.appendChild( widget )


	def getWidget(self):
		return( self.currentWidget )
