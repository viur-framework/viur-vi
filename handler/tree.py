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
from config import conf
from widgets import ModulListWidget, TopBarWidget
from __pyjamas__ import JS
import json
from network import NetworkService
from priorityqueue import HandlerClassSelector
from widgets import TreeWidget
from config import conf
import pygwt
from pane import Pane


class TreeHandler( Pane ):
	def __init__(self, modulName, modulInfo, *args, **kwargs):
		super( TreeHandler, self ).__init__( modulName )
		self.modulName = modulName



	@staticmethod
	def canHandle( modulName, modulInfo ):
		return( modulInfo["handler"]=="tree" or modulInfo["handler"].startswith("tree."))

	def onClick(self, *args, **kwargs ):
		print("CLICK")
		if not len(self.widgets):
			self.addWidget( TreeWidget(self.modulName ) )
		super( TreeHandler, self ).onClick()


HandlerClassSelector.insert( 3, TreeHandler.canHandle, TreeHandler )
