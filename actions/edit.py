import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from i18n import translate

class SaveContinue( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( SaveContinue, self ).__init__( translate("Save-Continue"), *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--save-continue"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="save.continue" )

	def onClick(self, sender=None):
		self["class"].append("is-loading")
		self.parent().parent().doSave(closeOnSuccess=False)

	def resetLoadingState(self):
		if "is-loading" in self["class"]:
			self["class"].remove("is-loading")

actionDelegateSelector.insert( 1, SaveContinue.isSuitableFor, SaveContinue )

class SaveSingleton(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(SaveSingleton, self).__init__(translate("Save"), *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "save.singleton" and module != "_tasks"

	def onClick(self, sender=None):
		self["class"].append("is-loading")
		self.parent().parent().doSave(closeOnSuccess=False)

	def resetLoadingState(self):
		if "is-loading" in self["class"]:
			self["class"].remove("is-loading")

actionDelegateSelector.insert(1, SaveSingleton.isSuitableFor, SaveSingleton)

class ExecuteSingleton(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(ExecuteSingleton, self).__init__(translate("Execute"), *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "save.singleton" and module == "_tasks"

	def onClick(self, sender=None):
		self["class"].append("is-loading")
		self.parent().parent().doSave(closeOnSuccess=True)

	def resetLoadingState(self):
		if "is-loading" in self["class"]:
			self["class"].remove("is-loading")

actionDelegateSelector.insert(1, ExecuteSingleton.isSuitableFor, ExecuteSingleton)

class SaveClose( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( SaveClose, self ).__init__( translate("Save-Close"), *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( actionName=="save.close" )

	def onClick(self, sender=None):
		self.addClass("is-loading")
		self.parent().parent().doSave(closeOnSuccess=True)

	def resetLoadingState(self):
		if "is-loading" in self["class"]:
			self.removeClass("is-loading")
		pass

actionDelegateSelector.insert( 1, SaveClose.isSuitableFor, SaveClose )


class Refresh(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(Refresh, self).__init__(translate("Reload"), *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--reload"

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return actionName == "refresh"

	def onClick(self, sender=None):
		if self.parent().parent().modified:
			html5.ext.YesNoDialog(translate("vi.action.edit.refresh.question"),
		                            translate("vi.action.edit.refresh.title"),
		                            yesCallback=self.performReload)
		else:
			self.performReload()

	def performReload(self, sender=None):
		self.addClass("is-loading")
		self.parent().parent().reloadData()

	def resetLoadingState(self):
		self.removeClass("is-loading")


actionDelegateSelector.insert(1, Refresh.isSuitableFor, Refresh)
