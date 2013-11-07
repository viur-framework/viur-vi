import html5
import pyjd # this is dummy in pyjs.
from network import NetworkService
from widgets.actionbar import ActionBar
from event import EventDispatcher


class HierarchyItem( html5.Li ):
	def __init__(self, modul, data, *args, **kwargs ):
		super( HierarchyItem, self ).__init__( *args, **kwargs )
		self.modul = modul
		self.data = data
		self.element.innerHTML = data["name"]
		self.isLoaded = False
		self.isExpanded = False
		self.ol = html5.Ol()
		self.appendChild(self.ol)
		self.ol["style"]["display"] = "none"
		self["class"].append("hierarchyitem")
		self["class"].append("unexpaned")

	def toggleExpand(self):
		if self.isExpanded:
			self.ol["style"]["display"] = "none"
			self["class"].remove("expaned")
			self["class"].append("unexpaned")
		else:
			self.ol["style"]["display"] = "block"
			self["class"].append("expaned")
			self["class"].remove("unexpaned")
		self.isExpanded = not self.isExpanded




class HierarchyWidget( html5.Div ):

	def __init__( self, modul, rootNode=None, node=None, *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super( HierarchyWidget, self ).__init__( )
		print("INIT HierarchyWidget WIDGET")
		self.modul = modul
		self.rootNode = rootNode
		self.node = node or rootNode
		#self.setStyleName("vi_viewer")
		self.actionBar = ActionBar( self, modul )
		self.appendChild( self.actionBar )
		self.entryFrame = html5.Ol()
		self.appendChild( self.entryFrame )
		#self.entryFrame.selectionActivatedEvent.register( self )
		self.entryFrame["style"]["border"] = "1px solid green"
		#DOM.setStyleAttribute(self.entryFrame,"border","1px solid green")
		self._currentCursor = None
		self._currentRequests = []
		if self.rootNode:
			print("INIT TREE WIDGET X!")
			self.reloadData()
		else:
			print("INIT TREE WIDGET X2")
			NetworkService.request(self.modul,"listRootNodes", successHandler=self.onSetDefaultRootNode)
		self.path = []
		self.sinkEvent( "onClick" )
		##Proxy some events and functions of the original table
		#for f in ["selectionChangedEvent","selectionActivatedEvent","cursorMovedEvent","getCurrentSelection"]:
		#	setattr( self, f, getattr(self.table,f))
		#self.actionBar.setActions(["add","edit","delete"])
		#HTTPRequest().asyncGet("/admin/%s/list" % self.modul, self)

	def itemForEvent(self,event, elem=None):
		if elem is None:
			elem = self.entryFrame
		for child in elem._children:
			if child.element==event.target:
				return( child )
			tmp = self.itemForEvent( event, child.ol )
			if tmp is not None:
				return( tmp )
		return( None )

	def itemForKey(self, key, elem=None ):
		if elem is None:
			elem = self.entryFrame
		for child in elem._children:
			if child.data["id"]==key:
				return( child )
			tmp = self.itemForKey( key, child.ol )
			if tmp is not None:
				return( tmp )
		return( None )

	def onClick(self, event):
		item = self.itemForEvent( event )
		if item is None:
			return
		item.toggleExpand()
		if not item.isLoaded:
			item.isLoaded = True
			self.loadNode( item.data["id"] )


	def onSetDefaultRootNode(self, req):
		data = NetworkService.decode( req )
		if len(data)>0:
			self.setRootNode( data[0]["key"])

	def setRootNode(self, rootNode):
		self.rootNode = rootNode
		self.node = rootNode
		self.reloadData()


	def reloadData(self):
		self.loadNode( self.rootNode )

	def loadNode(self, node):
		print("FETCHING PARENT", node)
		r = NetworkService.request(self.modul,"list/", {"parent":node}, successHandler=self.onRequestSucceded )
		r.node = node

	def onRequestSucceded(self, req):
		data = NetworkService.decode( req )
		if req.node==self.rootNode:
			ol = self.entryFrame
		else:
			tmp = self.itemForKey( req.node )
			assert ol is not None
			ol = tmp.ol
		for skel in data["skellist"]:
			ol.appendChild( HierarchyItem( self.modul, skel ) )

