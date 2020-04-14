# -*- coding: utf-8 -*-
from vi import html5

from .network import DeferredCall
from .i18n import translate
from .config import conf
from vi.embedsvg import embedsvg

from datetime import datetime
from vi.priorityqueue import toplevelActionSelector
from vi.framework.components.button import Button
from vi.pane import Pane
from vi.widgets import table as tablewdgt
from vi.widgets.edit import EditWidget
from .utils import indexeddb

class logEntry(html5.Span):
	'''
	PopOut Elements
	'''
	def __init__(self, logObj=None):
		super(logEntry, self).__init__()
		if isinstance( logObj["msg"], html5.Widget ):
			msg = logObj["msg"]
		else:
			msg = html5.TextNode(html5.utils.unescape(logObj["msg"]))

		self.appendChild(msg)

class logA(html5.A):
	'''
	click handler for loglist
	'''

	def __init__(self, logObj=None):
		super(logA, self).__init__()
		if "key" in logObj:
			self.logObj = logObj
			self.sinkEvent("onClick")
			self.appendChild(html5.TextNode(logObj["key"]))


	def onClick(self,sender=None):
		self.openEditor(self.logObj["key"])

	def openEditor(self, key):
		pane = Pane(translate("Edit"), closeable=True, iconURL="icons-edit",
		            iconClasses=["modul_%s" % self.logObj["modul"], "apptype_list", "action_edit"])
		conf["mainWindow"].stackPane(pane, focus=True)
		edwg = EditWidget(self.logObj["modul"], EditWidget.appList, key=key)
		pane.addWidget(edwg)




class logWidget(html5.Div):
	def __init__(self, logList ):
		super(logWidget, self).__init__()
		self["class"] ="vi-widget"

		header = html5.Div()
		header["class"] = ["vi-actionbar","bar"]
		self.appendChild(header)

		tablehead = ["Datum","Status","Nachricht","Key"] #,"Daten"
		tablefields = ["date","type","msg","key"] #,"data"
		table = tablewdgt.SelectTable(indexes=True)
		table.setHeader(tablehead)

		for eidx, entry in enumerate(logList):
			for fidx in range(0,len(tablehead)):
				table.prepareCol(eidx,fidx+1)
				currentDatafield = tablefields[fidx]
				print(currentDatafield)
				print(entry)
				if currentDatafield=="msg":

					if isinstance(entry[currentDatafield], html5.Widget):
						table["cell"][eidx][fidx+1] = entry[currentDatafield]
					else:
						table["cell"][eidx][fidx+1] = html5.TextNode(html5.utils.unescape( entry[currentDatafield]))
				elif currentDatafield == "key":
					table["cell"][eidx][fidx + 1] = logA(entry)
				else:
					table["cell"][eidx][fidx+1] = html5.TextNode( entry[ currentDatafield ] )

		self.appendChild(table)



class LogButton(html5.Div):
	def __init__(self):
		super(LogButton,self).__init__()

		self.logsList = []

		self["class"] = ["popout-opener", "popout-anchor", "popout--sw"]


		self.logbtn = Button(icon="icons-time", className="btn btn--topbar btn--log")
		self.appendChild(self.logbtn)

		popout = html5.Div()
		popout["class"] = ["popout"]
		self.popoutlist = html5.Div()
		self.popoutlist["class"] = ["list"]

		popout.appendChild(self.popoutlist)
		self.appendChild(popout)
		self.sinkEvent("onClick")

		aitem = html5.Div()
		aitem["class"] = ["item", "has-hover", "item--small item--info"]
		listentry = logEntry({"msg":translate("Das Log ist Leer")})
		aitem.appendChild(listentry)
		self.popoutlist.appendChild(aitem)

		#load old logs from idb
		idb = conf["indexeddb"]
		if "vi_log" not in idb.objectStoreNames:
			idb.dbAction( "createStore", "vi_log", None, { "autoIncrement": True } )
		data = idb.getList("vi_log")
		#data.addEventListener("dataready", self.idbdata)


	def idbdata(self,event):
		print(len(event.detail["data"]))
		for item in event.detail["data"]:
			self.log(item["type"],
			         item["msg"],
			         item["icon"],
		             item["modul"],
		             item["action"],
		             item["key"],
		             item["data"],
		             item["date"]
		          )

	def renderPopOut(self):
		self.popoutlist.removeAllChildren()

		for entry in self.logsList[:10]:
			aitem = html5.Div()
			aitem["class"] = ["item", "has-hover", "item--small", "item--%s"%(entry["type"])]
			listentry = logEntry(entry)
			aitem.appendChild(listentry)
			self.popoutlist.appendChild(aitem)



	def onClick(self,sender=None):
		self.openLog()

	def openLog(self):
		apane = Pane(
			translate("Log"),
			closeable=True,
			iconClasses=[ "apptype_list"],
			collapseable=True
		)

		wg = logWidget(self.logsList )

		apane.addWidget(wg)



		conf["mainWindow"].addPane(apane)
		conf["mainWindow"].focusPane(apane)

	def log(self, type, msg, icon=None,modul=None,action=None,key=None,data =None, date=None):
		logObj = {"type":type,
		          "msg":msg,
		          "icon":icon,
		          "modul":modul,
		          "action":action,
		          "key":key,
		          "data":data
		          }

		if not date:
			logObj.update({"date":datetime.now().strftime("%d. %b. %Y, %H:%M:%S")})
		else:
			logObj.update({"date":date})

		#conf["indexeddb"].dbAction("createStore", "vi_log",None,{"autoIncrement": True})
		#conf["indexeddb"].dbAction("createStore", "vi_test")
		#conf["indexeddb"].dbAction("createStore", "vi_test2")
		#conf["indexeddb"].dbAction("add", "vi_test", "1", {"test":1})
		#conf["indexeddb"].dbAction("add", "vi_test", "2", {"test": 1})
		#conf["indexeddb"].dbAction("edit", "vi_test", "2", {"test": 1,"test2":1})
		#conf["indexeddb"].dbAction("add", "vi_test", "3", {"test": 1})
		#conf["indexeddb"].dbAction("delete", "vi_test", "1")
		if isinstance(msg,str):
			conf["indexeddb"].dbAction("add","vi_log", None, logObj)
			self.logsList.insert(0,logObj)
		self.renderPopOut()

		self.msgOverlay(logObj)



	def msgOverlay(self,logObj):
		assert logObj["type"] in ["success", "error", "warning", "info", "progress"]


		msgwrap = html5.Div()
		msgwrap["class"] = ["msg","is-active","popup","popup--se","msg--%s"%logObj["type"]]

		msgcontent = html5.Div()
		msgcontent["class"] = ["msg-content"]
		msgwrap.appendChild(msgcontent)

		date = html5.Span()
		date["class"] = ["msg-date"]
		date.appendChild(html5.TextNode(logObj["date"]))
		msgcontent.appendChild(date)

		msgdescr = html5.Div()
		msgdescr["class"]=["msg-descr"]
		msgcontent.appendChild(msgdescr)

		if isinstance( logObj["msg"], html5.Widget ):
			msgdescr.appendChild( logObj["msg"] )
		else:
			msgdescr.appendChild(html5.TextNode(html5.utils.unescape(logObj["msg"])))

		if logObj["icon"]:
			svg = embedsvg.get(logObj["icon"])
		else:
			svg = embedsvg.get("icons-%s" % logObj["type"])

		if not svg:
			svg = embedsvg.get("icons-message-news")

		if svg:
			msgwrap.element.innerHTML = svg + msgwrap.element.innerHTML

		self.appendChild(msgwrap)
		DeferredCall(self.removeInfo, msgwrap, _delay=2500)

	def removeInfo(self,wrap):
		self.removeChild(wrap)

	def reset(self):
		self.popoutlist.removeAllChildren()

	@staticmethod
	def canHandle( action ):
		return action == "log"

toplevelActionSelector.insert( 0, LogButton.canHandle, LogButton )


class Log(html5.Div):
	"""
		Provides the "messaging" center displayed at the bottom of VI
	"""
	def __init__(self):
		super(Log, self).__init__()

		self.addClass("vi-messenger")
		openLink = html5.ext.Button(translate("Open message center"), self.toggleMsgCenter)
		self.appendChild(openLink)


		self.logUL = html5.Ul()
		self.logUL["id"] = "statuslist"
		self.logUL.addClass( "statuslist" )
		self.appendChild( self.logUL )

		versionDiv = html5.Div()
		versionDiv.addClass("versiondiv")

		# Server name and version number
		name = conf["vi.viur"]
		if name:
			versionspan = html5.Span()
			versionspan.appendChild("%s v%s" %
				(name, ".".join([str(x) for x in conf["core.version"]])))
			versionspan.addClass("serverspan")
			versionDiv.appendChild(versionspan)

		# Vi name and version number
		name = conf["vi.name"]
		if name:
			versionspan = html5.Span()
			versionspan.appendChild("%s v%s%s" %
				(name, ".".join([str(x) for x in conf["vi.version"]]),
					conf["vi.version.appendix"]))
			versionspan.addClass("versionspan")

			versionDiv.appendChild(versionspan)

			''' fixme ... VI3.0
			revspan = html5.Span()
			revspan.appendChild(html5.TextNode("Rev %s" % revision))
			revspan.addClass("revisionspan")

			datespan = html5.Span()
			datespan.appendChild(html5.TextNode("Built %s" % builddate))
			datespan.addClass("datespan")

			versionDiv.appendChild(revspan)
			versionDiv.appendChild(datespan)
			'''

		if versionDiv.children():
			self.appendChild(versionDiv)

	def toggleMsgCenter(self, *args, **kwargs):
		if self.hasClass("is-open"):
			self.removeClass("is-open")
		else:
			self.addClass("is-open")

	def log(self, type, msg, icon=None,date=None ):
		"""
			Adds a message to the log
			:param type: The type of the message.
			:type type: "success", "error", "warning", "info", "progress"
			:param msg: The message to append
			:type msg: str
		"""
		assert type in ["success", "error", "warning", "info", "progress"]

		msgWrap = html5.Li()
		msgWrap.addClass("msg--"+type, "msg", "is-active")
		msgWrap.addClass("is-new popup popup--s")

		if icon:
			svg = embedsvg.get(icon)
		else:
			svg = embedsvg.get("icons-%s" % type)

		if not svg:
			svg = embedsvg.get("icons-message-news")

		if svg:
			msgWrap.element.innerHTML = svg + msgWrap.element.innerHTML

		msgContent = html5.Div()
		msgContent.addClass("msg-content")
		msgWrap.appendChild(msgContent)
		if not date:
			adate = datetime.now().strftime("%d. %b. %Y, %H:%M:%S")
		else:
			adate = date
		msgDate = html5.Span()
		msgDate.appendChild( html5.TextNode( adate ))
		msgDate.addClass("msg-date")
		msgContent.appendChild(msgDate)



		if isinstance( msg, html5.Widget ):
			#Append that widget directly
			msgContent.appendChild( msg )

		else:
			#Create a span element for that message
			msgDescr = html5.Span()
			msgDescr.appendChild(html5.TextNode(html5.utils.unescape(msg)))
			msgDescr.addClass("msg-descr")
			msgContent.appendChild(msgDescr)

		DeferredCall(self.removeNewCls, msgWrap,_delay=2500)
		self.logUL.appendChild( msgWrap )

		if len(self.logUL._children)>1:
			self.logUL.element.removeChild( msgWrap.element )
			self.logUL.element.insertBefore( msgWrap.element, self.logUL.element.children.item(0) )

	def removeNewCls(self,span):
		span.removeClass("is-new popup popup--s")

	def reset(self):
		self.logUL.removeAllChildren()
