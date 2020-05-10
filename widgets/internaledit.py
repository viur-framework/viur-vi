# -*- coding: utf-8 -*-
from vi import html5
from vi.network import DeferredCall
from vi.config import conf
from vi.priorityqueue import boneSelector
from vi.exception import InvalidBoneValueException
from vi.widgets.tooltip import ToolTip
from vi.widgets.accordion import Accordion

class InternalEdit(html5.Div):

	def __init__(self, skelStructure, values=None, errorInformation=None, readOnly=False,
	                        context=None, defaultCat="", module = None,boneparams = None):
		super(InternalEdit, self).__init__()

		self.addClass("vi-internaledit")
		self.sinkEvent("onChange", "onKeyDown")

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

			boneFactory = boneSelector.select(self.module, key, tmpDict)(self.module, key, tmpDict)
			widget = boneFactory.editWidget()
			widget["id"] = "vi_%s_%s_%s_%s_bn_%s" % (self.editIdx, None, "internal", cat or "empty", key)

			descrLbl = html5.Label(bone["descr"])
			descrLbl.addClass("label", "vi-label", "vi-label--%s" % bone["type"].replace(".","-"), "vi-label--%s" % key)
			descrLbl["for"] = "vi_%s_%s_%s_%s_bn_%s" % ( self.editIdx, None, "internal", cat or "empty", key)

			if bone["required"]:
				descrLbl["class"].append("is-required")

			if (bone["required"]
			    and (bone["error"] is not None
			            or (self.errorInformation and key in self.errorInformation.keys()))):
				descrLbl["class"].append("is-invalid")
				if bone["error"]:
					descrLbl["title"] = bone["error"]
				else:
					descrLbl["title"] = self.errorInformation[ key ]

				if segments and cat in segments:
					segments[cat]["class"].append("is-incomplete")

			if bone["required"] and not (bone["error"] is not None or (self.errorInformation and key in self.errorInformation.keys())):
				descrLbl["class"].append("is-valid")

			if "params" in bone.keys() and isinstance(bone["params"], dict) and "tooltip" in bone["params"].keys():
				tmp = html5.Span()
				tmp.appendChild(descrLbl)
				tmp.appendChild( ToolTip(longText=bone["params"]["tooltip"]) )
				descrLbl = tmp

			self.containers[key] = html5.Div()
			self.containers[key].appendChild(descrLbl)
			self.containers[key].appendChild(widget)
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

		print(self.boneparams)
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
