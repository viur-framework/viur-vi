from flare import html5
from flare.popup import Popup
from vi.config import conf
from js import CodeMirror, URL, window
from flare.i18n import translate
from flare.network import DeferredCall,NetworkService
from pyodide import to_js
from flare.utils import createWorker
from js import document
from flare.button import Button

class CodeHelpPopup( Popup ):
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

class CodePopup( Popup ):
	def __init__( self, title="🐍Editor" ):
		super( CodePopup, self ).__init__( title = title )
		self[ "class" ].append( "popup--script" )
		self["style"]["width"]="75%"
		self["style"]["height"]="90%"
		self["style"]["max-width"]="75%"
		self.popupBox["style"]["height"] = "100%"
		self.title = title
		self.appendChild(Scripter())

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
		data = e.data.to_py()

		if "error" in data:
			self.scripter.loading.hide()
			self.scripter.runbtn.show()
			self.scripter.killbtn.hide()
			self.addToLog(data["error"],"error")

		if "results" in data:
			self.scripter.loading.hide()
			self.scripter.runbtn.show()
			self.scripter.killbtn.hide()
			self.addToLog(data["results"])

		if "type" in data:
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

		self.worker = createWorker(source, self.workerFeedback, self.workerFeedback,context={"scriptPath":"/vi/s/"})

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
log.info("Hello ViUR!")
'''

		self.scriptEditor.code.value = exampleCode
		self.editor.appendChild(self.scriptEditor)
		if executable:
			actionbar = html5.Div()
			actionbar["style"]["display"] = "flex"
			actionbar["style"]["gap"] = "5px"
			actionbar["style"]["padding-left"] = "5px"
			self.editor.appendChild(actionbar)

			self.runbtn = Button(translate("run"), icon="icon-play", callback=self.runClick)
			self.runbtn.addClass("btn--add")
			actionbar.appendChild(self.runbtn)

			self.killbtn = Button(translate("abbrechen"), icon="icon-stop", callback=self.killClick)
			self.killbtn.addClass("btn--delete")
			self.killbtn.hide()
			actionbar.appendChild(self.killbtn)

			self.helpbtn = Button(translate("Hilfe"), icon="icon-question", callback=self.openHelp)
			self.helpbtn.addClass("btn--edit")
			actionbar.appendChild(self.helpbtn)

			self.fullscreenbtn = Button(translate("Vollbild"), callback=self.startFullscreen)
			actionbar.appendChild(self.fullscreenbtn)

			self.loading = html5.Img()
			self.loading["src"] = "./public/images/is-loading32.gif"
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

	def startFullscreen(self,event):
		if window.document.fullscreenElement:
			self.fullscreenbtn._setText("Vollbild")
			window.document.exitFullscreen()
		else:
			self.element.requestFullscreen()
			self.fullscreenbtn._setText("Vollbild verlassen")
