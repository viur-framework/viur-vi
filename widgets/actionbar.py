import html5
from priorityqueue import actionDelegateSelector
from config import conf
from i18n import translate


class ActionBar( html5.Div ):
	"""
		Provides the container for actions (add,edit,..) suitable for one modul (eg. for lists).
	"""
	def __init__( self, modul, appType, currentAction=None, *args, **kwargs ):
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
		self.currentAction = currentAction
		self["class"].append("actionbar")

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
		if self.currentAction is not None:
			h3 = html5.H3()
			h3["class"].append("modul_%s" % self.modul)
			h3["class"].append("apptype_%s" %self.appType)
			h3["class"].append("action_%s" %self.currentAction)

			h3.appendChild(html5.TextNode(translate(self.currentAction)))
			self.appendChild(h3)
		self.actions = actions
		for action in actions:
			if action=="|":
				continue
			else:
				if self.modul is not None and self.modul in conf["modules"].keys():
					handler = conf["modules"][self.modul]["handler"]
				else:
					handler = ""
				actionWdg = actionDelegateSelector.select( self.modul, handler, action )
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

	def resetLoadingState(self):
		"""
			Resets the loading-state of each child.
			Each child has the ability to provide visual feedback once it has been clicked
			and started working. This function is called from our parent once that action
			has finished, so we can tell our children to return to a sane state.
		"""
		for c in self._children[:]:
			if "resetLoadingState" in dir(c):
				c.resetLoadingState()