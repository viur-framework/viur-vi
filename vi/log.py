# -*- coding: utf-8 -*-
from flare import html5
from flare.icons import SvgIcon
from flare.network import DeferredCall
from flare.i18n import translate
from .config import conf

from datetime import datetime
from vi.priorityqueue import toplevelActionSelector
from flare.button import Button
from vi.pane import Pane
from vi.widgets import table as tablewdgt
from vi.widgets.edit import EditWidget
from .utils import indexeddb
import pyodide


iddbTableName = "vi_log3"
class logEntry(html5.Span):
	'''
	PopOut Elements
	'''
	def __init__(self, logObj=None):
		super(logEntry, self).__init__()
		if isinstance( logObj["msg"], html5.Widget ):
			msg = logObj["msg"]
		else:
			msg = html5.TextNode(html5.unescape(logObj["msg"]))

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
		pane = Pane(translate("Edit"), closeable=True, iconURL="icon-edit",
		            iconClasses=["modul_%s" % self.logObj["modul"], "apptype_list", "action_edit"])
		conf["mainWindow"].stackPane(pane, focus=True)
		edwg = EditWidget(self.logObj["modul"], EditWidget.appList, key=key)
		pane.addWidget(edwg)




class logWidget(html5.Div):
	def __init__(self, logList ):
		super(logWidget, self).__init__()
		self["class"] ="vi-widget vi-widget--log"
		self.logList = logList
		header = html5.Div()
		header["class"] = ["vi-actionbar","bar"]
		self.appendChild(header)

		DeferredCall(self.builDataTable)

	def builDataTable( self ):
		tablehead = [ "Datum", "Status", "Nachricht", "Key" ]  # ,"Daten"
		tablefields = [ "date", "type", "msg", "key" ]  # ,"data"
		table = tablewdgt.SelectTable( indexes = True )
		table.setHeader( tablehead )

		for eidx, entry in enumerate(self.logList):
			for fidx in range(0,len(tablehead)):
				table.prepareCol(eidx,fidx+1)
				currentDatafield = tablefields[fidx]

				if currentDatafield=="msg":

					if isinstance(entry[currentDatafield], html5.Widget):
						table["cell"][eidx][fidx+1] = entry[currentDatafield]
					else:
						table["cell"][eidx][fidx+1] = html5.TextNode(html5.unescape( entry[currentDatafield]))
				elif currentDatafield == "key":
					table["cell"][eidx][fidx + 1] = logA(entry)
				else:
					table["cell"][eidx][fidx+1] = html5.TextNode( entry[ currentDatafield ] )

		self.appendChild(table)



class LogButton(html5.Div):
	def __init__(self):
		super(LogButton,self).__init__()

		self.logsList = []

		self["class"] = ["popout-opener", "popout-anchor", "popout--sw", "input-group-item"]


		self.logbtn = Button(icon="icon-time", className="btn btn--topbar btn--log")
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
		if iddbTableName not in idb.objectStoreNames:
			idb.dbAction( "createStore", iddbTableName, None, { "autoIncrement": True } )
		data = idb.getList(iddbTableName)
		data.addEventListener("dataready", pyodide.create_proxy(self.idbdata))


	def idbdata(self,event):
		logAmount = conf["logAmount"]

		for item in list(event.detail["data"])[:logAmount]:
			item = item.to_py()
			self.log(item["type"],
			         item["msg"],
			         item["icon"],
		             item["modul"],
		             item["action"],
		             item["key"],
		             item["data"],
		             item["date"],
					 onlyLoad=True
		          )
		self.cleanLog()


	def cleanLog( self ):
		idb = conf[ "indexeddb" ]
		data = idb.getListKeys( iddbTableName )
		data.addEventListener( "dataready", pyodide.create_proxy(self.cleanLogAction) )

	def cleanLogAction( self,event ):
		for idx in list(event.detail["data"])[:-conf["logAmount"]-1]:
			conf[ "indexeddb" ].dbAction( "delete", iddbTableName, idx )


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
		'''
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
		'''
		conf[ "mainWindow" ].openNewMainView(
			translate("Log"),  # AnzeigeName
			"icon-debug",  # Icon
			"loghandler",  # viewName
			None,  # Modulename
			"list",  # Action
			data = {"logslist":self.logsList },
			append=True
		)

	def log(self, type, msg, icon=None,modul=None,action=None,key=None,data =None, date=None, onlyLoad=False):
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

		if isinstance(msg,str):
			if not onlyLoad:
				conf["indexeddb"].dbAction("add",iddbTableName, None, logObj)
			self.logsList.insert(0,logObj)

			#self.cleanLog()
		self.renderPopOut()
		if not onlyLoad:
			return self.msgOverlay(logObj)
		return None


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
			msgdescr.appendChild(html5.TextNode(html5.unescape(logObj["msg"])))

		if logObj["icon"]:
			svg = SvgIcon( logObj["icon"], title = logObj["msg"] )
		else:
			svg = SvgIcon( "icon-%s" % logObj["type"], title = logObj[ "msg" ], fallbackIcon="icon-message-news" )

		msgwrap.prependChild(svg)
		self.appendChild(msgwrap)
		if logObj["type"] != "progress":
			DeferredCall(self.removeInfo, msgwrap, _delay=2500)
		return msgwrap

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
		openLink = Button(translate("Open message center"), self.toggleMsgCenter)
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
			svg = SvgIcon( icon )
		else:
			svg = SvgIcon( "icon-%s" % type, fallbackIcon="icon-message-news" )

		if svg:
			msgWrap.prependChild(svg)

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
			msgDescr.appendChild(html5.TextNode(html5.unescape(msg)))
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
