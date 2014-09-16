import html5

from html5.ext.popup import Popup
from html5.keycodes import isReturn
from event import EventDispatcher
from priorityqueue import editBoneSelector
from i18n import translate
from bones import selectmulti, date
from widgets.actionbar import ActionBar
from network import NetworkService
import utils
from config import conf
from widgets.edit import fieldset_A

class RepeatDatePopup(html5.Div):

	__editIdx_ = 0

	def __init__(self, modul, key):
		super(RepeatDatePopup, self).__init__()
		self.modul = modul
		self.editIdx = RepeatDatePopup.__editIdx_ #Iternal counter to ensure unique ids
		RepeatDatePopup.__editIdx_ += 1
		self.key = key
		self._lastData = {} #Dict of structure and values received
		self.closeOnSuccess = False

		h3 = html5.H3()
		h3["class"].append("modul_%s" % self.modul)
		h3["class"].append("apptype_list")

		h3.appendChild(html5.TextNode(translate("create recurrent dates")))

		self.wasInitialRequest = True
		self.actionbar = ActionBar( self.modul, "list", "repeatdate")
		self.appendChild( self.actionbar )
		self.form = html5.Form()
		self.appendChild(self.form)
		self.actionbar.setActions(["save.close", "save.continue", "reset"])
		self.reloadData()

	def reloadData(self):
		self.save({})
		return

	def save(self, data):
		self.wasInitialRequest = not len(data)>0
		if self.modul=="_tasks":
			return #FIXME!
		else:
			if not data:
				NetworkService.request(self.modul,"view/%s" % self.key, successHandler=self.setData, failureHandler=self.showErrorMsg)
			else:
				NetworkService.request(self.modul, "add", data, secure=len(data)>0, successHandler=self.setData, failureHandler=self.showErrorMsg )

	def setData( self, request=None, data=None, ignoreMissing=False ):
		"""
		Rebuilds the UI according to the skeleton received from server

		@param request: A finished NetworkService request
		@type request: NetworkService
		@type data: dict
		@param data: The data received
		"""
		assert (request or data)
		if request:
			data = NetworkService.decode( request )

		skelStructure = utils.boneListToDict(data["structure"])

		if "action" in data and (data["action"] in ["addSuccess", "editSuccess"]):
			NetworkService.notifyChange(self.modul)
			logDiv = html5.Div()
			logDiv["class"].append("msg")
			spanMsg = html5.Span()
			spanMsg.appendChild( html5.TextNode( translate("Entry saved!") ))
			spanMsg["class"].append("msgspan")
			logDiv.appendChild(spanMsg)
			if self.modul in conf["modules"].keys():
				spanMsg = html5.Span()
				spanMsg.appendChild( html5.TextNode( conf["modules"][self.modul]["name"] ))
				spanMsg["class"].append("modulspan")
				logDiv.appendChild(spanMsg)
			if "values" in data.keys() and "name" in data["values"].keys():
				spanMsg = html5.Span()
				spanMsg.appendChild( html5.TextNode( str(data["values"]["name"]) ))
				spanMsg["class"].append("namespan")
				logDiv.appendChild(spanMsg)
			conf["mainWindow"].log("success",logDiv)
			if self.closeOnSuccess:
				conf["mainWindow"].removeWidget( self )
				return
			self.clear()
			# self.bones = {}
			self.reloadData()
			return

		self.clear()
		self.actionbar.resetLoadingState()
		self.dataCache = data

		fieldSets = {}
		cat = "default"
		fs = html5.Fieldset()
		fs["class"] = cat
		if cat=="default":
			fs["class"].append("active")

		fs["name"] = cat
		legend = html5.Legend()
		fshref = fieldset_A()
		fshref.appendChild(html5.TextNode(cat) )
		legend.appendChild( fshref )
		fs.appendChild(legend)
		section = html5.Section()
		fs.appendChild(section)
		fs._section = section
		fieldSets[ cat ] = fs

		startdateLabel = html5.Label("Termin")
		startdateLabel["class"].append("termin")
		startdateLabel["class"].append("date")
		startdate_id = "vi_%s_%s_edit_bn_%s" % ( self.editIdx, self.modul, "repeatdate")
		startdateLabel["for"] = startdate_id
		startdate = date.DateViewBoneDelegate("termin", "startdate", skelStructure).render(data["values"], "startdate")
		startdate["id"] = startdate_id
		containerDiv = html5.Div()
		containerDiv.appendChild(startdateLabel)
		containerDiv.appendChild(startdate)
		containerDiv["class"].append("bone")
		containerDiv["class"].append("bone_startdate")
		containerDiv["class"].append("date")
		fieldSets[ cat ]._section.appendChild( containerDiv )

		countLabel = html5.Label("Wiederholungen")
		countLabel["class"].append("count")
		countLabel["class"].append("numeric")
		count_id = "vi_%s_%s_edit_bn_%s" % ( self.editIdx, self.modul, "count")
		countLabel["for"] = count_id

		count = html5.Input()
		count["id"] = count_id
		containerDiv2 = html5.Div()
		containerDiv2["class"].append("bone")
		containerDiv2["class"].append("bone_count")
		containerDiv2["class"].append("date")
		containerDiv2.appendChild(countLabel)
		containerDiv2.appendChild(count)
		fieldSets[ cat ]._section.appendChild(containerDiv2)
		for (k,v) in fieldSets.items():
			if not "active" in v["class"]:
				v["class"].append("active")
		tmpList = [(k,v) for (k,v) in fieldSets.items()]
		tmpList.sort( key=lambda x:x[0])
		for k,v in tmpList:
			self.form.appendChild( v )
			v._section = None

	def clear(self):
		"""
			Removes all visible bones/forms/fieldsets.
		"""
		for c in self.form._children[ : ]:
			self.form.removeChild( c )

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionbar["style"]["display"] = "none"
		self.form["style"]["display"] = "none"
		errorDiv = html5.Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = translate("Access denied!")
		else:
			txt = translate("An unknown error occurred!")
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild( html5.TextNode( txt ) )
		self.appendChild( errorDiv )

	def doSave( self, closeOnSuccess=False, *args, **kwargs ):
		print("args", args)
		print("kwargs", kwargs)
		self.closeOnSuccess = closeOnSuccess
		# r = rrule.rrule(2, dtstart=datetime(2014, 7,1, 18,00), count=7)
		self.save()
