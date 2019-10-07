# -*- coding: utf-8 -*-
from vi import html5

from .network import DeferredCall
from .i18n import translate
from .config import conf
from .embedsvg import embedsvg

from datetime import datetime


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
				(name, ".".join([str(x) for x in conf["server.version"]])))
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

	def log(self, type, msg, icon=None ):
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

		msgDate = html5.Span()
		msgDate.appendChild( html5.TextNode( datetime.now().strftime("%d. %b. %Y, %H:%M:%S") ))
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
