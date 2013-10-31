import pyjd # this is dummy in pyjs.
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Label import Label
from pyjamas.ui import Event
from pyjamas import Window
from pyjamas.HTTPRequest import HTTPRequest
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui.Widget import Widget
from pyjamas.ui.Panel import Panel
from pyjamas import DOM
import json
from network import NetworkService
from widgets.table import DataTable
from priorityqueue import actionDelegateSelector
import pygwt




class ActionBar( Widget ):
	def __init__( self, parent, modul, *args, **kwargs ):
		self.element = DOM.createElement("div")
		super( ActionBar, self ).__init__( self.element )
		self.actions = []
		self.modul = modul
		self.element.innerHTML ="ACTIONS"
		self.parent = parent

	def setActions(self, actions):
		self.element.innerHTML = actions
		self.actions = actions
		for action in actions:
			if action=="|":
				continue
			else:
				actionWdg = actionDelegateSelector.select( "list.%s" % self.modul, action )
				if actionWdg is not None:
					actionWdg = actionWdg( self.parent )
					DOM.appendChild( self.element, actionWdg.getElement() )
					actionWdg.onAttach()
					actionWdg.parent = self.parent

	def getActions(self):
		return( self.actions )
