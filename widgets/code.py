from vi import html5
from vi.config import conf
from js import CodeMirror, URL, window
from vi.i18n import translate
from vi.network import DeferredCall,NetworkService
#from pyodide import to_js #todo 0.17
from vi.utils import createWorker
from vi.framework.components.icon import Icon
from vi.framework.components.button import Button
from js import document
from vi.framework.components.tree import Tree, TreeNode

class CodeHelpPopup( html5.ext.Popup ):
	def __init__( self, title="Code Hilfe" ):
		super( CodeHelpPopup, self ).__init__( title = title )
		self[ "class" ].append( "popup--script" )
		self["style"]["width"]="75%"
		self["style"]["height"]="90%"
		self["style"]["max-width"]="75%"
		self.popupBox["style"]["height"] ="100%"
		self.title = title

		exampleCode='''#exampleCode
log.info("info Text")
log.warn("warn Text")
log.error("error Text")

# get an entry
myUser = request("/user/view/self")

# get a simple list of entries
get5Users = request("/user/list/",params={"amount":5}) #default amount = 30, max amount = 99

# iterate over a long lists (more than 99 entries)
userList = requestList("/user/list", maxRequests=2) # max possible entries: maxRequests*amount
while userList.running():
	auser = userList.next() # get one entry or false
	log.info(auser["name"]) # print the mail of a user

#example csv data
csvdata = [["1.1","1.2","1.3"],["2.1","2.2","2.3"],["3.1","3.2","3.3"]]
csvfile = csvWriter()
csvfile.writeRows(csvdata) # write a list of rows to csv file
for item in csvdata:
	csvfile.writeRow(item) # write one row to file

csvfile.download() #trigger download of the file
'''
		self.appendChild(Scripter(exampleCode=exampleCode,executable=False))

class CodePopup( html5.ext.Popup ):
	def __init__( self, title="Editor" ):
		super( CodePopup, self ).__init__( title = title )
		self[ "class" ].append( "popup--script" )
		self["style"]["width"]="75%"
		self["style"]["height"]="90%"
		self["style"]["max-width"]="75%"
		self.popupBox["style"]["height"] = "100%"
		self.title = title
		self.appendChild(Scripter())





class CodeStructurePopup( html5.ext.Popup ):

	def moduleAction(self,wdg,*args,**kwargs):
		if "loaded" not in dir(wdg):
			wdg.loaded = False

		if "moduleName" in kwargs and not wdg.loaded:
			wdg.loaded = True

			if "handler" in kwargs and kwargs["handler"] =="list.grouped" and "group" in kwargs and kwargs["group"]:
				action = f"add/{kwargs['group']}"
			else:
				action = "add"

			loading = html5.Img()
			loading["src"] = "./public/images/is-loading.gif"
			wdg.item.appendChild(loading)

			def copyString(e):
				akey = document.createElement("textarea")
				if "handler" in kwargs and kwargs["handler"] == "list.grouped" and "group" in kwargs and kwargs[
					"group"]:
					akey.value = f'alist = request("/{kwargs["moduleName"]}/list/{kwargs["group"]}", params={{"amount":5}})'
				else:

					akey.value = f'alist = request("/{kwargs["moduleName"]}/list/", params={{"amount":5}})'
				document.body.appendChild(akey)
				akey.select()
				akey.setSelectionRange(0, 99999)
				document.execCommand("copy")

				document.body.removeChild(akey)

			cpybtn = Button("copy", callback=copyString)

			wdg.item.appendChild(cpybtn)

			r = NetworkService.request(kwargs["moduleName"], action,
								   successHandler=self.actionResult)
			r.wdg = wdg
			r.loading = loading
			r.kwargs = kwargs

	def actionResult(self,req):
		wdg = req.wdg
		kwargs = req.kwargs
		answ = NetworkService.decode(req)

		if not answ or not "structure" in answ:
			return

		for bone in answ["structure"]:
			anEntry = html5.Div()
			anEntry["style"]["border-bottom"] = "1xp solid white"

			anameLine = html5.Div()

			amult = False
			if "multiple" in bone[1] and bone[1]["multiple"]:
				amult = " (multiple)"

			aname = html5.Span(bone[0])
			aname["style"]["font-weight"] ="bold"
			anameLine.appendChild(aname)

			aname2 = html5.Span((amult if amult else "") +" ")
			anameLine.appendChild(aname2)
			if bone[1]["type"] == "select":
				aval = html5.Span("( "+", ".join([k for k,v in bone[1]["values"]])+" )")
				aval["style"]["word-break"] = "break-all"
				anameLine.appendChild(aval)
			elif bone[1]["type"].startswith("relational") and "relskel" in bone[1] and bone[1]["relskel"]:
				aval = html5.Span("( " + ", ".join([k[0] for k in bone[1]["relskel"]]) + " )")
				aval["style"]["word-break"] = "break-all"
				anameLine.appendChild(aval)

			anEntry.appendChild(anameLine)


			atype = html5.Div(bone[1]["type"])
			atype["style"]["font-style"] = "italic"
			atype["style"]["font-size"] = "11px"

			anEntry.appendChild(atype)


			wdg.subItem.appendChild(TreeNode(anEntry))
		try:
			wdg.item.removeChild(req.loading)
		except:
			pass


	def __init__( self, title="Strukturinformation" ):
		super( CodeStructurePopup, self ).__init__( title = title )
		moduleStructure = [] #conf["mainConfig"]["configuration"]["moduleGroups"]

		modulChilds = {}

		for m, x in conf["mainConfig"]["modules"].items():
			if "hideInMainBar" in x and x["hideInMainBar"]:
				continue
			x.update({"moduleName":m,"action":self.moduleAction})

			if x["handler"] == "list.grouped" and "views" in x and x["views"]:
				for view in x["views"]:
					view.update({"moduleName": m, "action": self.moduleAction})

				x.update({"children":x["views"]})
				del x["action"]



			if ": " in x["name"]:
				prefixkey = x["name"].split(":")[0]+": "
				if not prefixkey in modulChilds:
					modulChilds.update({prefixkey:[x]})
				else:
					modulChilds[prefixkey].append(x)
			else:
				moduleStructure.append(x)

		for group in conf["mainConfig"]["configuration"]["moduleGroups"]:
			if group["prefix"] in modulChilds:
				group.update({"children":modulChilds[group["prefix"]]})
			if group["children"]:
				moduleStructure.append(group)
		#moduleStructure = sorted(moduleStructure, key=lambda x: x["name"])

		self.loading = html5.Img()
		self.loading["src"] = "./public/images/is-loading.gif"
		self.appendChild(self.loading)
		DeferredCall(self.loadTree,moduleStructure, _delay=1000)

	def loadTree(self,moduleStructure):
		treeWidget = Tree(moduleStructure)
		self.appendChild(treeWidget)

		self.popupBody.removeChild(self.loading)


@html5.tag
class Codemirror(html5.Textarea):

	def __init__(self, syntax="python"):
		super().__init__()

		self.syntax = syntax
		self.value = ""
		self.codemirror = None
		self._element = None

	def _attachCodemirror(self):
		print("_attachCodemirror")

		# todo 0.17
		'''
		self.codemirror = CodeMirror.fromTextArea(
			self.element,
			mode =self.syntax,
			theme = "neo",
			lineNumbers = True,
			lineWrapping = True,
			styleActiveLine= True,
			styleActiveSelected =True,
			matchBrackets= True,
			keyMap = "sublime",
			smartIndent= True,
			indentUnit= 4,
			indentWithTabs= True,
			gutters= to_js(["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"]),
			foldGutter= True,
			autofocus= True,
			autorefresh= True,
			autoCloseBrackets= True
		)
		'''

		self.codemirror = CodeMirror.fromTextArea(
			self.element, {
				"mode":self.syntax,
				"theme":"neo",
				"lineNumbers":True,
				"lineWrapping":True,
				"styleActiveLine":True,
				"styleActiveSelected":True,
				"matchBrackets":True,
				"keyMap":"sublime",
				"smartIndent":True,
				"indentUnit":4,
				"indentWithTabs":True,
				"gutters":["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"],
				"foldGutter":True,
				"autofocus":True,
				"autorefresh":True,
				"autoCloseBrackets":True
			}
		)

		#self.codemirror.refresh()
		self._element = self.element
		self.element = self.codemirror

		self.codemirror.setSize(None, "600px")

		if self.value:
			self.codemirror.setValue(self.value)

	def onAttach(self):
		super().onAttach()

		if self.codemirror:
			return

		self._attachCodemirror()

	def onDetach(self):
		super().onDetach()
		self.value = self["value"]

		if self.codemirror:
			self.codemirror.toTextArea()
			self.codemirror = None

			self.element = self._element
			self._element = None

	def _getValue(self):
		if not self.codemirror:
			return self.value

		return self.codemirror.getValue()

	def _setValue(self, val):
		if not self.codemirror:
			self.value = val
			return

		self.codemirror.setValue(val)
		self.codemirror.clearHistory()

	def insertText(self, text):
		self.codemirror.replaceSelection(text, "around")

	def setCursor(self, line, char):
		self.codemirror.setCursor(line, char)

class PythonCode(html5.Div):
	def __init__(self,logger,scripter):
		super().__init__()
		self.code = Codemirror()
		self.log = []
		self.logger = logger
		self.scripter = scripter
		self.ul = html5.Ul()
		self.logger.appendChild(self.ul)
		self.appendChild(self.code)
		self.worker = None

	def addToLog(self,data,type="normal"):
		"""allowed types:

			normal, info, warn, error
		"""
		if data:
			self.log.append(data)

		liEntry = html5.Li(html5.TextNode(data))
		liEntry.addClass(f'logtype_{type}')
		self.ul.appendChild(liEntry)


	def workerFeedback(self,e):
		# todo 0.17
		'''
		data = e.data.to_py()
		if "error" in data:
			self.addToLog(data["error"])

		if "results" in data:
			self.addToLog(data["results"])

		if "type" in data:
			self.addToLog(data["text"])
		'''

		data = e.data
		if "error" in dir(data):
			self.scripter.loading.hide()
			self.scripter.runbtn.show()
			self.scripter.killbtn.hide()
			self.addToLog(data["error"],"error")

		if "results" in dir(data):
			self.scripter.loading.hide()
			self.scripter.runbtn.show()
			self.scripter.killbtn.hide()
			self.addToLog(data["results"])

		if "type" in dir(data):
			if data["type"] == "download":
				blob = data["blob"]
				filename = data["filename"]

				# create a link click it and at the end remove it
				link = window.document.createElement("a")
				link.href = URL.createObjectURL(blob)
				link.style = "visible:hidden"
				link.download = filename
				window.document.body.appendChild(link)
				link.click()
				window.document.body.removeChild(link)

			else: #logs
				self.addToLog(data["text"],data["type"])

	def run(self):
		self.log = []
		self.ul.removeAllChildren()

		print("RUN: %s"%(self.code["value"]))

		source = "from scripts.webworker_scripts import *\n"+self.code["value"]

		if self.worker:
			self.stop()

		self.worker = createWorker(source, self.workerFeedback, self.workerFeedback)

		self.scripter.runbtn.hide()
		self.scripter.killbtn.show()

	def stop(self):
		self.scripter.loading.hide()
		self.scripter.runbtn.show()
		self.scripter.killbtn.hide()
		if self.worker:
			self.worker.terminate()
			self.worker = None


class Scripter(html5.Div):


	def __init__(self,coder=PythonCode, exampleCode=None ,executable=True):
		super().__init__()
		self["style"]["height"] = "100%"
		self["style"]["background-color" ] = "white"
		#language = HTML
		self.grid = self.fromHTML('''
			<style>
				.logtype_info{color:hsl(210,50%,50%)}
				.logtype_warn{color:hsl(60,50%,50%)}
				.logtype_error{color:hsl(0,50%,50%)}
			</style>

			<div [name]="editor"></div>
			<h2 class="headline" style="margin-top:10px;">Protokoll</h2>
			<div style="border-top:1px solid hsl(0,0%,50%);" [name]="log"></div>
		''')
		self.scriptEditor = coder(self.log,self)
		if not exampleCode:
			exampleCode = '''# Python 3.9 / Pyodide 0.18
log.info("Hello !")
'''

		self.scriptEditor.code.value = exampleCode
		self.editor.appendChild(self.scriptEditor)
		if executable:
			actionbar = html5.Div()
			actionbar["style"]["display"] = "flex"
			actionbar["style"]["gap"] = "5px"
			actionbar["style"]["padding-left"] = "5px"
			self.editor.appendChild(actionbar)

			self.runbtn = Button(translate("run"), icon="icons-play", callback=self.runClick)
			self.runbtn.addClass("btn--add")
			actionbar.appendChild(self.runbtn)

			self.killbtn = Button(translate("abbrechen"), icon="icons-stop", callback=self.killClick)
			self.killbtn.addClass("btn--delete")
			self.killbtn.hide()
			actionbar.appendChild(self.killbtn)

			self.helpbtn = Button(translate("Hilfe"), icon="icons-question", callback=self.openHelp)
			self.helpbtn.addClass("btn--edit")
			actionbar.appendChild(self.helpbtn)

			self.structurebtn = Button(translate("Struktur"), icon="icons-hierarchy", callback=self.openStructure)
			self.helpbtn.addClass("btn--edit")
			actionbar.appendChild(self.structurebtn)

			self.fullscreenbtn = Button(translate("Vollbild"), icon="icons-fullscreen", callback=self.startFullscreen)
			actionbar.appendChild(self.fullscreenbtn)

			self.loading = html5.Img()
			self.loading["src"] = "./public/images/is-loading.gif"
			self.loading["style"]["margin-top"] ="13px"
			self.loading["style"]["height"] ="16px"

			self.loading.hide()
			actionbar.appendChild(self.loading)

	def runClick(self,event):
		self.loading.show()
		self.loading["style"]["display"] = "inline-block"
		self.scriptEditor.run()

	def killClick(self,event):
		self.scriptEditor.stop()

	def openHelp(self, event):
		CodeHelpPopup()

	def openStructure(self,event):
		CodeStructurePopup()

	def startFullscreen(self,event):
		if window.document.fullscreenElement:
			self.fullscreenbtn.setText("Vollbild")
			self.fullscreenbtn.resetIcon()
			window.document.exitFullscreen()
		else:
			self.element.requestFullscreen()
			self.fullscreenbtn.setText("Vollbild verlassen")
			self.fullscreenbtn.setIcon("icons-fullscreen-exit")
