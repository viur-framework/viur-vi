import html5
from priorityqueue import actionDelegateSelector




class ActionBar( html5.Div ):
	def __init__( self, modul, appType, *args, **kwargs ):
		super( ActionBar, self ).__init__(  )
		self.actions = []
		self.modul = modul
		self.appType = appType
		self.element.innerHTML ="ACTIONS"

	def setActions(self, actions):
		self.element.innerHTML = actions
		self.actions = actions
		for action in actions:
			if action=="|":
				continue
			else:
				actionWdg = actionDelegateSelector.select( "%s.%s" % (self.appType, self.modul), action )
				print("HAVE ACTION for", action)
				if actionWdg is not None:
					actionWdg = actionWdg( self.parent )
					self.appendChild( actionWdg )

	def getActions(self):
		return( self.actions )
