import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane

class SaveContinue( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( SaveContinue, self ).__init__( "Save-Continue", *args, **kwargs )
		self["class"] = "icon save continue"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="save.continue" )

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		self.parent().parent().doSave(closeOnSuccess=False)

	def resetLoadingState(self):
		if "is_loading" in self["class"]:
			self["class"].remove("is_loading")

actionDelegateSelector.insert( 1, SaveContinue.isSuitableFor, SaveContinue )

class SaveClose( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( SaveClose, self ).__init__( "Save-Close", *args, **kwargs )
		self["class"] = "icon save close"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="save.close" )

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		self.parent().parent().doSave(closeOnSuccess=True)

	def resetLoadingState(self):
		if "is_loading" in self["class"]:
			self["class"].remove("is_loading")
		pass

actionDelegateSelector.insert( 1, SaveClose.isSuitableFor, SaveClose )