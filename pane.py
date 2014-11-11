from config import conf
import html5

from i18n import translate


class Pane( html5.Li ):
	"""
		Base class for Panes.
		A pane represents a entry in the left menu as well
		as a list of widgets associated with this pane.
		It is possible to stack panes on-top of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr, iconURL=None, iconClasses=None, closeable=False ):
		super( Pane, self ).__init__( )
		self.descr = descr
		self.iconURL = iconURL
		self.iconClasses = iconClasses
		self.closeable = closeable
		self.childPanes = []
		self.widgetsDomElm = html5.Div()
		self.widgetsDomElm["class"].append("has_no_child")
		self.childDomElem = None
		self.label = html5.A( )
		self.label["class"].append("button")
		h=html5.H3()
		h.element.innerHTML=descr

		#self.label.element.innerHTML = descr #FIXME: descr fehlt
		if iconURL is not None:
			img = html5.Img()
			img["src"] = iconURL
			self.label.appendChild(img)
		if iconClasses is not None:
			for cls in iconClasses:
				self.label["class"].append( cls )
		self.label.appendChild(h)
		self.appendChild( self.label )
		self.sinkEvent("onClick")
		#self.label.addClickListener( self.onClick )
		if closeable:
			self.closeBtn = html5.ext.Button(translate("Close"), self.onBtnCloseReleased)
			self.closeBtn["class"].append("closebtn")
			self.appendChild(self.closeBtn)
		else:
			self.closeBtn = None

	def onBtnCloseReleased(self, *args, **kwargs):
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
			#self.childDomElem["class"] = "actionlist"
			self.appendChild( self.childDomElem )
			#self.childDomElem = DOM.createElement("ul")
			#DOM.setElemAttribute(self.childDomElem, "class", "actionlist")
			#DOM.appendChild( self.getElement(), self.childDomElem )

			if self.closeBtn:
				self.closeBtn[ "style" ][ "display" ] = "none"

		self.childDomElem.appendChild( pane )
		#DOM.appendChild( self.childDomElem, pane.getElement() )

	def removeChildPane(self, pane):
		"""
			Removes a subpane.
			@param pane: The pane to remove. Must be a direct child of this pane
			@type pane: Pane
		"""
		assert pane in self.childPanes, "Cannot remove unknown child-pane %s from %s" % (str(pane),str(self))
		self.childPanes.remove( pane )
		self.childDomElem.removeChild( pane )
		#DOM.removeChild( self.childDomElem, pane.getElement() )
		if len(self.childPanes)==0: #No more children, remove the UL element
			self.removeChild( self.childDomElem )
			#DOM.removeChild( self.getElement(), self.childDomElem )
			self.childDomElem = None

			if self.closeBtn:
				self.closeBtn[ "style" ][ "display" ] = "initial"


	def onDetach(self):
		assert len(self.childPanes)==0, "Attempt to detach a pane which still has subpanes!"
		#Kill all remaining children
		for widget in self.widgetsDomElm._children[:]:
			self.widgetsDomElm.removeChild(widget)
		self.closeBtn = None
		self.label = None
		super(Pane,self).onDetach()

	def addWidget(self, widget):
		"""
			Adds a widget to this pane.
			Note: all widgets of a pane are visible at the same time!
			@param widget: The widget to add
			@type widget: Widget

		"""
		div = html5.Div()
		div["class"].append("vi_operator")
		div.appendChild( widget )
		for w in self.widgetsDomElm._children[:]:
			w["disabled"] = True
		self.widgetsDomElm.appendChild( div )
		self.rebuildChildrenClassInfo()

	def rebuildChildrenClassInfo(self):
		if "has_no_child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_no_child")
		if "has_single_child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_single_child")
		if "has_multiple_children" in self.widgetsDomElm["class"]:
			self.widgetsDomElm["class"].remove("has_multiple_children")
		if len(self.widgetsDomElm._children)==0:
			self.widgetsDomElm["class"].append("has_no_child")
		elif len(self.widgetsDomElm._children)==1:
			self.widgetsDomElm["class"].append("has_single_child")
		else:
			self.widgetsDomElm["class"].append("has_multiple_children")

	def removeWidget(self, widget):
		"""
			Removes a widget.
			@param widget: The widget to remove. Must be a direct child of this pane.
			@type widget: Widget
		"""
		for c in self.widgetsDomElm._children:
			if widget in c._children:
				self.widgetsDomElm.removeChild( c )
				if self.closeable and len(self.widgetsDomElm._children)==0:
					conf["mainWindow"].removePane( self )
				for w in self.widgetsDomElm._children[:]:
					w["disabled"] = False
				self.rebuildChildrenClassInfo()
				return
		raise ValueError("Cannot remove unknown widget %s" % str(widget))

	def containsWidget(self, widget ):
		"""
			Tests wherever widget is a direct child of this pane.
			@returns: Bool
		"""
		for c in self.widgetsDomElm._children:
			if widget in c._children:
				return( True )
		return( False )

	def onClick(self, event, *args, **kwargs ):
		self.focus()
		event.stopPropagation()

	def focus(self):
		conf["mainWindow"].focusPane( self )


class GroupPane( Pane ):
	"""
		This pane groups subpanes; it cannot have direct childrens
	"""

	def __init__(self, *args, **kwargs ):
		super( GroupPane, self ).__init__( *args, **kwargs )
		self.childDomElem = html5.Ul()
		self.childDomElem["style"]["display"] = "none"
		self.appendChild( self.childDomElem )

	def onClick(self, event, *args, **kwargs ):
		if self.childDomElem["style"]["display"] == "none":
			self.childDomElem["style"]["display"] = "block"
		else:
			self.childDomElem["style"]["display"] = "none"
		event.stopPropagation()

	def onFocus(self,event):
		if len( self.childPanes )>0:
			conf["mainWindow"].focusPane( self.childPanes[0] )
