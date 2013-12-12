import html5
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from widgets.file import Uploader


class FileSelectUploader( html5.Input ):
	"""
		Small wrapper around <input type="file">.
		Creates the element; executes the click (=opens the file dialog);
		runs the callback if a file has been selected and removes itself from its parent.

	"""
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
	"""
		Allows uploading of files using the file dialog.
	"""
	def __init__(self, *args, **kwargs):
		super( AddLeafAction, self ).__init__( "Add", *args, **kwargs )
		self["class"] = "icon upload"

	@staticmethod
	def isSuitableFor( modul, handler, actionName ):
		return( handler == "tree.simple.file" and actionName=="add.leaf" )

	def onClick(self, sender=None):
		self.parent().parent().appendChild( FileSelectUploader() )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 3, AddLeafAction.isSuitableFor, AddLeafAction )

