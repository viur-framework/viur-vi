# fixme: This module is onlky used in login.py and should be superseeded by Flare already.

# -*- coding: utf-8 -*-
from flare import html5
from flare.network import DeferredCall
from collections import defaultdict

from vi.config import conf
from vi.exception import InvalidBoneValueException
from flare.viur import BoneSelector
from vi.widgets.accordion import Accordion
from vi.widgets.tooltip import ToolTip

from js import console

from typing import List, Tuple
from flare.viur.bones.base import ReadFromClientErrorSeverity

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

def checkErrors(bone) -> Tuple[bool, List[str]]:
	errors = bone["errors"]
	if not errors:
		return False, list()
	invalidatedFields = list()
	for error in errors:
		if (
				(error["severity"] == ReadFromClientErrorSeverity.Empty and bone["required"]) or
				(error["severity"] == ReadFromClientErrorSeverity.InvalidatesOther)
		):
			if error["invalidatedFields"]:
				invalidatedFields.extend(error["invalidatedFields"])
	return True, invalidatedFields


class InternalEdit(html5.Div):

	def __init__(self, skelStructure, values=None, errorInformation=None, readOnly=False,
	                        context=None, defaultCat="", module = None,boneparams = None, errorQueue=None, prefix=None):
		console.log("InternalEdit: %r, %r, %r, %r, %r, %r, %r, %r, %r", skelStructure, values, errorInformation, readOnly, context, defaultCat, boneparams, errorQueue, prefix)
		super(InternalEdit, self).__init__()

		self.errorQueue = errorQueue
		self.addClass("vi-internaledit")
		self.sinkEvent("onChange", "onKeyDown")
		self.prefix = prefix
		self.editIdx = 1
		self.skelStructure = skelStructure
		self.values = values
		self.errorInformation = errorInformation
		self.defaultCat = defaultCat
		self.context = context
		self.module = module
		self.boneparams = boneparams

		self.accordion = None

		self.renderStructure(readOnly=readOnly)

		if values:
			self.unserialize(values)

	def renderStructure(self, readOnly = False):
		self.bones = {}
		self.containers = {}

		tmpDict = {k: v for k, v in self.skelStructure}
		segments = {}
		currRow = 0

		defaultCat = self.defaultCat
		firstCat = None

		errors = defaultdict(list)

		if self.errorInformation:
			for error in self.errorInformation:
				if error["fieldPath"].startswith(self.prefix):  # just filter errors for our InternalEdit, since errors are prefixed for rel bones
					console.log("found a prefixed bone error for us: %r, %r", error, error["fieldPath"].replace(self.prefix, ""))
					errors[error["fieldPath"].replace(self.prefix, "")].append(error)

		for key, bone in self.skelStructure:

			#Enforcing readOnly mode
			if readOnly:
				tmpDict[key]["readonly"] = True

			cat = defaultCat

			if ("params" in bone.keys()
			    and isinstance(bone["params"],dict)
			    and "category" in bone["params"].keys()):
				cat = bone["params"]["category"]

			if cat is not None and not cat in segments.keys():
				if self.accordion is None:
					self.accordion = Accordion()
					self.appendChild(self.accordion)

				segments[cat] = self.accordion.addSegment(cat, directAdd=True)

				if not firstCat:
					firstCat = segments[cat]

			boneFactory = BoneSelector.select(self.module, key, tmpDict)(self.module, key, tmpDict, errors, self.errorQueue)
			widget = boneFactory.editWidget()
			widget["id"] = "vi_%s_%s_%s_%s_bn_%s" % (self.editIdx, None, "internal", cat or "empty", key)

			descrLbl = html5.Label(bone["descr"])
			descrLbl.addClass("label", "flr-label", "flr-label--%s" % bone["type"].replace(".","-"), "flr-label--%s" % key)
			descrLbl["for"] = "vi_%s_%s_%s_%s_bn_%s" % ( self.editIdx, None, "internal", cat or "empty", key)

			if bone["required"]:
				descrLbl["class"].append("is-required")

			bone["errors"] = errors.get(key)
			fieldErrors = html5.fromHTML("""<div class="vi-bone-widget-item"></div>""")[0]
			errorsFound, invalidatedFields = checkErrors(bone)

			if errorsFound:
				descrLbl["class"].append("is-invalid")
				if isinstance(bone["errors"], dict):
					fieldErrors.appendChild(ParsedErrorItem(bone["errors"]))
				elif isinstance(bone["errors"], list):
					for error in bone["errors"]:
						fieldErrors.appendChild(ParsedErrorItem(error))
				console.log("invalidatedFields", invalidatedFields)
				for i in invalidatedFields:
					container = self.containers.get(i)
					if container:
						otherLabel = container.children()[0]
						otherLabel.removeClass("is-valid")
						otherLabel.addClass("is-invalid")
						container.children()[1].children()[1].appendChild(PassiveErrorItem(error))
					else:
						self.errorQueue[i].append(error)

				if segments and cat in segments:
					segments[cat]["class"].append("is-incomplete")

			if bone["required"] and "error" in bone and not (bone["error"] is not None or (self.errorInformation and key in self.errorInformation.keys())):
				descrLbl["class"].append("is-valid")

			if "params" in bone.keys() and isinstance(bone["params"], dict) and "tooltip" in bone["params"].keys():
				tmp = html5.Span()
				tmp.appendChild(descrLbl)
				tmp.appendChild( ToolTip(longText=bone["params"]["tooltip"]) )
				descrLbl = tmp

			self.containers[key] = html5.Div()
			self.containers[key].appendChild(descrLbl)
			self.containers[key].appendChild(widget)
			self.containers[key].appendChild(fieldErrors)
			self.containers[key].addClass("vi-bone", "vi-bone--%s" % bone["type"].replace(".","-"), "vi-bone--%s" % key)

			if "." in bone["type"]:
				for t in bone["type"].split("."):
					self.containers[key].addClass(t)


			if cat is not None:
				segments[cat].addWidget(self.containers[key])
			else:
				self.appendChild(self.containers[key])

			currRow += 1
			self.bones[key] = widget

			#Hide invisible bones
			if not bone["visible"]:
				self.containers[key].hide()

		for myKey, myErrors in self.errorQueue.items():
			container = self.containers.get(myKey)
			if container:
				otherLabel = container.children()[0]
				otherLabel.removeClass("is-valid")
				otherLabel.addClass("is-invalid")
				for myError in myErrors:
					container.children()[1].children()[1].appendChild(PassiveErrorItem(myError))


		if self.boneparams and "vi.style.rel.categories" in self.boneparams and self.boneparams["vi.style.rel.categories"] == "collapsed":pass
		else:
			if firstCat:
				firstCat.activate()

	def serializeForPost(self, validityCheck = False): #fixme consolidate this with serializeForDocument() to just serialize()
		res = {}

		for key, bone in self.bones.items():
			try:
				res[key] = bone.serialize()

			except InvalidBoneValueException:
				if validityCheck:
					# Fixme: Bad hack..
					lbl = bone.parent()._children[0]
					if "is-valid" in lbl["class"]:
						lbl["class"].remove("is-valid")
					lbl["class"].append("is-invalid")
					self.actionbar.resetLoadingState()
					return None

		return res

	def serializeForDocument(self):
		res = {}

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
		return self.serializeForPost(True)

	def unserialize(self, data = None):
		"""
			Applies the actual data to the bones.
		"""
		for key, bone in self.bones.items():
			if "setContext" in dir(bone) and callable(bone.setContext):
				bone.setContext(self.context)

			if data is not None:
				bone.unserialize(data.get(key))

		DeferredCall(self.performLogics)

	def onChange(self, event):
		DeferredCall(self.performLogics)

	def onKeyDown(self, event):
		event.stopPropagation()

	def performLogics(self):
		return  # fixme: Logics temporarily disabled

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
