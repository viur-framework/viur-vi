import html5
from network import DeferredCall
from datetime import datetime
from i18n import translate
from config import conf

class Log( html5.Div ):
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

			#Try loading the revision and build date
			try:
				from version import builddate, revision

				revspan = html5.Span()
				revspan.appendChild(html5.TextNode("Rev %s" % revision))
				revspan.addClass("revisionspan")

				datespan = html5.Span()
				datespan.appendChild(html5.TextNode("Built %s" % builddate))
				datespan.addClass("datespan")

				versionDiv.appendChild(revspan)
				versionDiv.appendChild(datespan)

			except:
				pass

		if versionDiv.children():
			self.appendChild(versionDiv)

	def toggleMsgCenter(self, *args, **kwargs):
		if "is-open" in self["class"]:
			self.removeClass("is-open")
		else:
			self.addClass("is-open")

	def log(self, type, msg ):
		"""
			Adds a message to the log
			@param type: The type of the message.
			@type type: "success", "error", "warning", "info", "progress"
			@param msg: The message to append
			@type msg: String
		"""
		assert type in ["success", "error", "warning", "info", "progress"]

		liwrap = html5.Li()
		liwrap.addClass("log-"+type)
		liwrap.addClass("is-new")

		spanDate = html5.Span()
		spanDate.appendChild( html5.TextNode( datetime.now().strftime("%H:%M:%S") ))
		spanDate.addClass("date")
		liwrap.appendChild(spanDate)

		if isinstance( msg, html5.Widget ):
			#Append that widget directly
			liwrap.appendChild( msg )

		else:
			#Create a span element for that message
			spanMsg = html5.Span()
			spanMsg.appendChild(html5.TextNode(html5.utils.unescape(msg)))
			spanMsg.addClass("msg")
			liwrap.appendChild(spanMsg)

		DeferredCall(self.removeNewCls, liwrap,_delay=2500)
		self.logUL.appendChild( liwrap )

		if len(self.logUL._children)>1:
			self.logUL.element.removeChild( liwrap.element )
			self.logUL.element.insertBefore( liwrap.element, self.logUL.element.children.item(0) )

	def removeNewCls(self,span):
		span.removeClass("is-new")

	def reset(self):
		self.logUL.removeAllChildren()
