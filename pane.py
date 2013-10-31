import pyjd # this is dummy in pyjs.

from pyjamas.ui import Event

from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Button import Button

from pyjamas import DOM
from config import conf




class ClickableLabel( FocusWidget ):
	"""
		Provides a clickable label for panes.
		Its not possible to catch clicks on a pane directly
		as it also catches clicks for its children.
	"""
	def __init__( self, descr ):
		self.element = DOM.createElement("a")
		super( ClickableLabel, self ).__init__( self.element )
		DOM.setElemAttribute(self.element,"href","#")
		self.element.innerHTML = descr
		self.sinkEvents(Event.ONCLICK | Event.MOUSEEVENTS)

class Pane( Widget ):
	"""
		Base class for Panes.
		A pane represents a entry in the left menu aswell
		as a list of widgets associated with this pane.
		Its possible to stack panes ontop of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr, icon=None, closeable=False ):
		self.element = DOM.createElement("li")
		super( Pane, self ).__init__( self.element )
		self.descr = descr
		self.icon = icon
		self.closeable = closeable
		self.widgets = []
		self.childPanes = []
		self.widgetsDomElm = DOM.createElement("div")
		self.childDomElem = None
		self.label = ClickableLabel( descr )
		DOM.appendChild(self.getElement(), self.label.getElement())
		self.label.onAttach()
		self.label.addClickListener( self.onClick )
		if closeable:
			self.closeBtn = Button("X", self.onBtnCloseReleased)
			DOM.appendChild(self.getElement(),self.closeBtn.getElement())
			self.closeBtn.onAttach()

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
			self.childDomElem = DOM.createElement("ul")
			DOM.setElemAttribute(self.childDomElem, "class", "actionlist")
			DOM.appendChild( self.getElement(), self.childDomElem )
		DOM.appendChild( self.childDomElem, pane.getElement() )

	def removeChildPane(self, pane):
		assert pane in self.childPanes, "Cannot remove unknown child-pane %s from %s" % (str(pane),str(self))
		self.childPanes.remove( pane )
		DOM.removeChild( self.childDomElem, pane.getElement() )
		if len(self.childPanes)==0: #No more children, remove the UL element
			DOM.removeChild( self.getElement(), self.childDomElem )
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
		self.widgets.append( widget )
		DOM.appendChild( self.widgetsDomElm, widget.getElement() )
		widget.onAttach()

	def removeWidget(self, widget):
		assert widget in self.widgets, "Cannot remove unknown widget %s" % str(widget)
		self.widgets.remove( widget )
		DOM.removeChild( self.widgetsDomElm, widget.getElement() )
		widget.onDetach()

	def onClick(self, *args, **kwargs ):
		self.focus()

	def focus(self):
		conf["mainWindow"].focusPane( self )