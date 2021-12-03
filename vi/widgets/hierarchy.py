from vi.widgets.tree import TreeWidget
from vi.widgets.list import ListWidget
from vi.config import conf

from vi.priorityqueue import DisplayDelegateSelector, ModuleWidgetSelector


class HierarchyWidget(TreeWidget):
	"""
	A Hierarchy is a Tree without leaf distiction!
	"""
	leafWidget = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.listview = ListWidget(self.module, context=self.context, autoload=False)
		self.listview.actionBar.setActions(["preview", "selectfields"], widget=self)
		self.listwidgetadded = False
		self.listviewActive = False
		self.setListView(self.listviewActive)

	def reloadData(self):
		super(HierarchyWidget, self).reloadData()

		if self.listviewActive and not self.listwidgetadded:
			self.listwidgetadded = True
			conf["mainWindow"].stackWidget(self.listview, disableOtherWidgets=False)

		if self.listviewActive:
			self.reloadListWidget()

	def reloadListWidget(self):
		listfilter = {
			"orderby": "sortindex",
			"skelType": "node"
		}

		if self.selection:
			listfilter.update({"parententry": self.selection[0].data["key"]})
		else:
			listfilter.update({"parententry": self.rootNode})

		self.listview.setFilter(listfilter)

	def toggleListView(self):
		self.setListView(not self.listviewActive)
		if not self.viewNodeStructure:
			self.requestStructure()
		else:
			self.reloadData()

	def setListView(self, visible=False):
		if visible:
			self["style"]["width"] = "50%"
			self.listviewActive = True
			self.showListView()
			return

		self.listviewActive = False
		self.hideListView()
		self["style"]["width"] = "100%"

	def showListView(self):
		self.listview.show()

	def hideListView(self):
		self.listview.hide()

	def onSelectionChanged(self, widget, selection, *args,**kwargs):
		if self.listviewActive:
			if not self.viewNodeStructure:
				self.requestStructure()
			else:
				self.reloadData()

	@staticmethod
	def canHandle(moduleName, moduleInfo):
		return moduleInfo["handler"] == "hierarchy" or moduleInfo["handler"].startswith("hierarchy.")


ModuleWidgetSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget)
DisplayDelegateSelector.insert(1, HierarchyWidget.canHandle, HierarchyWidget)
