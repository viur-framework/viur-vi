# -*- coding: utf-8 -*-

from flare import html5
from flare.forms.formerrors import collectBoneErrors, checkErrors
from flare.popup import Confirm

from collections import defaultdict, deque

import vi.utils as utils

from flare.network import NetworkService, DeferredCall
from vi.config import conf
from flare.forms import boneSelector
from vi.widgets.tooltip import ToolTip
from vi.framework.components.actionbar import ActionBar
from flare.i18n import translate
from vi.widgets.list import ListWidget
from vi.widgets.accordion import Accordion
from vi.exception import InvalidBoneValueException

from js import console




class ParsedErrorItem(html5.Li):
	style = []

	def __init__(self, error):
		super().__init__("""<div><span>Severity: </span><span [name]="errorSeverity"></span>&nbsp;<span>Message: </span><span [name]="errorMessage"></span>
				<div [name]="invalidatedArea"><h4>Invalidated Fields</h4><ul [name]="errorList"></ul></div>
			""")

		self.errorSeverity.element.innerHTML = str(ReadFromClientErrorSeverity(error["severity"])).split(".")[1]
		self.errorMessage.element.innerHTML = error["errorMessage"]
		if error["invalidatedFields"]:
			for item in error["invalidatedFields"]:
				self.errorList.appendChild("<li>{}</li>".format(item))
		else:
			self.invalidatedArea.hide()


class PassiveErrorItem(html5.Li):
	style = []

	def __init__(self, error):
		super().__init__("""<div><span [name]="errorSeverity"></span></div>""")
		self.errorSeverity.element.innerHTML = "Invalidated by other field {}!".format(error["fieldPath"])





def parseHashParameters( src, prefix="" ):
	"""
		Converts a flat dictionary containing dotted properties into a multi-dimensional one.

		Example:
			{ "a":"a", "b.a":"ba","b.b":"bb" } -> { "a":"a", "b":{"a":"ba","b":"bb"} }

		If a dictionary contains only numeric indexes, it will be converted to a list:
			{ "a.0.a":"a0a", "a.0.b":"a0b",a.1.a":"a1a" } -> { "a":[{"a":"a0a","b":"a0b"},{"a":"a1a"}] }

	"""

	res = {}
	processedPrefixes = [] #Dont process a prefix twice

	for k,v in src.items():
		if prefix and not k.startswith( prefix ):
			continue

		if prefix:
			k = k.replace(prefix,"")

		if not "." in k:
			if k in res.keys():
				if not isinstance( res[k], list ):
					res[k] = [ res[k] ]
				res[k].append( v )
			else:
				res[ k ] = v

		else:
			newPrefix = k[ :k.find(".")  ]

			if newPrefix in processedPrefixes: #We did this already
				continue

			processedPrefixes.append( newPrefix )

			if newPrefix in res.keys():
				if not isinstance( res[ newPrefix ], list ):
					res[ newPrefix ] = [ res[ newPrefix ] ]
				res[ newPrefix ].append( parseHashParameters( src, prefix="%s%s." %(prefix,newPrefix)) )

			else:
				res[ newPrefix ] = parseHashParameters( src, prefix="%s%s." %(prefix,newPrefix))

	if all( [x.isdigit() for x in res.keys()]):
		newRes = []
		keys = [int(x) for x in res.keys()]
		keys.sort()

		for k in keys:
			newRes.append( res[str(k)] )

		return newRes

	return res

class EditWidget(html5.Div):
	appList = "list"
	appHierarchy = "hierarchy"
	appTree = "tree"
	appSingleton = "singleton"
	__editIdx_ = 0 #Internal counter to ensure unique ids

	def __init__(self, module, applicationType, key=0, node=None, skelType=None, clone=False,
	                hashArgs=None, context=None, logAction = "Entry saved!", *args, **kwargs):
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
		if not module in conf["modules"].keys():
			conf["mainWindow"].log("error", translate("The module '{{module}}' does not exist.", module=module),modul=self.module,key=self.key,action=self.mode,data=data)
			assert module in conf["modules"].keys()

		super(EditWidget, self ).__init__(*args, **kwargs)
		self.module = module

		self.addClass("vi-widget vi-widget--edit form-group--validation")


		# A Bunch of santy-checks, as there is a great chance to mess around with this widget
		assert applicationType in [ EditWidget.appList, EditWidget.appHierarchy, EditWidget.appTree, EditWidget.appSingleton ] #Invalid Application-Type?

		if applicationType==EditWidget.appHierarchy or applicationType==EditWidget.appTree:
			assert key is not None or node is not None #Need either an id or an node

		if clone:
			assert key is not None #Need an id if we should clone an entry
			assert not applicationType==EditWidget.appSingleton # We cant clone a singleton
			if applicationType==EditWidget.appHierarchy or applicationType==EditWidget.appTree:
				assert node is not None #We still need a rootNode for cloning
			if applicationType==EditWidget.appTree:
				assert node is not None #We still need a path for cloning #FIXME

			self.clone_of = key
		else:
			self.clone_of = None

		# End santy-checks
		self.editIdx = EditWidget.__editIdx_ #Internal counter to ensure unique ids
		EditWidget.__editIdx_ += 1
		self.applicationType = applicationType
		self.key = key
		self.mode = "edit" if self.key or applicationType == EditWidget.appSingleton else "add"
		print("apptype %r" % applicationType)
		print("appSingleton??? %r" % applicationType == EditWidget.appSingleton)
		self.modified = False
		self.node = node
		self.skelType = skelType
		self.clone = clone
		self.bones = {}
		self.closeOnSuccess = False
		self.logAction = logAction
		self.sinkEvent("onChange")

		self.context = context
		self.views = {}

		self._lastData = {} #Dict of structure and values received

		if hashArgs:
			self._hashArgs = parseHashParameters(hashArgs)
		else:
			self._hashArgs = None

		self.editTaskID = None
		self.wasInitialRequest = True #Wherever the last request attempted to save data or just fetched the form

		# Action bar
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
			self.actionbar.setActions(["save.continue","save.close" ] + editActions, widget=self)

		# Set path
		if applicationType == EditWidget.appSingleton:
			conf["theApp"].setPath(module + "/" + self.mode)
		elif self.mode == "edit":
			conf["theApp"].setPath(module + "/" + (self.mode if not clone else "clone") + "/" + self.key)
		else:
			conf["theApp"].setPath(module + "/" + self.mode)

		# Input form
		self.accordion = Accordion()
		self.appendChild(self.accordion)

		# Engage
		self.reloadData()

	def onDetach(self):
		utils.setPreventUnloading(False)
		super(EditWidget, self).onDetach()

	def onAttach(self):
		super(EditWidget, self).onAttach()
		utils.setPreventUnloading(True)

	def performLogics(self):
		return  # fixme: Logics temporarily disabled

		fields = self.serializeForDocument()

		for key, desc in self.dataCache["structure"]:
			if desc.get("params") and desc["params"]:
				for event in ["logic.visibleIf", "logic.readonlyIf", "logic.evaluate"]: #add more here!
					logic = desc["params"].get(event)

					if not logic:
						continue

					# Compile logic at first run
					if isinstance(logic, str):
						desc["params"][event] = conf["logics"].compile(logic)
						if desc["params"][event] is None:
							alert("ViUR logics: Parse error in >%s<" % logic)
							continue

						logic = desc["params"][event]

					res = conf["logics"].execute(logic, fields)

					if event == "logic.evaluate":
						self.bones[key].unserialize({key: res})
					elif res:
						if event == "logic.visibleIf":
							self.containers[key].show()
						elif event == "logic.readonlyIf":
							self.containers[key].disable()

						# add more here...
					else:
						if event == "logic.visibleIf":
							self.containers[key].hide()
						elif event == "logic.readonlyIf":
							self.containers[key].enable()
						# add more here...

	def onChange(self, event):
		self.modified = True
		DeferredCall(self.performLogics)

	def onBoneChange(self, bone):
		self.modified = True
		DeferredCall(self.performLogics)

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displays an error message
		"""
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An error occurred: {{code}}", code=code or 0)

		conf["mainWindow"].log("error", txt)

		if self.wasInitialRequest:
			conf["mainWindow"].removeWidget(self)

	def reloadData(self):
		self.save({})

	def save(self, data):
		"""
			Creates the actual NetworkService request used to transmit our data.
			If data is None, it fetches a clean add/edit form.

			:param data: The values to transmit or None to fetch a new, clean add/edit form.
			:type data: dict or None
		"""
		self.wasInitialRequest = not len(data) > 0

		if self.context:
			# Data takes precedence over context.
			ndata = self.context.copy()
			ndata.update(data.copy())
			data = ndata

		if self.module=="_tasks":
			NetworkService.request(None, "/vi/%s/execute/%s" % (self.module, self.key), data,
			                        secure=not self.wasInitialRequest,
			                        successHandler=self.setData,
			                        failureHandler=self.showErrorMsg)

		elif self.applicationType == EditWidget.appList: ## Application: List
			if self.key and (not self.clone or self.wasInitialRequest):
				NetworkService.request(self.module, "edit/%s" % self.key, data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg)
			else:
				NetworkService.request(self.module, "add", data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg )

		elif False and self.applicationType == EditWidget.appHierarchy: ## Application: Hierarchy
			if self.key and (not self.clone or self.wasInitialRequest):
				NetworkService.request(self.module, "edit/%s" % self.key, data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg)
			else:
				NetworkService.request(self.module, "add/%s" % self.node, data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg)

		elif self.applicationType == EditWidget.appTree or self.applicationType == EditWidget.appHierarchy: ## Application: Tree
			if self.key and not self.clone:
				NetworkService.request(self.module, "edit/%s/%s" % (self.skelType, self.key), data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg)
			else:
				NetworkService.request(self.module, "add/%s/%s" % (self.skelType, self.node), data,
				                       secure=not self.wasInitialRequest,
				                       successHandler=self.setData,
				                       failureHandler=self.showErrorMsg)

		elif self.applicationType == EditWidget.appSingleton: ## Application: Singleton
			NetworkService.request(self.module, "edit", data,
			                       secure=not self.wasInitialRequest,
			                       successHandler=self.setData,
			                       failureHandler=self.showErrorMsg)
		else:
			raise NotImplementedError() #Should never reach this

	def clear(self):
		"""
			Removes all visible bones/forms/fieldsets.
		"""
		self.accordion.removeAllChildren()

	def closeOrContinue(self, sender=None ):
		NetworkService.notifyChange(self.module, key=self.key, action=self.mode)

		if self.closeOnSuccess:
			if self.module == "_tasks":
				self.parent().close()
				return

			if not conf[ "mainWindow" ].navWrapper.removeNavigationPoint(self.parent().view.name):
				conf[ "mainWindow" ].removeWidget(self.parent()) #if no navpoint try to kill popup
			return

		self.clear()
		self.bones = {}

		if self.mode == "add":
			self.key = 0

		self.reloadData()

	def doCloneHierarchy(self, sender=None ):
		if self.applicationType == EditWidget.appHierarchy:
			NetworkService.request( self.module, "clone",
		                            { "fromRepo" : self.node, "toRepo" : self.node,
		                              "fromParent" : self.clone_of, "toParent" : self.key },
		                                secure=True, successHandler=self.cloneComplete )
		else:
			NetworkService.request( conf[ "modules" ][ self.module ][ "rootNodeOf" ], "clone",
		                            { "fromRepo" : self.clone_of, "toRepo" : self.key },
		                                secure=True, successHandler=self.cloneComplete )

	def cloneComplete(self, request):
		conf["mainWindow"].log("success", translate( u"The hierarchy will be cloned in the background." ))
		self.closeOrContinue()

	def formatReadFromClientErrorSeverity(self, error):

		template = "Severity {severity}: "

	def setData(self, request=None, data=None, ignoreMissing=False, askHierarchyCloning=True):
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

		if "action" in data and (data["action"] == "addSuccess" or data["action"] == "editSuccess"):
			self.modified = False
			try:
				self.key = data["values"]["key"]
			except:
				self.key = None

			conf["mainWindow"].log("success",translate(self.logAction),modul=self.module,key=self.key,action=self.mode,data=data)

			if askHierarchyCloning and self.clone:
				# for lists, which are rootNode entries of hierarchies, ask to clone entire hierarchy
				if self.applicationType == EditWidget.appList and "rootNodeOf" in conf[ "modules" ][ self.module ]:
					Confirm(translate(u"Do you want to clone the entire hierarchy?"),
				                            yesCallback=self.doCloneHierarchy,
				                            noCallback=self.closeOrContinue)
					return
				# for cloning within a hierarchy, ask for cloning all subentries.
				elif self.applicationType == EditWidget.appHierarchy:
					Confirm(translate(u"Do you want to clone all subentries of this item?"),
				                            yesCallback=self.doCloneHierarchy,
				                            noCallback=self.closeOrContinue)
					return

			self.closeOrContinue()
			return

		#Clear the UI
		self.clear()
		self.bones = {}
		self.views = {}
		self.containers = {}
		self.actionbar.resetLoadingState()
		self.dataCache = data



		self.modified = False

		tmpDict = {k: v for k, v in self.dataCache["structure"]}
		segments = {}
		firstCat = None
		currRow = 0
		hasMissing = False
		defaultCat = conf["modules"][self.module].get("visibleName", self.module)
		adminCat = conf["modules"][self.module].get("defaultCategory",None)

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

		self.accordion.clearSegments()

		for key, bone in self.dataCache["structure"]:
			cat = defaultCat #meow!

			if ("params" in bone.keys()
			    and isinstance(bone["params"], dict)
			    and "category" in bone["params"].keys()):
				cat = bone["params"]["category"]

			if cat not in segments:
				segments[cat] = self.accordion.addSegment(cat)

			boneFactory = boneSelector.select(self.module, key, tmpDict)(self.module, key, tmpDict, data.get("errors"))
			containerDiv, descrLbl, widget, hasError = boneFactory.boneWidget() #get bone

			if "setContext" in dir(widget) and callable(widget.setContext):
				widget.setContext(self.context)

			if "changeEvent" in dir(widget):
				widget.changeEvent.register(self)

			segments[ cat ].addWidget( containerDiv )

			if hasError:
				segments[ cat ].addClass( "is-incomplete is-active" )
				hasMissing = True

			currRow += 1
			self.bones[ key ] = widget
			self.containers[ key ] = containerDiv

			# Hide invisible bones or logic-flavored bones with their default desire
			if not bone[ "visible" ] or (bone[ "params" ] and bone[ "params" ].get( "logic.visibleIf" )):
				self.containers[ key ].hide()
			elif bone[ "visible" ] and not firstCat and not adminCat:
				firstCat = segments[ cat ]
			elif adminCat and cat == adminCat:
				firstCat = segments[ cat ]

			# NO elif!
			if bone[ "params" ] and bone[ "params" ].get( "logic.readonlyIf" ):
				self.containers[ key ].disable()

		# Hide all segments where all fields are invisible
		for fs in segments.values():
			fs.checkVisibility()

		# Show default category
		if firstCat:
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

				if vmodule not in segments:
					segments[vmodule] = self.accordion.addSegment(vmodule, vtitle or vdescr.get("name", vmodule),directAdd=True)
					segments[vmodule].addClass("editview")

				if vclass:
					segments[vmodule].addClass(*vclass)

				if vvariable:
					context = self.context.copy() if self.context else {}
					context[vvariable] = data["values"]["key"]
				else:
					context = self.context

				self.views[vmodule] = ListWidget(vmodule, filter=vfilter or vdescr.get("filter", {}),
				                                    columns = vcolumns or vdescr.get("columns"),
				                                    context = context)
				segments[vmodule].addWidget(self.views[vmodule])

		self.unserialize(data["values"], data.get("errors"))

		if self._hashArgs: #Apply the default values (if any)
			self.unserialize(self._hashArgs)
			self._hashArgs = None

		self._lastData = data

		if hasMissing and not self.wasInitialRequest:
			conf["mainWindow"].log("warning",translate("Could not save entry!"),icon="icon-cancel",modul=self.module,key=self.key,action=self.mode,data=data)

		DeferredCall(self.performLogics)

	def unserialize(self, data = None, errors=()):
		"""
			Applies the actual data to the bones.
		"""
		for key, bone in self.bones.items():
			if "setContext" in dir(bone) and callable(bone.setContext):
				bone.setContext(self.context)

			if data is not None:
				bone.unserialize(data.get(key))

	def serializeForPost(self, validityCheck = False): #fixme consolidate this with serializeForDocument() to just serialize()
		res = {}

		for key, bone in self.bones.items():
			# ignore the key, it is stored in self.key, and read-only bones
			if key == "key" or bone.bone.readonly:
				continue

			try:
				res[key] = bone.serialize()
				if res[key] is None or res[key] == []:
					res[key] = ""

			except InvalidBoneValueException:
				if validityCheck:
					# Fixme: Bad hack..
					lbl = bone.parent()._children[0]
					if "is-valid" in lbl["class"]:
						lbl.removeClass("is-valid")
					lbl.addClass("is-invalid")
					self.actionbar.resetLoadingState()
					return None

		return res

	def serializeForDocument(self):
		res = self._lastData.get("values", {})

		for key, bone in self.bones.items():
			try:
				res[key] = bone.serialize()
			except InvalidBoneValueException as e:
				res[key] = str(e)

		return res

	def doSave( self, closeOnSuccess=False, *args, **kwargs ):
		"""
			Starts serializing and transmitting our values to the server.
		"""
		self.closeOnSuccess = closeOnSuccess

		res = self.serializeForPost(True)
		if res is None:
			return None

		self.save(res)

