import html5


class SideBar( html5.Div ):

	def __init__(self, *args, **kwargs):
		super( SideBar, self ).__init__( *args, **kwargs )
		self.isInit = False
		self.currentWidget = None
		self.addClass("sidebarwidgets")
		self.addClass("is-empty")

	def onAttach(self):
		super( SideBar, self ).onAttach()
		self.parent().addClass("is-fullview")
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
				self.removeClass("has-child")
				self.addClass("is-empty")
				self.parent().removeClass("is-splitview")
				self.parent().addClass("is-fullview")

		elif widget is not None:
			self.addClass("has-child")
			self.removeClass("is-empty")
			self.parent().addClass("is-splitview")
			self.parent().removeClass("is-fullview")

		self.currentWidget = widget

		if widget is not None:
			self.appendChild( widget )


	def getWidget(self):
		return( self.currentWidget )
