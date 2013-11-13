import html5
from priorityqueue import actionDelegateSelector
from config import conf



class ActionBar( html5.Div ):
	"""
		Provides the container for actions (add,edit,..) suitable for one modul (eg. for lists).
	"""
	def __init__( self, modul, appType, *args, **kwargs ):
		"""
			@param modul: Name of the modul were going to handle
			@type modul: String
			@param appType: Type of the application (list, tree, hierarchy, ..)
			@type appType: String
		"""
		super( ActionBar, self ).__init__(  )
		self.actions = []
		self.modul = modul
		self.appType = appType
		self.element.innerHTML ="ACTIONS"

	def setActions(self, actions):
		"""
			Sets the list of valid actions for this modul.
			This function tries to resolve a suitable action-widget for each
			given action-name and adds them on success.
			All previous actions are removed.
			@param actions: List of names of actions which should be avaiable.
			@type actions: List of String
		"""
		for c in self._children[:]:
			self.removeChild( c )
		self.actions = actions
		for action in actions:
			if action=="|":
				continue
			else:
				print()
				actionWdg = actionDelegateSelector.select( conf["modules"][self.modul]["handler"], action )
				print("HAVE ACTION for", action, actionWdg)
				if actionWdg is not None:
					actionWdg = actionWdg( )
					self.appendChild( actionWdg )

	def getActions(self):
		"""
			Returns the list of action-names currently active for this modul.
			May also contain action-names which couldn't be resolved and therefore
			not displayed.
			@returns: List of String
		"""
		return( self.actions )
