#-*- coding: utf-8 -*-
import html5
from config import conf
from i18n import translate

class Pane(html5.Li):
	"""
		Base class for Panes.
		
		A pane represents a entry in the left menu as well
		as a list of widgets associated with this pane.
		
		It is possible to stack panes on-top of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr=None, iconURL=None, iconClasses=None, closeable=False, collapseable=True):
		super(Pane, self).__init__()

		self.parentPane = None
		self.sinkEvent("onClick")

		self.descr = descr
		self.iconURL = iconURL
		self.iconClasses = iconClasses
		self.closeable = closeable
		self.collapseable = collapseable

		self.childPanes = []

		self.widgetsDomElm = html5.Div()
		self.widgetsDomElm["class"].append("has_no_child")
		self.childDomElem = None

		self.label = html5.A()
		self.label["class"].append("button")
		self.appendChild(self.label)

		self.setText(descr, iconURL)

		#self.label.addClickListener( self.onClick )
		if closeable:
			self.closeBtn = html5.ext.Button(translate("Close"), self.onBtnCloseReleased)
			self.closeBtn["class"].append("closebtn")
			self.appendChild(self.closeBtn)
		else:
			self.closeBtn = None

	def setText(self, descr = None, iconURL = None):
		self.label.removeAllChildren()

		if iconURL is None:
			iconURL = self.iconURL

		if iconURL is not None:
			img = html5.Img()
			img["src"] = iconURL
			self.label.appendChild(img)

		if self.iconClasses is not None:
			for cls in self.iconClasses:
				self.label.addClass(cls)

		if descr is None:
			descr = self.descr

		if descr is not None:
			h = html5.H3()
			h.appendChild(descr)
			self.label.appendChild(h)

	def onBtnCloseReleased(self, *args, **kwargs):
		conf["mainWindow"].removePane(self)

	def addChildPane(self, pane):
		"""
			Stack a pane under this one.
			It gets displayed as a subpane.
			@param pane: Another pane
			@type pane: pane
		"""
		assert pane != self, "A pane cannot be a child of itself"

		self.childPanes.append( pane )
		pane.parentPane = self

		if not self.childDomElem:
			self.childDomElem = html5.Ul()

			if self.collapseable and not pane.closeable:
				self.childDomElem[ "style" ][ "display" ] = "none"
			else:
				self.childDomElem[ "style" ][ "display" ] = "initial"

			self.appendChild( self.childDomElem )

			if self.closeBtn:
				self.closeBtn[ "style" ][ "display" ] = "none"

		if ( pane.closeable
			 and "display" in self.childDomElem[ "style" ]
			 and self.childDomElem[ "style" ][ "display" ] == "none" ):
			self.childDomElem[ "style" ][ "display" ] = "initial"

		self.childDomElem.appendChild( pane )

	def removeChildPane(self, pane):
		"""
			Removes a subpane.
			@param pane: The pane to remove. Must be a direct child of this pane
			@type pane: Pane
		"""
		assert pane in self.childPanes, "Cannot remove unknown child-pane %s from %s" % (str(pane),str(self))

		self.childPanes.remove( pane )
		self.childDomElem.removeChild( pane )

		pane.parentPane = None

		#DOM.removeChild( self.childDomElem, pane.getElement() )
		if len(self.childPanes)==0: #No more children, remove the UL element
			self.removeChild( self.childDomElem )
			#DOM.removeChild( self.getElement(), self.childDomElem )
			self.childDomElem = None

			if self.closeBtn:
				self.closeBtn[ "style" ][ "display" ] = "initial"


	def onDetach(self):
		#assert len(self.childPanes)==0, "Attempt to detach a pane which still has subpanes!"
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
		div.appendChild(widget)

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
