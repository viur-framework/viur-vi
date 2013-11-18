import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from widgets.file import Uploader


class FileSelectUploader( html5.Input ):
	def __init__(self, *args, **kwargs):
		super( FileSelectUploader, self ).__init__( *args, **kwargs )
		self["type"] = "file"
		self["style"]["display"] = "none"
		self.sinkEvent("onChange")
		self.element.click()

	def onChange(self, event):
		if event.target.files.length>0:
			self.parent().appendChild( Uploader( event.target.files.item(0), self.parent().node ) )
		self.parent().removeChild( self )



class AddLeafAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon upload"

	@staticmethod
	def isSuitableFor( modul, actionName ):
		print(modul, actionName)
		return( modul == "tree.simple.file" and actionName=="add.leaf" )

	def onClick(self, sender=None):
		print("OPEN FILE DIALOG")
		#fdiag = html5.Input()
		#fdiag["type"] = "file"
		#fdiag.element.click()
		self.parent().parent().appendChild( FileSelectUploader() )
		print("DIALOG DONE")
		return
		pane = Pane("Add", closeable=True, iconClasses=["modul_%s" % self.parent().parent().modul, "apptype_tree", "action_add_leaf" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().modul, EditWidget.appTree, node=self.parent().parent().node, skelType="leaf" )
		pane.addWidget( edwg )
		pane.focus()

actionDelegateSelector.insert( 3, AddLeafAction.isSuitableFor, AddLeafAction )

