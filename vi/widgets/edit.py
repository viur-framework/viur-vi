import pyodide
import logging

from flare import html5
from flare.popup import Confirm

from flare.network import NetworkService, DeferredCall
from flare.viur import ViurForm
from flare.i18n import translate

from vi import utils
from vi.config import conf
from vi.framework.components.actionbar import ActionBar
from vi.widgets.list import ListWidget
from vi.widgets.tree import TreeWidget
from vi.widgets.accordion import Accordion


def parseHashParameters(src, prefix=""):
	"""
		Converts a flat dictionary containing dotted properties into a multi-dimensional one.

		Example:
			{ "a":"a", "b.a":"ba","b.b":"bb" } -> { "a":"a", "b":{"a":"ba","b":"bb"} }

		If a dictionary contains only numeric indexes, it will be converted to a list:
			{ "a.0.a":"a0a", "a.0.b":"a0b",a.1.a":"a1a" } -> { "a":[{"a":"a0a","b":"a0b"},{"a":"a1a"}] }

	"""

	res = {}
	processedPrefixes = []  # Dont process a prefix twice

	for k, v in src.items():
		if prefix and not k.startswith(prefix):
			continue

		if prefix:
			k = k.replace(prefix, "")

		if not "." in k:
			if k in res.keys():
				if not isinstance(res[k], list):
					res[k] = [res[k]]
				res[k].append(v)
			else:
				res[k] = v

		else:
			newPrefix = k[:k.find(".")]

			if newPrefix in processedPrefixes:  # We did this already
				continue

			processedPrefixes.append(newPrefix)

			if newPrefix in res.keys():
				if not isinstance(res[newPrefix], list):
					res[newPrefix] = [res[newPrefix]]
				res[newPrefix].append(parseHashParameters(src, prefix="%s%s." % (prefix, newPrefix)))

			else:
				res[newPrefix] = parseHashParameters(src, prefix="%s%s." % (prefix, newPrefix))

	if all([x.isdigit() for x in res.keys()]):
		newRes = []
		keys = [int(x) for x in res.keys()]
		keys.sort()

		for k in keys:
			newRes.append(res[str(k)])

		return newRes

	return res


class EditWidget(html5.Div):
	appList = "list"
	appHierarchy = "hierarchy"
	appTree = "tree"
	appSingleton = "singleton"
	__editIdx_ = 0  # Internal counter to ensure unique ids

	def __init__(self, module, applicationType, key=None, node=None, skelType=None, clone=False, action=None,
				hashArgs=None, context=None, logAction="Entry saved!", skel=None, *args, **kwargs):
		"""
			Initialize a new Edit or Add-Widget for the given module.
			:param module: Name of the module
			:type module: str
			:param applicationType: Defines for what application this Add / Edit should be created. This hides additional complexity introduced by the hierarchy / tree-application
			:type applicationType: Any of EditWidget.appList, EditWidget.appHierarchy, EditWidget.appTree or EditWidget.appSingleton
			:param id: ID of the entry. If none, it will add a new Entry.
			:type id: Number
			:param rootNode: If applicationType==EditWidget.appHierarchy, the new entry will be added under this node, if applicationType==EditWidget,appTree the final node is derived from this and the path-parameter.
			Has no effect if applicationType is not appHierarchy or appTree or if an id have been set.
			:type rootNode: str
			:param path: Specifies the path from the rootNode for new entries in a treeApplication
			:type path: str
			:param clone: If true, it will load the values from the given id, but will save a new entry (i.e. allows "cloning" an existing entry)
			:type clone: bool
			:param hashArgs: Dictionary of parameters (usually supplied by the window.hash property) which should prefill values.
			:type hashArgs: dict
		"""
		if module not in conf["modules"]:
			conf["mainWindow"].log(
				"error",
				translate("The module '{{module}}' does not exist.", module=module),
				modul=self.module,
				key=self.key,
				action=self.action
			)
			return

		super().__init__(context=context)
		self.addClass("vi-widget vi-widget--edit")
		self.sinkEvent("onChange")

		# A Bunch of santy-checks, as there is a great chance to mess around with this widget
		assert applicationType in (
			EditWidget.appList,
			EditWidget.appHierarchy,
			EditWidget.appTree,
			EditWidget.appSingleton
		)  # Invalid Application-Type?

		if applicationType == EditWidget.appHierarchy or applicationType == EditWidget.appTree:
			assert key is not None or node is not None  # Need either an entry or a node
		elif applicationType == EditWidget.appTree:
			assert skelType
		elif applicationType == EditWidget.appSingleton:
			key = ""
			clone = False

		# Initialize instance variables
		self.editIdx = EditWidget.__editIdx_  # Internal counter to ensure unique ids
		EditWidget.__editIdx_ += 1

		self.module = module
		self.applicationType = applicationType
		self.key = key
		self.modified = False

		self.action = action or ("add" if key is None else "clone" if clone else "edit")
		self.node = node
		self.skelType = skelType
		self.skel = skel or {}
		self.closeOnSuccess = False
		self.logAction = logAction

		self.context = context or {}
		self.context["__action__"] = self.action
		self.context["__mode__"] = self.action  # fixme: deprecated, replaced by __action__

		self.group = None
		if "group" in kwargs and kwargs["group"]:
			self.group = kwargs["group"]

		self.segments = {}
		self.views = {}

		if hashArgs:
			self._hashArgs = parseHashParameters(hashArgs)
		else:
			self._hashArgs = None

		self.editTaskID = None
		self.wasInitialRequest = True  # Wherever the last request attempted to save data or just fetched the form

		# Widgets
		self.form = None
		self.actionbar = ActionBar(self.module, self.applicationType, self.action)
		self.appendChild(self.actionbar)

		editActions = []

		if self.action == "edit":
			editActions.append("refresh")

		if module in conf["modules"] and conf["modules"][module]:
			editActions.extend(conf["modules"][module].get("editActions", []))

		if applicationType == EditWidget.appSingleton:
			self.actionbar.setActions(["save.singleton"] + editActions, widget=self)
		else:
			self.actionbar.setActions(["save.continue", "save.close"] + editActions, widget=self)

		# Input form
		self.accordion = Accordion()
		self.accordion.addClass("flr-form")
		self.appendChild(self.accordion)

		# Engage
		self.reloadData()

	def onDetach(self):
		utils.setPreventUnloading(False)
		super(EditWidget, self).onDetach()

	def onAttach(self):
		super(EditWidget, self).onAttach()
		utils.setPreventUnloading(True)

	def onChange(self, event):
		assert self.form
		self.modified = True
		DeferredCall(self.form.update)

	def onBoneChange(self, bone):
		assert self.form
		self.modified = True
		DeferredCall(self.form.update)

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displays an error message
		"""
		# Try to obtain error reason from header
		if not (reason := pyodide.create_once_callable(req.request.req.getResponseHeader)("x-viur-error")):
			reason = translate(
				f"flare.network.error.{code}", fallback=translate("flare.network.error")
			)

		hint = translate(f"flare.network.hint.{code}", fallback="")

		conf["mainWindow"].log(
			"error",
			reason + ((". " + hint) if hint else "")
		)

		if self.wasInitialRequest:
			conf["mainWindow"].removeWidget(self)

		self.actionbar.resetLoadingState()

	def reloadData(self):
		self.form = None  # rebuild the entire form
		self._save({})

	def _save(self, data):
		"""
			Creates the actual NetworkService request used to transmit our data.
			If data is None, it fetches a clean add/edit form.

			:param data: The values to transmit or None to fetch a new, clean add/edit form.
			:type data: dict or None
		"""
		data.pop("key", None)  # "key" is only stored in self.key, and must be removed here.
		self.wasInitialRequest = not len(data) > 0

		if self.context:
			# Data takes precedence over context.
			ndata = self.context.copy()
			ndata.update(data.copy())
			data = ndata

		# Add node to parameters if set
		if self.node:
			data["node"] = self.node

		# Construct the URL
		url = [self.action]

		for part in (self.skelType, self.group, self.key):
			if part:
				url.append(part)

		conf["theApp"].setPath("/".join([self.module] + url))

		NetworkService.request(
			self.module,
			"/".join(url),
			data,
			secure=not self.wasInitialRequest,
			successHandler=self.setData,
			failureHandler=self.showErrorMsg
		)

	def clear(self):
		"""
			Removes all visible bones/forms/fieldsets.
		"""
		self.accordion.clear()
		self.segments.clear()
		self.views.clear()

	def closeOrContinue(self, sender=None):
		self.modified = False
		NetworkService.notifyChange(self.module, key=self.key, action=self.action)

		if self.closeOnSuccess:
			if self.module == "_tasks":
				self.parent().parent().parent().close()
				return

			if not conf["mainWindow"].navWrapper.removeNavigationPoint(self.parent().view.name):
				conf["mainWindow"].removeWidget(self.parent())  # if no navpoint try to kill popup
			return

		self.clear()

		if self.action == "add":
			self.key = None

		self.reloadData()

	def setData(self, request=None, data=None):
		"""
		Rebuilds the UI according to the skeleton received from server

		:param request: A finished NetworkService request
		:type request: NetworkService
		:type data: dict
		:param data: The data received
		"""
		assert (request or data)

		if request:
			data = NetworkService.decode(request)

		if not self.wasInitialRequest:
			self.addClass("form-group--validation")

		# Reset loading state
		self.actionbar.resetLoadingState()

		if data.get("action") == self.action + "Success":
			try:
				self.key = data["values"]["key"]
			except:
				self.key = None

			conf["mainWindow"].log("success", translate(self.logAction),
				modul=self.module, key=self.key, action=self.action, data=data
			)

			self.closeOrContinue()
			return

		# Context-Variables
		contextVariable = conf["modules"][self.module].get("editContext")
		if self.action == "edit" and contextVariable:
			if not self.context:
				self.context = {}

			if "=" in contextVariable:
				contextVariable, contextKey = contextVariable.split("=", 1)
			else:
				contextKey = "key"

			self.context.update({
				contextVariable: data["values"].get(contextKey)
			})

		if not self.form:
			self.clear()

			# Build the form as ViurForm with the available information as internalForm first.
			# The bone widgets inside it are being re-arranged afterwards.
			self.form = ViurForm(
				skel=self.skel if self.wasInitialRequest and self.skel else data["values"],
				structure=data["structure"],
				context=self.context
			)
			self.form.buildInternalForm()
			init = True
		else:
			init = False

		hasMissing = False
		firstCat = None
		defaultCat = conf["modules"][self.module].get("name", self.module)  # Name of the default category
		adminCat = conf["modules"][self.module].get("defaultCategory", None)  # The category displayed first (I think...)

		for name, bone in self.form.bones.items():
			desc = self.form.structure[name]

			# Get category from bone description
			cat = desc["params"].get("category") or defaultCat

			if init:
				if cat not in self.segments:
					self.segments[cat] = self.accordion.addSegment(cat)

				# Move the bone from the ViurForm into our segment.
				self.segments[cat].addWidget(bone)

			# Hide invisible bones or logic-flavored bones with their default desire
			if not firstCat and not adminCat:
				firstCat = self.segments[cat]
			elif adminCat and cat == adminCat:
				firstCat = self.segments[cat]

		# Render errors (if any)
		self.form.errors = data.get("errors")
		self.form.handleErrors()

		# Hide all segments where all fields are invisible
		for segment in self.segments.values():
			segment.checkVisibility()

		if init:
			# Show default category
			if firstCat and init:
				firstCat.activate()

			self.accordion.buildAccordion("asc")  # order and add to dom

		# Views
		views = conf["modules"][self.module].get("editViews")
		if self.action == "edit" and isinstance(views, list):
			for view in views:
				vmodule = view.get("module")
				vvariable = view.get("context")
				vclass = view.get("class")
				vtitle = view.get("title")
				vcolumns = view.get("columns")
				vfilter = view.get("filter")

				if not vmodule:
					print("Misconfiured view: %s" % view)
					continue

				if vmodule not in conf["modules"]:
					print("Module '%s' is not described." % vmodule)
					continue

				vdescr = conf["modules"][vmodule]

				if vmodule not in self.segments:
					self.segments[vmodule] = self.accordion.addSegment(
						vmodule, vtitle or vdescr.get("name", vmodule), directAdd=True
					)
					self.segments[vmodule].addClass("editview")

				if vclass:
					self.segments[vmodule].addClass(*vclass)

				if vvariable:
					context = self.context.copy() if self.context else {}
					if isinstance(vvariable, str):
						context[vvariable] = data["values"]["key"]
					elif isinstance(vvariable, dict):
						context |= {v: data["values"][k] for v, k in vvariable.items()}
				else:
					context = self.context

				if vdescr["handler"] == "list" or vdescr["handler"].startswith("list."):
					self.views[vmodule] = ListWidget(
						vmodule, filter=vfilter or vdescr.get("filter", {}),
						columns=vcolumns or vdescr.get("columns"),
						context=context
					)
				elif vdescr["handler"] == "tree" or vdescr["handler"].startswith("tree."):
					self.views[vmodule] = TreeWidget(vmodule, context=context)
				else:
					logging.error(f"Handler {vdescr['handler']} is not supported")
					continue

				self.segments[vmodule].addWidget(self.views[vmodule])

		if self._hashArgs:  # Apply the default values (if any)
			self.form.unserialize(self._hashArgs)
			self._hashArgs = None

		if hasMissing and not self.wasInitialRequest:
			conf["mainWindow"].log(
				"warning", translate("Could not save entry!"),
				icon="icon-cancel",
				modul=self.module,
				key=self.key,
				action=self.action,
				data=data["values"]
			)

	def doSave(self, closeOnSuccess=False, *args, **kwargs):
		"""
			Starts serializing and transmitting values to the server.
		"""
		self.closeOnSuccess = closeOnSuccess

		assert self.form
		res = self.form.serialize()
		if res:
			self._save(res)
