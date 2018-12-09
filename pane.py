#-*- coding: utf-8 -*-
import html5
from config import conf
from i18n import translate

class Pane(html5.Div):
	"""
		Base class for Panes.

		A pane represents a entry in the module list as well
		as a list of widgets associated with this pane.

		It is possible to stack panes on-top of each other.
		If a pane is active, _all_ its child widgets are visible
		(through they might overlap).
	"""
	def __init__(self, descr=None, iconURL=None, iconClasses=None, closeable=False, collapseable=True, focusable=True):
		super(Pane, self).__init__()

		self.addClass("vi-pane")

		self.parentPane = None
		self.sinkEvent("onClick")

		self.item = html5.Div()
		self.item.addClass("item has-hover")
		self.appendChild(self.item)

		self.descr = descr
		self.iconURL = iconURL
		self.iconClasses = iconClasses
		self.collapseable = collapseable
		self.focusable = focusable

		self.childPanes = []

		self.widgetsDomElm = html5.Div()
		self.widgetsDomElm.addClass("vi-viewer-pane has-no-child")
		self.childDomElem = None

		self.label = html5.Div()
		self.label.addClass("item-link")
		self.item.appendChild(self.label)

		self.setText(descr, iconURL)

		self.closeBtn = html5.ext.Button(u"×", self.onBtnCloseReleased)
		self.closeBtn["class"] = "item-action"
		self.item.appendChild(self.closeBtn)

		if not closeable:
			self.closeBtn.hide()

		self.closeable = closeable
		self.isExpanded = False

	def __setattr__(self, key, value):
		super(Pane, self).__setattr__(key, value)
		if key == "closeable":
			if value:
				self.closeBtn.show()
			else:
				self.closeBtn.hide()

	def setText(self, descr = None, iconURL = None):
		self.label.removeAllChildren()

		self.itemImage = html5.Div()
		self.itemImage.addClass("item-image")
		self.label.appendChild(self.itemImage)
		self.itemIcon = html5.I()
		self.itemImage.appendChild(self.itemIcon)

		if descr is None:
			descr = self.descr

		if iconURL is None:
			self.itemIcon.appendChild(descr[:1])

		if iconURL is not None:
			img = html5.Img()
			img["src"] = iconURL
			self.itemIcon.appendChild(img)

		if self.iconClasses is not None:
			for cls in self.iconClasses:
				self.label.addClass(cls)

		self.itemContent = html5.Div()
		self.itemContent.addClass("item-content")
		self.label.appendChild(self.itemContent)

		if descr is not None:
			h = html5.H3()
			h.appendChild(descr)
			h.addClass("item-headline")
			self.itemContent.appendChild(h)

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
			self.childDomElem = html5.Div()
			self.childDomElem.addClass("list list--sub")

			if self.collapseable and not pane.closeable:
				self.childDomElem.removeClass("is-active")
			else:
				self.childDomElem.addClass("is-active")

			self.appendChild( self.childDomElem )

			if self.closeable:
				self.closeBtn.hide()

		if ( pane.closeable
			 and "is-active" not in self.childDomElem[ "class" ] ):
			self.childDomElem.addClass("is-active")

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

			if self.closeable:
				self.closeBtn.show()

	def onDetach(self):
		#assert len(self.childPanes)==0, "Attempt to detach a pane which still has subpanes!"
		#Kill all remaining children
		for widget in self.widgetsDomElm.children():
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

		for w in self.widgetsDomElm._children[:]:
			w["disabled"] = True

		self.widgetsDomElm.appendChild( widget )
		self.rebuildChildrenClassInfo()

	def rebuildChildrenClassInfo(self):
		if "has-no-child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm.removeClass("has-no-child")
		if "has-single-child" in self.widgetsDomElm["class"]:
			self.widgetsDomElm.removeClass("has-single-child")
		if "has-multiple-children" in self.widgetsDomElm["class"]:
			self.widgetsDomElm.removeClass("has-multiple-children")
		if len(self.widgetsDomElm._children)==0:
			self.widgetsDomElm.addClass("has-no-child")
		elif len(self.widgetsDomElm._children)==1:
			self.widgetsDomElm.addClass("has-single-child")
		else:
			self.widgetsDomElm.addClass("has-multiple-children")

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

	def onClick(self, event = None, *args, **kwargs ):
		self.focus()

		if event:
			event.stopPropagation()

	def expand(self):
		if self.childDomElem and self.collapseable and not self.isExpanded:
			self.addClass("is-active")
			self.isExpanded = True

	def collapse(self):
		if self.childDomElem and self.collapseable and self.isExpanded:
			self.removeClass("is-active")
			self.isExpanded = False

	def focus(self):
		conf["mainWindow"].focusPane(self)

class GroupPane(Pane):
	"""
		This pane groups subpanes; it cannot have direct childrens
	"""

	def __init__(self, *args, **kwargs):
		super(GroupPane, self ).__init__(*args, **kwargs)
		self.addClass("vi-viewer-grouppane")

		self.childDomElem = html5.Ul()
		self.childDomElem["style"]["display"] = "none"
		self.appendChild(self.childDomElem)

	def onClick(self, event = None, *args, **kwargs):
		if self.isExpanded:
			self.collapse()
		else:
			self.expand()

		if event:
			event.stopPropagation()

	def onFocus(self, event):
		if len(self.childPanes) > 0:
			conf["mainWindow"].focusPane(self.childPanes[0])
