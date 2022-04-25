import pyodide

from flare import html5
from flare.popup import Confirm

from flare.network import NetworkService, DeferredCall
from flare.viur import ViurForm
from flare.i18n import translate

from vi import utils
from vi.config import conf
from vi.framework.components.actionbar import ActionBar
from vi.widgets.list import ListWidget
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

	def __init__(self, module, applicationType, key=0, node=None, skelType=None, clone=False,
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
				action=self.mode
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
			assert key is not None or node is not None  # Need either an id or an node

		if clone:
			assert key is not None  # Need an id if we should clone an entry
			assert not applicationType == EditWidget.appSingleton  # We cant clone a singleton
			if applicationType == EditWidget.appHierarchy or applicationType == EditWidget.appTree:
				assert node is not None  # We still need a rootNode for cloning
			if applicationType == EditWidget.appTree:
				assert node is not None  # We still need a path for cloning #FIXME

			self.cloneOf = key
		else:
			self.cloneOf = None

		# Initialize instance variables
		self.editIdx = EditWidget.__editIdx_  # Internal counter to ensure unique ids
		EditWidget.__editIdx_ += 1

		self.module = module
		self.applicationType = applicationType
		self.key = key
		self.modified = False
		self.mode = "edit" if self.key or applicationType == EditWidget.appSingleton else "add"
		self.node = node
		self.skelType = skelType
		self.skel = skel or {}
		self.clone = clone
		self.closeOnSuccess = False
		self.logAction = logAction

		self.context = context or {}
		self.context["__mode__"] = self.mode

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
		self.actionbar = ActionBar(self.module, self.applicationType, (self.mode if not clone else "clone"))
		self.appendChild(self.actionbar)

		editActions = []

		if self.mode == "edit":
			editActions.append("refresh")

		if module in conf["modules"] and conf["modules"][module]:
			editActions.extend(conf["modules"][module].get("editActions", []))

		if applicationType == EditWidget.appSingleton:
			self.actionbar.setActions(["save.singleton"] + editActions, widget=self)
		else:
			self.actionbar.setActions(["save.continue", "save.close"] + editActions, widget=self)

		pathList = [module]

		if clone:
			curr_mode = "clone"
		else:
			curr_mode = self.mode

		pathList.append(curr_mode)

		if self.group:
			pathList.append(self.group)

		if self.mode == "edit" and applicationType != EditWidget.appSingleton:
			pathList.append(self.key)

		conf[ "theApp" ].setPath( "/".join( pathList ) )

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

		if self.module == "_tasks":
			NetworkService.request(
				self.module, "execute/%s" % self.key, data,
				secure=not self.wasInitialRequest,
				successHandler=self.setData,
				failureHandler=self.showErrorMsg
			)

		elif self.applicationType == EditWidget.appList:  ## Application: List

			if self.group:
				if self.key and (not self.clone or self.wasInitialRequest):
					NetworkService.request(self.module, "edit/%s/%s" % (self.group, self.key), data,
										   secure=not self.wasInitialRequest,
										   successHandler=self.setData,
										   failureHandler=self.showErrorMsg)
				else:
					NetworkService.request(self.module, "add/%s" % self.group, data,
										   secure=not self.wasInitialRequest,
										   successHandler=self.setData,
										   failureHandler=self.showErrorMsg)
			else:

				if self.key and (not self.clone or self.wasInitialRequest):
					NetworkService.request(
						self.module, "edit/%s" % self.key, data,
						secure=not self.wasInitialRequest,
						successHandler=self.setData,
						failureHandler=self.showErrorMsg
					)
				else:
					NetworkService.request(
						self.module, "add", data,
						secure=not self.wasInitialRequest,
						successHandler=self.setData,
						failureHandler=self.showErrorMsg
					)

		elif self.applicationType == EditWidget.appTree or self.applicationType == EditWidget.appHierarchy:  ## Application: Tree
			if self.key and not self.clone:
				NetworkService.request(
					self.module, "edit/%s/%s" % (self.skelType, self.key), data,
					secure=not self.wasInitialRequest,
					successHandler=self.setData,
					failureHandler=self.showErrorMsg
				)
			else:
				NetworkService.request(
					self.module, "add/%s/%s" % (self.skelType, self.node), data,
					secure=not self.wasInitialRequest,
					successHandler=self.setData,
					failureHandler=self.showErrorMsg
				)

		elif self.applicationType == EditWidget.appSingleton:  ## Application: Singleton
			NetworkService.request(
				self.module, "edit", data,
				secure=not self.wasInitialRequest,
				successHandler=self.setData,
				failureHandler=self.showErrorMsg
			)
		else:
			raise NotImplementedError()  # Should never reach this

	def clear(self):
		"""
			Removes all visible bones/forms/fieldsets.
		"""
		self.accordion.clear()
		self.segments.clear()
		self.views.clear()

	def closeOrContinue(self, sender=None):
		self.modified = False
		NetworkService.notifyChange(self.module, key=self.key, action=self.mode)

		if self.closeOnSuccess:
			if self.module == "_tasks":
				self.parent().parent().parent().close()
				return

			if not conf["mainWindow"].navWrapper.removeNavigationPoint(self.parent().view.name):
				conf["mainWindow"].removeWidget(self.parent())  # if no navpoint try to kill popup
			return

		self.clear()

		if self.mode == "add":
			self.key = 0

		self.reloadData()

	def doCloneHierarchy(self, sender=None):
		if self.applicationType == EditWidget.appHierarchy:
			NetworkService.request(
				self.module, "clone", {
					"fromRepo": self.node,
					"toRepo": self.node,
					"fromParent": self.cloneOf,
					"toParent": self.key
				},
				secure=True,
				successHandler=self.cloneComplete
			)
		else:
			for module in conf["modules"][self.module]["changeInvalidates"]:
				NetworkService.request(
					module, "clone", {
						"fromRepo": self.cloneOf,
						"toRepo": self.key
					},
					secure=True,
					successHandler=self.cloneComplete
				)

	def cloneComplete(self, req):
		conf["mainWindow"].log("success", translate("The hierarchy will be cloned in the background."))
		self.closeOrContinue()

	def setData(self, request=None, data=None, askHierarchyCloning=True):
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

		if "action" in data and (data["action"] == "addSuccess" or data["action"] == "editSuccess"):
			try:
				self.key = data["values"]["key"]
			except:
				self.key = None

			conf["mainWindow"].log("success", translate(self.logAction),
				modul=self.module, key=self.key, action=self.mode, data=data
			)

			if askHierarchyCloning and self.clone:
				# for lists, which are rootNode entries of hierarchies, ask to clone entire hierarchy
				if self.applicationType == EditWidget.appList and "changeInvalidates" in conf["modules"][self.module]:
					Confirm(
						translate("Do you want to clone the entire hierarchy?"),
						yesCallback=self.doCloneHierarchy,
						noCallback=self.closeOrContinue
					)
					return
				# for cloning within a hierarchy, ask for cloning all subentries.
				elif self.applicationType == EditWidget.appHierarchy:
					Confirm(
						translate("Do you want to clone all subentries of this item?"),
						yesCallback=self.doCloneHierarchy,
						noCallback=self.closeOrContinue
					)
					return

			self.closeOrContinue()
			return

		# Context-Variables
		contextVariable = conf["modules"][self.module].get("editContext")
		if self.mode == "edit" and contextVariable:
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
				skel=data["values"],
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
		if self.mode == "edit" and isinstance(views, list):
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
					context[vvariable] = data["values"]["key"]
				else:
					context = self.context

				self.views[vmodule] = ListWidget(
					vmodule, filter=vfilter or vdescr.get("filter", {}),
					columns=vcolumns or vdescr.get("columns"),
					context=context
				)
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
				action=self.mode,
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
