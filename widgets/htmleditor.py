import html5
import network
from __pyjamas__ import JS
from i18n import translate
from widgets.file import FileWidget
from config import conf


class TextInsertImageAction(html5.ext.Button):
	def __init__(self, summernote=self, boneName="", *args, **kwargs):
		super(TextInsertImageAction, self).__init__(translate("Insert Image"), *args, **kwargs)
		self["class"] = "icon text image viur-insert-image-btn"
		self["title"] = translate("Insert Image")
		self["style"]["display"] = "none"
		self.element.setAttribute("data-bonename", boneName)
		self.summernote = summernote

	def onClick(self, sender=None):
		currentSelector = FileWidget("file", selectMode="multi")
		currentSelector.selectionActivatedEvent.register(self)
		conf["mainWindow"].stackWidget(currentSelector)

	def onSelectionActivated(self, selectWdg, selection):
		print("onSelectionActivated")

		if not selection:
			return

		print(selection)

		for item in selection:
			encodeURI = eval("encodeURI")

			if "mimetype" in item.data.keys() and item.data["mimetype"].startswith("image/"):
				if item.data["servingurl"]:
					dataUrl = item.data["servingurl"] + "=s1200"
				else:
					dataUrl = "/file/download/%s/%s" % (item.data["dlkey"], encodeURI(item.data["name"]))

				self.summernote.summernote("editor.insertImage", dataUrl, item.data["name"].replace("\"", ""))
				print("insert img %s" % dataUrl)
			else:
				dataUrl = "/file/download/%s/%s" % (item.data["dlkey"], encodeURI(item.data["name"]))

				text = str(self.summernote.summernote("createRange")) # selected text
				if not text:
					text = item.data["name"].replace("\"", "")

				self.summernote.summernote("editor.createLink",
										   JS("{url: @{{dataUrl}}, text: @{{text}}, isNewWindow: true}"))
				print("insert link %s<%s> " % (text, dataUrl))

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return (actionName == "text.image")

	def resetLoadingState(self):
		pass


class HtmlEditor(html5.Textarea):
	initSources = False

	def __init__(self, *args, **kwargs):
		super(HtmlEditor, self).__init__(*args, **kwargs)

		self.value = ""
		self.summernote = None
		self.enabled = True
		self.summernoteContainer = self
		self.boneName = ""

		self._attachSources()

	def _attachSources(self):
		if not HtmlEditor.initSources:
			print("initialize HTML Editor libraries")

			js = html5.Script()
			js["src"] = "htmleditor/htmleditor.min.js"
			html5.Head().appendChild(js)

			css = html5.Link()
			css["rel"] = "stylesheet"
			css["href"] = "htmleditor/htmleditor.min.css"
			html5.Head().appendChild(css)

		HtmlEditor.initSources = True

	def _attachSummernote(self, retry=0):
		elem = self.summernoteContainer.element
		lang = conf["currentlanguage"]

		try:
			self.summernote = html5.window.top.summernoteEditor(elem, lang)
		except:
			if retry >= 3:
				alert("Unable to connect summernote, please contact technical support...")
				return

			print("Summernote initialization failed, retry will start in 1sec")
			network.DeferredCall(self._attachSummernote, retry=retry + 1, _delay=1000)
			return

		imagebtn = TextInsertImageAction(summernote=self.summernote, boneName=self.boneName)
		self.parent().appendChild(imagebtn)

		if not self.enabled:
			self.summernote.summernote("disable")

		if self.value:
			self["value"] = self.value

	def onAttach(self):
		super(HtmlEditor, self).onAttach()

		if self.summernote:
			return

		self._attachSummernote()

		self.element.setAttribute("data-bonename", self.boneName)

	def onDetach(self):
		super(HtmlEditor, self).onDetach()
		self.value = self["value"]

		if self.summernote:
			self.summernote.summernote("destroy")
			self.summernote = None

	def onEditorChange(self, e, *args, **kwargs):
		if self.parent():
			e = JS("new Event('keyup')")
			self.parent().element.dispatchEvent(e)

	def _getValue(self):
		if not self.summernote:
			return self.value

		ret = self.summernote.summernote("code")
		return ret

	def _setValue(self, val):
		if not self.summernote:
			self.value = val
			return

		self.summernote.off("summernote.change")
		self.summernote.summernote("reset")  # reset history and content
		self.summernote.summernote("code", val)
		self.summernote.on("summernote.change", self.onEditorChange)

	def enable(self):
		super(HtmlEditor, self).enable()

		self.enabled = True
		self.removeClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("enable")

	def disable(self):
		super(HtmlEditor, self).disable()

		self.enabled = False
		self.addClass("is-disabled")

		if self.summernote:
			self.summernote.summernote("disable")
