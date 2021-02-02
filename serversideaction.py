# -*- coding: utf-8 -*-

from vi.config import conf
from flare.html5 import window
from flare.button import Button
from flare.safeeval import SafeEval
from flare.network import NetworkService
import logging


class ServerSideActionWdg(Button):
	def __init__(self, module, handler, actionName, actionData):
		super(ServerSideActionWdg, self).__init__(actionData["name"])
		self.module = module
		self.handler = handler
		self.actionName = actionName
		self.actionData = actionData
		self["class"] = "bar-item btn btn--small %s" % actionData["icon"]
		self["disabled"] = True
		self.isDisabled = True
		self.pendingFetches = []
		self.selectionCheckerAst = None
		self.additionalEvalData = actionData.get("additionalEvalData")
		self.sinkEvent("onClick")
		if "enabled" in actionData:
			try:
				self.selectionCheckerAst = SafeEval.parse(actionData["enabled"])
			except:
				pass

	def switchDisabledState(self, disabled):
		if not disabled:
			if self.isDisabled:
				self.isDisabled = False
				self["disabled"] = False
		else:
			if not self.isDisabled:
				self["disabled"] = True
				self.isDisabled = True

	def onAttach(self):
		super(ServerSideActionWdg, self).onAttach()
		self.parent().parent().selectionChangedEvent.register(self)

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister(self)
		super(ServerSideActionWdg, self).onDetach()

	def onSelectionChanged(self, table, selection):
		if self.actionData["allowMultiSelection"] and len(selection) > 0 or len(selection) == 1:
			if not self.pendingFetches:
				if self.selectionCheckerAst:
					valid = True
					for sel in selection:
						try:
							if not SafeEval.evalAst(self.selectionCheckerAst,
													{"skel": sel, "additionalEvalData": self.additionalEvalData}):
								valid = False
								break
						except Exception as e:
							logging.exception(e)
							valid = False
							break
					self.switchDisabledState(not valid)
				else:
					self.switchDisabledState(False)
		else:
			self.switchDisabledState(True)

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if self.actionData["allowMultiSelection"] and len(selection) > 0 or len(selection) == 1:
			# if (len(selection) == 1 and not self.actionData["allowMultiSelection"]) or len(selection) > 0:
			wasIdle = not self.pendingFetches
			for item in selection:
				if self.actionData["action"] == "open":
					url = self.actionData["url"].replace("{{key}}", item["key"])
					window.open(url, "_blank")
				elif self.actionData["action"] == "fetch":
					url = self.actionData["url"].replace("{{key}}", item["key"])
					self.pendingFetches.append(url)
				else:
					raise NotImplementedError()
			if wasIdle and self.pendingFetches:
				self.addClass("is-loading")
				self.fetchNext()

	def fetchNext(self):
		if not self.pendingFetches:
			return
		url = self.pendingFetches.pop()
		NetworkService.request(
			None, url, secure=True,
			successHandler=self.fetchSucceeded,
			failureHandler=self.fetchFailed
		)

	def fetchSucceeded(self, req):
		if self.pendingFetches:
			self.fetchNext()
		else:
			conf["mainWindow"].log("success", "Done :)")

			self.removeClass("is-loading")
			NetworkService.notifyChange(self.parent().parent().module)

	def fetchFailed(self, req):
		self.pendingFetches = []
		conf["mainWindow"].log("failed", "Failed :(")

	def resetLoadingState(self):
		self.removeClass("is-loading")
