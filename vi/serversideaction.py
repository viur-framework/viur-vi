import logging

from flare.button import Button
from flare.html5 import window
from flare.network import NetworkService, NiceErrorAndThen
from flare.safeeval import SafeEval
from flare.i18n import translate
from flare.popup import Confirm

from vi.config import conf


class ServerSideActionWdg(Button):
	def __init__(self, module, handler, actionName, actionData):
		super(ServerSideActionWdg, self).__init__(actionData["name"], icon=actionData["icon"])
		self.module = module
		self.handler = handler
		self.actionName = actionName
		self.actionData = actionData
		self.multiSelection = self.actionData.get("allowMultiSelection", False)
		self["class"] = "bar-item btn btn--small %s" % actionData["icon"]
		self["disabled"] = True
		self.isDisabled = True
		self.pendingFetches = []
		self.selectionCheckerAst = None
		self.additionalEvalData = actionData.get("additionalEvalData")
		self.sinkEvent("onClick")

		self.se = SafeEval()
		if "enabled" in actionData:
			try:
				self.selectionCheckerAst = self.se.compile(actionData["enabled"])
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

	def onSelectionChanged(self, table, selection, *args, **kwargs):
		if self.actionData.get("enabled") == "True":
			self.switchDisabledState(False)
			return

		if self.multiSelection and len(selection) > 0 or len(selection) == 1:
			if not self.pendingFetches:
				if self.selectionCheckerAst:
					valid = True
					for sel in selection:
						try:
							if not self.se.execute(self.selectionCheckerAst,
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
		if self.actionData.get("confirm",None) and self.actionData["confirm"]:
			Confirm(self.actionData["confirm"],
					title=translate(self.actionData['name']),
					yesCallback=self.apply)
		else:
			self.apply()


	def apply(self,sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if self.actionData["action"] == "view":
			url_parts = self.actionData['url'].split("/")
			targetInfo = conf["modules"][url_parts[0]]

			if "params" in self.actionData:
				if selection:
					targetInfo.update({k: v.replace("{{key}}", selection[0]["key"]) for k, v in self.actionData["params"].items()})
				else:
					targetInfo.update(self.actionData["params"])
			conf["mainWindow"].openView(
				translate("{{module}} - {{name}}", module=targetInfo["name"], name=self.actionData['name']),
				targetInfo.get("icon") or "icon-edit",
				targetInfo["moduleName"] + targetInfo["handler"],
				targetInfo["moduleName"],
				None,  # is not used...
				data=targetInfo
				#data=utils.mergeDict(self.adminInfo, {"context": context})
			)

		else:
			if self.multiSelection and len(selection) > 0 or len(selection) == 1:
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
			elif self.actionData["enabled"] == "True":
				wasIdle = not self.pendingFetches
				if self.actionData["action"] == "open":
					url = self.actionData["url"]
					window.open(url, "_blank")
				elif self.actionData["action"] == "fetch":
					url = self.actionData["url"]
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
			failureHandler=NiceErrorAndThen(self.fetchFailed)
		)

	def fetchSucceeded(self, req):
		if self.pendingFetches:
			self.fetchNext()
		else:
			conf["mainWindow"].log("success", "Done")

			self.removeClass("is-loading")
			NetworkService.notifyChange(self.parent().parent().module)

	def fetchFailed(self):
		self.pendingFetches = []
		self.resetLoadingState()

	def resetLoadingState(self):
		self.removeClass("is-loading")
