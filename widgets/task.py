# -*- coding: utf-8 -*-

import html5, utils
from config import conf
from i18n import translate
from widgets.edit import EditWidget

class TaskWidget( html5.ext.Popup ):
	def __init__( self, title ):
		super( TaskWidget, self ).__init__( title = title )
		self[ "class" ].append( "popup--task" )
		self.title = title

class ServerTaskWidget( TaskWidget ):
	def __init__( self, title, key ):
		super( ServerTaskWidget, self ).__init__( title = title )
		self.widget = EditWidget( "_tasks", EditWidget.appSingleton, key, logaction = "Task started!" )
		self.popupBody.appendChild( self.widget )
		self.popupBody.removeClass("box--content")
		self.popupFoot.appendChild( html5.ext.Button( translate( "Cancel" ), self.close ) )

class TaskSelectWidget( TaskWidget ):
	def __init__( self ):
		super( TaskSelectWidget, self ).__init__( title = translate( "Select a task" ) )
		self.sinkEvent( "onChange" )

		div = html5.Div()
		div[ "class" ] = [ "task-selector" ]
		self.popupBody.appendChild( div )

		self.select = html5.Select()
		div.appendChild( self.select )

		for type in [ "server", "client" ]:
			for i, task in enumerate( conf[ "tasks" ][ type ] ):
				if type == "client":
					assert task[ "task" ], "task-Attribute must be set for client-side tasks"

				if not "type" in task.keys():
					task[ "type" ] = type

				opt = html5.Option()
				opt.task = task

				opt.appendChild( html5.TextNode( task[ "name" ] ) )

				if not self.select._children:
					opt._setSelected( True )

				self.select.appendChild( opt )

		self.descr = html5.Div()
		self.descr[ "class" ] = [ "task-description" ]
		self.popupBody.appendChild( self.descr )

		self.popupFoot.appendChild( html5.ext.Button( translate( "Cancel" ), self.close ) )
		self.popupFoot.appendChild( html5.ext.Button( translate( "Run" ), self.invokeTask ) )

		# Init
		self.setActiveTask()

	def getSelectedTask(self):
		return self.select._children[ self.select[ "selectedIndex" ] ].task

	def setActiveTask(self):
		task = self.getSelectedTask()
		self.descr.removeAllChildren()
		self.descr.appendChild(
			html5.TextNode(
				task.get( "descr" ) or translate( "No description provided." ) ) )

	def onChange(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.select):
			self.setActiveTask()

	def invokeTask(self, *args, **kwargs):
		task = self.getSelectedTask()
		self.close()

		if task[ "type" ] == "server":
			ServerTaskWidget( task[ "name" ], task[ "key" ] )
		elif task[ "type" ] == "client":
			if not "task" in task.keys():
				return

			task[ "task" ]( task[ "name" ] )
		else:
			raise NotImplementedError()
