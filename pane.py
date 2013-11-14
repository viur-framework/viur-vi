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
		if icon is not None:
			img = html5.Img()
			img["src"] = icon
			self.appendChild(img)
		self.label = html5.A( )
		self.label["class"].append("button")
		self.label.appendChild(html5.TextNode(descr))
		#self.label.element.innerHTML = descr #FIXME: descr fehlt
		self.appendChild( self.label )
		self.sinkEvent("onClick")
		#self.label.addClickListener( self.onClick )
		if closeable:
			self.closeBtn = html5.ext.Button("Close", self.onBtnCloseReleased)
			self.closeBtn["class"].append("closebtn")
			self.appendChild(self.closeBtn)

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
		for widget in self.widgetsDomElm._children[:]:
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
		div = html5.Div()
		div["class"].append("vi_operator")
		div.appendChild( widget )
		self.widgetsDomElm.appendChild( div )

	def removeWidget(self, widget):
		self.widgetsDomElm.removeChild( widget )

	def onClick(self, event, *args, **kwargs ):
		self.focus()
		event.stopPropagation()

	def focus(self):
		conf["mainWindow"].focusPane( self )