# -*- coding: utf-8 -*-
import html5, utils

from html5.ext import YesNoDialog

from network import NetworkService, DeferredCall
from config import conf
from priorityqueue import editBoneSelector
from widgets.tooltip import ToolTip
from widgets.actionbar import ActionBar
from i18n import translate

from widgets.list import ListWidget

class InvalidBoneValueException(ValueError):
	pass

class InternalEdit(html5.Div):

	def __init__(self, skelStructure, values=None, errorInformation=None, readOnly=False, context=None, defaultCat="",
	                    module = None):
		super(InternalEdit, self).__init__()

		self.sinkEvent("onChange", "onKeyDown")

		self.editIdx = 1
		self.skelStructure = skelStructure
		self.values = values
		self.errorInformation = errorInformation
		self.defaultCat = defaultCat
		self.context = context
		self.module = module

		self.form = self

		self.renderStructure(readOnly=readOnly)
		self.unserialize(values)

	def renderStructure(self, readOnly = False):
		self.bones = {}
		self.containers = {}

		tmpDict = {k: v for k, v in self.skelStructure}
		fieldSets = {}
		currRow = 0

		defaultCat = self.defaultCat
		firstCat = True

		for key, bone in self.skelStructure:

			#Enforcing readOnly mode
			if readOnly:
				tmpDict[key]["readonly"] = True

			cat = defaultCat

			if ("params" in bone.keys()
			    and isinstance(bone["params"],dict)
			    and "category" in bone["params"].keys()):
				cat = bone["params"]["category"]

			if cat is not None and not cat in fieldSets.keys():
				fs = html5.Fieldset()
				fs["class"] = cat

				if firstCat:
					fs["class"].append("active")
					firstCat = False

					if self.form is self:
						self.form = html5.Form()
						self.appendChild(self.form)

				fieldSets[cat] = EditWidgetFieldset(cat)

			wdgGen = editBoneSelector.select(self.module, key, tmpDict)
			widget = wdgGen.fromSkelStructure(self.module, key, tmpDict)
			widget["id"] = "vi_%s_%s_%s_%s_bn_%s" % (self.editIdx, None, "internal", cat or "empty", key)

			descrLbl = html5.Label(bone["descr"])
			descrLbl["class"].append(key)
			descrLbl["class"].append(bone["type"].replace(".","_"))
			descrLbl["for"] = "vi_%s_%s_%s_%s_bn_%s" % ( self.editIdx, None, "internal", cat or "empty", key)

			if bone["required"]:
				descrLbl["class"].append("is_required")

			if (bone["required"]
			    and (bone["error"] is not None
			            or (self.errorInformation and key in self.errorInformation.keys()))):
				descrLbl["class"].append("is_invalid")
				if bone["error"]:
					descrLbl["title"] = bone["error"]
				else:
					descrLbl["title"] = self.errorInformation[ key ]

				if fieldSets and cat in fieldSets:
					fieldSets[cat]["class"].append("is_incomplete")

			if bone["required"] and not (bone["error"] is not None or (self.errorInformation and key in self.errorInformation.keys())):
				descrLbl["class"].append("is_valid")

			if "params" in bone.keys() and isinstance(bone["params"], dict) and "tooltip" in bone["params"].keys():
				tmp = html5.Span()
				tmp.appendChild(descrLbl)
				tmp.appendChild( ToolTip(longText=bone["params"]["tooltip"]) )
				descrLbl = tmp

			self.containers[key] = html5.Div()
			self.containers[key].appendChild(descrLbl)
			self.containers[key].appendChild(widget)
			self.containers[key].addClass("bone", "bone_%s" % key, bone["type"].replace(".","_"))

			if "." in bone["type"]:
				for t in bone["type"].split("."):
					self.containers[key].addClass(t)

			if cat is not None:
				fieldSets[cat]._section.appendChild(self.containers[key])
			else:
				self.form.appendChild(self.containers[key])

			currRow += 1
			self.bones[key] = widget

			#Hide invisible bones
			if not bone["visible"]:
				self.containers[key].hide()

		if len(fieldSets)==1:
			for (k,v) in fieldSets.items():
				if not "active" in v["class"]:
					v["class"].append("active")

		tmpList = [(k,v) for (k,v) in fieldSets.items()]
		tmpList.sort( key=lambda x:x[0])

		for k,v in tmpList:
			self.form.appendChild( v )
			v._section = None

	def serializeForPost(self, validityCheck = False):
		res = {}

		for key, bone in self.bones.items():
			try:
				res.update(bone.serializeForPost())
			except InvalidBoneValueException:
				if validityCheck:
					# Fixme: Bad hack..
					lbl = bone.parent()._children[0]
					if "is_valid" in lbl["class"]:
						lbl["class"].remove("is_valid")
					lbl["class"].append("is_invalid")
					self.actionbar.resetLoadingState()
					return None

		return res

	def serializeForDocument(self):
		res = {}

		for key, bone in self.bones.items():
			try:
				res.update(bone.serializeForDocument())
			except InvalidBoneValueException as e:
				res[key] = str(e)

		return res

	def doSave( self, closeOnSuccess=False, *args, **kwargs ):
		"""
			Starts serializing and transmitting our values to the server.
		"""
		self.closeOnSuccess = closeOnSuccess
		return self.serializeForPost(True)

	def unserialize(self, data = None):
		"""
			Applies the actual data to the bones.
		"""
		for bone in self.bones.values():
			if "setContext" in dir(bone) and callable(bone.setContext):
				bone.setContext(self.context)

			if data is not None:
				bone.unserialize(data)

		DeferredCall(self.performLogics)

	def onChange(self, event):
		DeferredCall(self.performLogics)

	def onKeyDown(self, event):
		event.stopPropagation()

	def performLogics(self):
		fields = self.serializeForDocument()
		#print("InternalEdit.performLogics", fields)

		for key, desc in self.skelStructure:
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

					#print("InternalEdit.performLogics", event, key, res)

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


class EditWidgetFieldset(html5.Fieldset):

	def __init__(self, cat, title = None):
		super(EditWidgetFieldset, self).__init__()
		self.sinkEvent("onClick")

		self.addClass("inactive")
		self["name"] = cat

		legend = html5.Legend()
		self.appendChild(legend)

		a = html5.A()
		a.appendChild(html5.TextNode(title or cat))
		legend.appendChild(a)

		section = html5.Section()
		self.appendChild(section)
		self._section = section

	def checkVisibility(self):
		if all([child.isHidden() for child in self._section.children()]):
			self.hide()
		else:
			self.show()

	def activate(self):
		self.removeClass("inactive")
		self.addClass("active")

	def deactivate(self):
		self.removeClass("active")
		self.addClass("inactive")

	def isActive(self):
		return "inactive" not in self["class"]

	def toggle(self):
		if self.isActive():
			self.deactivate()
		else:
			self.activate()

	def onClick(self, event):
		for child in self.parent().children():
			if html5.utils.doesEventHitWidgetOrChildren(event, child):
				if child is self:
					self.toggle()
				else:
					self.activate()
			else:
				child.deactivate()

class EditWidget(html5.Div):
	appList = "list"
	appHierarchy = "hierarchy"
	appTree = "tree"
	appSingleton = "singleton"
	__editIdx_ = 0 #Internal counter to ensure unique ids

	def __init__(self, module, applicationType, key=0, node=None, skelType=None, clone=False,
	                hashArgs=None, context=None, logaction = "Entry saved!", *args, **kwargs):
		"""
			Initialize a new Edit or Add-Widget for the given module.
			@param module: Name of the module
			@type module: String
			@param applicationType: Defines for what application this Add / Edit should be created. This hides additional complexity introduced by the hierarchy / tree-application
			@type applicationType: Any of EditWidget.appList, EditWidget.appHierarchy, EditWidget.appTree or EditWidget.appSingleton
			@param id: ID of the entry. If none, it will add a new Entry.
			@type id: Number
			@param rootNode: If applicationType==EditWidget.appHierarchy, the new entry will be added under this node, if applicationType==EditWidget,appTree the final node is derived from this and the path-parameter.
			Has no effect if applicationType is not appHierarchy or appTree or if an id have been set.
			@type rootNode: String
			@param path: Specifies the path from the rootNode for new entries in a treeApplication
			@type path: String
			@param clone: If true, it will load the values from the given id, but will save a new entry (i.e. allows "cloning" an existing entry)
			@type clone: Bool
			@param hashArgs: Dictionary of parameters (usually supplied by the window.hash property) which should prefill values.
			@type hashArgs: Dict
		"""
		if not module in conf["modules"].keys():
			conf["mainWindow"].log("error", translate("The module '{module}' does not exist.", module=module))
			assert module in conf["modules"].keys()

		super(EditWidget, self ).__init__(*args, **kwargs)
		self.module = module

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
		self.modified = False
		self.node = node
		self.skelType = skelType
		self.clone = clone
		self.bones = {}
		self.closeOnSuccess = False
		self.logaction = logaction
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
			self.actionbar.setActions(["save.singleton"] + editActions)
		else:
			self.actionbar.setActions(["save.close", "save.continue"] + editActions)

		# Set path
		if applicationType == EditWidget.appSingleton:
			conf["theApp"].setPath(module + "/" + self.mode)
		elif self.mode == "edit":
			conf["theApp"].setPath(module + "/" + (self.mode if not clone else "clone") + "/" + self.key)
		else:
			conf["theApp"].setPath(module + "/" + self.mode)

		# Input form
		self.form = html5.Form()
		self.appendChild(self.form)

		# Engage
		self.reloadData()

	def onDetach(self):
		utils.setPreventUnloading(False)
		super(EditWidget, self).onDetach()

	def onAttach(self):
		super(EditWidget, self).onAttach()
		utils.setPreventUnloading(True)

	def performLogics(self):
		fields = self.serializeForDocument()
		#print("EditWidget.performLogics", fields)

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

					#print("EditWidget.performLogics", event, key, res)

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
		try:
			print(req.result)
			print(NetworkService.decode(req))
		except:
			pass

		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An error occurred: {code}", code=code or 0)

		conf["mainWindow"].log("error", txt)

		if self.wasInitialRequest:
			conf["mainWindow"].removeWidget(self)

	def reloadData(self):
		self.save({})

	def save(self, data):
		"""
			Creates the actual NetworkService request used to transmit our data.
			If data is None, it fetches a clean add/edit form.

			@param data: The values to transmit or None to fetch a new, clean add/edit form.
			@type data: Dict or None
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

		elif self.applicationType == EditWidget.appHierarchy: ## Application: Hierarchy
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

		elif self.applicationType == EditWidget.appTree: ## Application: Tree
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
		for c in self.form._children[ : ]:
			self.form.removeChild( c )

	def closeOrContinue(self, sender=None ):
		NetworkService.notifyChange(self.module, key=self.key, action=self.mode)

		if self.closeOnSuccess:
			if self.module == "_tasks":
				self.parent().close()
				return

			conf["mainWindow"].removeWidget(self)
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
		logDiv = html5.Div()
		logDiv["class"].append("msg")
		spanMsg = html5.Span()
		spanMsg.appendChild( html5.TextNode( translate( u"The hierarchy will be cloned in the background." ) ) )
		spanMsg["class"].append("msgspan")
		logDiv.appendChild(spanMsg)

		conf["mainWindow"].log("success",logDiv)
		self.closeOrContinue()

	def setData(self, request=None, data=None, ignoreMissing=False, askHierarchyCloning=True):
		"""
		Rebuilds the UI according to the skeleton received from server

		@param request: A finished NetworkService request
		@type request: NetworkService
		@type data: dict
		@param data: The data received
		"""
		assert (request or data)

		if request:
			data = NetworkService.decode(request)

		if "action" in data and (data["action"] == "addSuccess" or data["action"] == "editSuccess"):
			self.modified = False

			logDiv = html5.Div()
			logDiv["class"].append("msg")
			spanMsg = html5.Span()

			spanMsg.appendChild( html5.TextNode( translate( self.logaction ) ) )
			spanMsg["class"].append("msgspan")
			logDiv.appendChild(spanMsg)

			if self.module in conf["modules"].keys():
				spanMsg = html5.Span()
				if self.module.startswith( "_" ):
					spanMsg.appendChild( html5.TextNode( self.key ) )
				else:
					spanMsg.appendChild( html5.TextNode( conf["modules"][self.module]["name"] ))
				spanMsg["class"].append("modulespan")
				logDiv.appendChild(spanMsg)

			if "values" in data.keys() and "name" in data["values"].keys():
				spanMsg = html5.Span()

				name = data["values"].get("name") or data["values"].get("key", "")
				if isinstance(name, dict):
					if conf["currentlanguage"] in name.keys():
						name = name[conf["currentlanguage"]]
					else:
						name = name.values()

				if isinstance(name, list):
					name = ", ".join(name)

				spanMsg.appendChild(html5.TextNode(str(html5.utils.unescape(name))))
				spanMsg["class"].append("namespan")
				logDiv.appendChild(spanMsg)

			try:
				self.key = data["values"]["key"]
			except:
				self.key = None

			conf["mainWindow"].log("success",logDiv)

			if askHierarchyCloning and self.clone:
				# for lists, which are rootNode entries of hierarchies, ask to clone entire hierarchy
				if self.applicationType == EditWidget.appList and "rootNodeOf" in conf[ "modules" ][ self.module ]:
					YesNoDialog( translate( u"Do you want to clone the entire hierarchy?" ),
				                    yesCallback=self.doCloneHierarchy, noCallback=self.closeOrContinue )
					return
				# for cloning within a hierarchy, ask for cloning all subentries.
				elif self.applicationType == EditWidget.appHierarchy:
					YesNoDialog( translate( u"Do you want to clone all subentries of this item?" ),
				                    yesCallback=self.doCloneHierarchy, noCallback=self.closeOrContinue )
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

		tmpDict = {k: v for k, v in data["structure"]}
		fieldSets = {}
		firstCat = None
		currRow = 0
		hasMissing = False
		defaultCat = conf["modules"][self.module].get("visibleName", self.module)

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

		for key, bone in data["structure"]:

			cat = defaultCat #meow!

			if ("params" in bone.keys()
			    and isinstance(bone["params"], dict)
			    and "category" in bone["params"].keys()):
				cat = bone["params"]["category"]

			if not cat in fieldSets.keys():
				fieldSets[cat] = EditWidgetFieldset(cat)

			wdgGen = editBoneSelector.select(self.module, key, tmpDict)
			widget = wdgGen.fromSkelStructure(self.module, key, tmpDict)
			widget["id"] = "vi_%s_%s_%s_%s_bn_%s" % (self.editIdx, self.module, self.mode, cat, key)

			if "setContext" in dir(widget) and callable(widget.setContext):
				widget.setContext(self.context)

			if "changeEvent" in dir(widget):
				widget.changeEvent.register(self)

			descrLbl = html5.Label(key if conf["showBoneNames"] else bone.get("descr", key))
			descrLbl["class"].append(key)
			descrLbl["class"].append(bone["type"].replace(".","_"))
			descrLbl["for"] = "vi_%s_%s_%s_%s_bn_%s" % (self.editIdx, self.module, self.mode, cat, key)

			#print(key, bone["required"], bone["error"])
			if bone["required"] or (bone.get("unique") and bone["error"]):
				descrLbl["class"].append("is_required")

				if bone["error"] is not None:
					descrLbl["class"].append("is_invalid")
					descrLbl["title"] = bone["error"]
					fieldSets[ cat ]["class"].append("is_incomplete")
					hasMissing = True
				elif bone["error"] is None and not self.wasInitialRequest:
					descrLbl["class"].append("is_valid")

			if isinstance(bone["error"], dict):
				widget.setExtendedErrorInformation(bone["error"])

			containerDiv = html5.Div()
			containerDiv.appendChild(descrLbl)
			containerDiv.appendChild(widget)

			if ("params" in bone.keys()
			    and isinstance(bone["params"], dict)
			    and "tooltip" in bone["params"].keys()):
				containerDiv.appendChild(ToolTip(longText=bone["params"]["tooltip"]))

			fieldSets[cat]._section.appendChild(containerDiv)
			containerDiv.addClass("bone", "bone_%s" % key, bone["type"].replace(".","_"))

			if "." in bone["type"]:
				for t in bone["type"].split("."):
					containerDiv["class"].append(t)

			currRow += 1
			self.bones[key] = widget
			self.containers[key] = containerDiv

			#Hide invisible bones or logic-flavored bones with their default desire
			if not bone["visible"] or (bone["params"] and bone["params"].get("logic.visibleIf")):
				self.containers[key].hide()
			elif bone["visible"] and not firstCat:
				firstCat = fieldSets[cat]

			# NO elif!
			if bone["params"] and bone["params"].get("logic.readonlyIf"):
				self.containers[key].disable()

		# Hide all fieldSets where all fields are invisible
		for fs in fieldSets.values():
			fs.checkVisibility()

		# Show default category
		if firstCat:
			firstCat.removeClass("inactive")
			firstCat.addClass("active")

		tmpList = [(k,v) for (k,v) in fieldSets.items()]
		tmpList.sort(key=lambda x:x[0])

		for k, v in tmpList:
			self.form.appendChild( v )
			v._section = None

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

				fs = html5.Fieldset()
				fs.addClass("editview", "inactive")

				if vclass:
					fs.addClass(*vclass)

				fieldSets[vmodule] = EditWidgetFieldset(vmodule, vtitle or vdescr.get("name", vmodule))

				if vvariable:
					context = self.context.copy() if self.context else {}
					context[vvariable] = data["values"]["key"]
				else:
					context = self.context

				self.views[vmodule] = ListWidget(vmodule, filter=vfilter or vdescr.get("filter", {}),
				                                    columns = vcolumns or vdescr.get("columns"),
				                                    context = context)
				fs._section.appendChild(self.views[vmodule])
				self.form.appendChild(fs)

		#print(data["values"])
		self.unserialize(data["values"])

		if self._hashArgs: #Apply the default values (if any)
			self.unserialize(self._hashArgs)
			self._hashArgs = None

		self._lastData = data

		if hasMissing and not self.wasInitialRequest:
			conf["mainWindow"].log("warning",translate("Could not save entry!"))

		DeferredCall(self.performLogics)

	def unserialize(self, data = None):
		"""
			Applies the actual data to the bones.
		"""
		for bone in self.bones.values():
			if "setContext" in dir(bone) and callable(bone.setContext):
				bone.setContext(self.context)

			if data is not None:
				bone.unserialize(data)

	def serializeForPost(self, validityCheck = False):
		res = {}

		for key, bone in self.bones.items():
			if key == "key":
				continue #ignore the key, it is stored in self.key!

			try:
				res.update(bone.serializeForPost())
			except InvalidBoneValueException:
				if validityCheck:
					# Fixme: Bad hack..
					lbl = bone.parent()._children[0]
					if "is_valid" in lbl["class"]:
						lbl["class"].remove("is_valid")
					lbl["class"].append("is_invalid")
					self.actionbar.resetLoadingState()
					return None

		return res

	def serializeForDocument(self):
		res = self._lastData.get("values", {})

		for key, bone in self.bones.items():
			try:
				res.update(bone.serializeForDocument())
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

