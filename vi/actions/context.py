#-*- coding: utf-8 -*-
from vi import utils

from vi.widgets import ListWidget, EditWidget
from vi.priorityqueue import actionDelegateSelector, ModuleWidgetSelector
from flare.i18n import translate
from vi.config import conf
from vi.pane import Pane
from flare.button import Button


class ContextAction(Button):
	def __init__(self, module, handler, actionName, *args, **kwargs):
		dsc = actionName.split(".", 3)
		assert dsc[0] == "context", u"Invalid definition!"
		mod = dsc[1]
		vars = dsc[2].split(",")

		assert mod in conf["modules"], "The module '%s' must provide an adminInfo when run in a context action"
		adminInfo = conf["modules"][mod]

		if "name" in adminInfo:
			title = adminInfo["name"]
		else:
			title = mod

		icon = adminInfo.get("icon")

		super(ContextAction, self).__init__(text=title, icon=icon)

		self.widget = None
		self.adminInfo = adminInfo
		self.contextModule = mod
		self.contextVariables = vars

		self.title = title
		self.filter = filter
		self.icon = icon

		self.addClass("context-%s" % self.contextModule)

		self["class"].extend(["bar-item","btn--small"])
		self.disable()

	def onAttach(self):
		super(ContextAction, self).onAttach()

		self.widget = self.parent().parent()

		if isinstance(self.widget, ListWidget):
			self.widget.selectionChangedEvent.register(self)
		elif isinstance(self.widget, EditWidget) and self.widget.mode == "edit":
			self.enable()

	def onDetach(self):
		if isinstance(self.widget, ListWidget):
			self.widget.selectionChangedEvent.unregister(self)

		super(ContextAction, self).onDetach()

	def onSelectionChanged(self, table, selection):
		if len(selection) > 0:
			self.enable()
		else:
			self.disable()

	def onClick(self, sender=None):
		assert self.widget, u"This action must be attached first!"

		if isinstance(self.widget, ListWidget):
			for s in self.widget.getCurrentSelection():
				self.openModule(s)

		elif isinstance(self.widget, EditWidget):
			d = self.widget.serializeForDocument()
			self.openModule(d)

	def openModule(self, data, title = None):
		# Have a handler?
		widgen = ModuleWidgetSelector.select(self.contextModule, self.adminInfo)
		assert widgen

		# Generate title
		if title is None:
			for key in conf["vi.context.title.bones"]:
				title = data.get(key)

				if title:
					if isinstance(title, dict) and conf["currentLanguage"] in title:
						title = title[conf["currentLanguage"]]

					break

		# Merge contexts
		context = {}
		context.update(self.widget.context or {})
		context.update(self.adminInfo.get("context", {}))

		# Evaluate context variables
		for var in self.contextVariables:
			if "=" in var:
				key, value = var.split("=", 1)
				if value[0] == "$":
					value = data.get(value[1:])
			else:
				key = var
				value = data.get("key")

			context[key] = value

		widget = widgen(self.contextModule, **utils.mergeDict(self.adminInfo, context))

		if widget:
			pane = Pane(translate(u"{module} - {name}", module=self.title, name=title),
			            closeable=True, iconURL=self.icon, iconClasses=["module_%s" % self.contextModule])
			conf["mainWindow"].stackPane(pane)

			pane.addWidget(widget)
			pane.focus()
		else:
			print("Widget could not be generated")

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		if module is None or module not in conf["modules"].keys():
			return False

		if not actionName.startswith("context."):
			return False

		mod = actionName.split(".", 3)[1]
		cuser = conf["currentUser"]
		return "root" in cuser["access"] or ("%s-view" % mod) in cuser["access"]

actionDelegateSelector.insert(1, ContextAction.isSuitableFor, ContextAction)
