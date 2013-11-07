from config import conf
import html5





class Pane( html5.Li ):
	"""
		Base class for Panes.
		A pane represents a entry in the left menu aswell
		as a list of widgets associated with this pane.
		Its possible to stack panes ontop of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr, icon=None, closeable=False ):
		super( Pane, self ).__init__( )
		self.descr = descr
		self.icon = icon
		self.closeable = closeable
		self.childPanes = []
		self.widgetsDomElm = html5.Div()
		self.childDomElem = None
		self.label = html5.Span( )
		self.label.element.innerHTML = descr #FIXME: descr fehlt
		self.appendChild( self.label )
		self.sinkEvent("onClick")
		#self.label.addClickListener( self.onClick )
		#if closeable:
		#	self.closeBtn = Button("X", self.onBtnCloseReleased)
		#	DOM.appendChild(self.getElement(),self.closeBtn.getElement())
		#	self.closeBtn.onAttach()

	def onBtnCloseReleased(self, *args, **kwargs):
		print("CLOSING PANE")
		conf["mainWindow"].removePane( self )

	def addChildPane(self, pane):
		"""
			Stack a pane under this one.
			It gets displayed as a subpane.
			@param pane: Another pane
			@type pane: pane
		"""
		assert pane != self, "A pane cannot be a child of itself"
		self.childPanes.append( pane )
		if not self.childDomElem:
			self.childDomElem = html5.Ul()
			self.childDomElem["class"] = "actionlist"
			self.appendChild( self.childDomElem )
			#self.childDomElem = DOM.createElement("ul")
			#DOM.setElemAttribute(self.childDomElem, "class", "actionlist")
			#DOM.appendChild( self.getElement(), self.childDomElem )
		self.childDomElem.appendChild( pane )
		#DOM.appendChild( self.childDomElem, pane.getElement() )

	def removeChildPane(self, pane):
		assert pane in self.childPanes, "Cannot remove unknown child-pane %s from %s" % (str(pane),str(self))
		self.childPanes.remove( pane )
		self.childDomElem.removeChild( pane )
		#DOM.removeChild( self.childDomElem, pane.getElement() )
		if len(self.childPanes)==0: #No more children, remove the UL element
			self.removeChild( self.childDomElem )
			#DOM.removeChild( self.getElement(), self.childDomElem )
			self.childDomElem = None


	def onDetach(self):
		assert len(self.childPanes)==0, "Attempt to detach a pane which still has subpanes!"
		#Kill all remaining children
		for widget in self.widgets[:]:
			self.removeWidget(widget)
		self.closeBtn = None
		self.label = None
		super(Pane,self).onDetach()

	def addWidget(self, widget):
		"""
			Adds a widget to this pane.
			Note: all widgets of a pane are visible at the same time!
			@param widget: The widget to add
			@type widget: widget

		"""
		self.widgetsDomElm.appendChild( widget )

	def removeWidget(self, widget):
		self.widgetsDomElm.removeChild( widget )

	def onClick(self, event, *args, **kwargs ):
		self.focus()
		event.stopPropagation()

	def focus(self):
		conf["mainWindow"].focusPane( self )