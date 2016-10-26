import html5, utils
from network import NetworkService
from priorityqueue import actionDelegateSelector
from widgets.edit import EditWidget
from config import conf
from pane import Pane
from widgets.repeatdate import RepeatDatePopup
from widgets.csvexport import ExportCsvStarter
from widgets.table import DataTable
from widgets.preview import Preview
from sidebarwidgets.internalpreview import InternalPreview
from sidebarwidgets.filterselector import FilterSelector
from i18n import translate

class EditPane( Pane ):
	pass

"""
	Provides the actions suitable for list applications
"""
class AddAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__(translate("Add"), *args, **kwargs )
		self["class"] = "icon add list"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="add"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-add" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "add" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		pane = EditPane(translate("Add"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget( self.parent().parent().module, EditWidget.appList )
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction( html5.ext.Button ):
	"""
		Allows editing an entry in a list-module.
	"""

	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), *args, **kwargs )
		self["class"] = "icon edit"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(EditAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )
		self.parent().parent().selectionActivatedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		self.parent().parent().selectionActivatedEvent.unregister( self )
		super(EditAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	def onSelectionActivated(self, table, selection ):
		if not self.parent().parent().isSelector and len(selection)==1:
			self.openEditor( selection[0]["key"] )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="edit"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Edit"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appList, key=key)
		pane.addWidget( edwg )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class CloneAction( html5.ext.Button ):
	"""
		Allows cloning an entry in a list-module.
	"""

	def __init__(self, *args, **kwargs):
		super( CloneAction, self ).__init__( translate("Clone"), *args, **kwargs )
		self["class"] = "icon clone"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(CloneAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(CloneAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="clone"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "clone" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Clone"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appList, key=key, clone=True)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, CloneAction.isSuitableFor, CloneAction )



class DeleteAction( html5.ext.Button ):
	"""
		Allows deleting an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( translate("Delete"), *args, **kwargs )
		self["class"] = "icon delete"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(DeleteAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(DeleteAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="delete"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-delete" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "delete" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		d = html5.ext.YesNoDialog(translate("Delete {amt} Entries?",amt=len(selection)) ,title=translate("Delete them?"), yesCallback=self.doDelete, yesLabel=translate("Delete"), noLabel=translate("Keep") )
		d.deleteList = [x["key"] for x in selection]
		d["class"].append( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			NetworkService.request( self.parent().parent().module, "delete", {"key": x}, secure=True, modifies=True )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ListPreviewAction( html5.Span ):
	def __init__(self, *args, **kwargs ):
		super( ListPreviewAction, self ).__init__( *args, **kwargs )
		self.urlCb = html5.Select()
		self.appendChild( self.urlCb )
		btn = html5.ext.Button( translate("Preview"), callback=self.onClick )
		btn["class"] = "icon preview"
		self.appendChild(btn)
		self.urls = None

	def onChange(self, event):
		event.stopPropagation()
		newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value
		self.setUrl( newUrl )

	def rebuildCB(self, *args, **kwargs):
		self.urlCb.element.innerHTML = ""

		if not isinstance(self.urls, dict):
			self.urlCb["style"]["display"] = "none"
			return

		for name,url in self.urls.items():
			o = html5.Option()
			o["value"] = url
			o.appendChild(html5.TextNode(name))
			self.urlCb.appendChild(o)

		if len( self.urls.keys() ) == 1:
			self.urlCb["style"]["display"] = "none"
		else:
			self.urlCb["style"]["display"] = ""

	def onAttach(self):
		super(ListPreviewAction,self).onAttach()
		modul = self.parent().parent().module
		if modul in conf["modules"].keys():
			modulConfig = conf["modules"][modul]
			if "previewurls" in modulConfig.keys() and modulConfig["previewurls"]:
				self.urls = modulConfig["previewurls"]
				self.rebuildCB()


	def onClick(self, sender=None):
		if self.urls is None:
			return
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return

		for entry in selection:
			if isinstance(self.urls, str):
				newUrl = self.urls
			elif len(self.urls.keys()) == 1:
				newUrl = self.urls.values()[0]
			else:
				newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value

			print(newUrl)

			newUrl = newUrl \
						.replace( "{{modul}}", self.parent().parent().module)\
							.replace("{{module}}", self.parent().parent().module)

			for k, v in entry.items():
				newUrl = newUrl.replace("{{%s}}" % k, v)

			newUrl = newUrl.replace("'", "\\'")

			print(newUrl)
			eval("""window.open('"""+newUrl+"""', 'ViPreview');""")
			#widget = Preview( self.urls, selection[0], self.parent().parent().module )
			#conf["mainWindow"].stackWidget( widget )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="preview"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-view" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "view" in conf["modules"][module]["disabledFunctions"]
		isAvailable = False

		if "previewurls" in conf["modules"][module].keys() and conf["modules"][module]["previewurls"]:
			isAvailable = True

		return correctAction and correctHandler and hasAccess and not isDisabled and isAvailable

actionDelegateSelector.insert( 2, ListPreviewAction.isSuitableFor, ListPreviewAction )


class ListPreviewInlineAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( ListPreviewInlineAction, self ).__init__( translate("Preview"), *args, **kwargs )
		self["class"] = "icon preview"
		self["disabled"] = True
		self.urls = None

	def onAttach(self):
		super( ListPreviewInlineAction,self ).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super( ListPreviewInlineAction, self ).onDetach()

	def onSelectionChanged(self, table, selection):
		if self.parent().parent().isSelector:
			return

		# Disable internal Preview by config
		module = self.parent().parent().module
		if conf["modules"][module].get("disableInternalPreview", not conf["internalPreview"]):
			return

		# If there is already something in the sidebar, don't show the internal preview!
		if (self.parent().parent().sideBar.getWidget()
			and not isinstance(self.parent().parent().sideBar.getWidget(), InternalPreview)):
			return

		# Show internal preview when one entry is selected; Else, remove sidebar widget if
		# it refers to an existing, internal preview.
		if len(selection) == 1:
			preview = InternalPreview( self.parent().parent().module, self.parent().parent()._structure, selection[0])
			self.parent().parent().sideBar.setWidget( preview )
		else:
			if isinstance( self.parent().parent().sideBar.getWidget(), InternalPreview ):
				self.parent().parent().sideBar.setWidget( None )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName == "preview"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-view" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "view" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

actionDelegateSelector.insert( 1, ListPreviewInlineAction.isSuitableFor, ListPreviewInlineAction )


class CloseAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( CloseAction, self ).__init__( translate("Close"), *args, **kwargs )
		self["class"] = "icon close"

	def onClick(self, sender=None):
		conf["mainWindow"].removeWidget( self.parent().parent() )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="close"

actionDelegateSelector.insert( 1, CloseAction.isSuitableFor, CloseAction )

class ActivateSelectionAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( ActivateSelectionAction, self ).__init__( translate("Select"), *args, **kwargs )
		self["class"] = "icon activateselection"

	def onClick(self, sender=None):
		self.parent().parent().activateCurrentSelection()

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="select"

actionDelegateSelector.insert( 1, ActivateSelectionAction.isSuitableFor, ActivateSelectionAction )


class SelectFieldsPopup( html5.ext.Popup ):
	def __init__(self, listWdg, *args, **kwargs):
		if not listWdg._structure:
			return

		super( SelectFieldsPopup, self ).__init__( title=translate("Select fields"), *args, **kwargs )

		self["class"].append("selectfields")
		self.listWdg = listWdg
		self.checkboxes = []

		ul = html5.Ul()
		self.appendChild( ul )

		for key, bone in self.listWdg._structure:
			li = html5.Li()
			ul.appendChild( li )

			chkBox = html5.Input()
			chkBox["type"] = "checkbox"
			chkBox["value"] = key

			li.appendChild(chkBox)
			self.checkboxes.append( chkBox )

			if key in self.listWdg.getFields():
				chkBox["checked"] = True
			lbl = html5.Label(bone["descr"],forElem=chkBox)
			li.appendChild(lbl)

		# Functions for Selection
		div = html5.Div()
		div[ "class" ].append( "selectiontools" )

		self.appendChild( div )

		self.selectAllBtn =  html5.ext.Button( translate( "Select all" ), callback=self.doSelectAll )
		self.selectAllBtn[ "class" ].append( "icon" )
		self.selectAllBtn[ "class" ].append( "selectall" )
		self.unselectAllBtn =  html5.ext.Button( translate( "Unselect all" ), callback=self.doUnselectAll )
		self.unselectAllBtn[ "class" ].append( "icon" )
		self.unselectAllBtn[ "class" ].append( "unselectall" )
		self.invertSelectionBtn =  html5.ext.Button( translate( "Invert selection" ), callback=self.doInvertSelection )
		self.invertSelectionBtn[ "class" ].append( "icon" )
		self.invertSelectionBtn[ "class" ].append( "selectinvert" )

		div.appendChild(self.selectAllBtn)
		div.appendChild(self.unselectAllBtn)
		div.appendChild(self.invertSelectionBtn)

		# Function for Commit
		self.cancelBtn = html5.ext.Button( translate( "Cancel" ), callback=self.doCancel)
		self.cancelBtn["class"].append("btn_no")

		self.applyBtn = html5.ext.Button( translate( "Apply" ), callback=self.doApply)
		self.applyBtn["class"].append("btn_yes")

		self.appendChild(self.applyBtn)
		self.appendChild(self.cancelBtn)

	def doApply(self, *args, **kwargs):
		self.applyBtn["class"].append("is_loading")
		self.applyBtn["disabled"] = True

		res = []
		for c in self.checkboxes:
			if c["checked"]:
				res.append( c["value"] )

		self.listWdg.setFields( res )
		self.close()

	def doCancel(self, *args, **kwargs):
		self.close()

	def doSelectAll(self, *args, **kwargs):
		for cb in self.checkboxes:
			if cb[ "checked" ] == False:
				cb[ "checked" ] = True

	def doUnselectAll(self, *args, **kwargs):
		for cb in self.checkboxes:
			if cb[ "checked" ] == True:
				cb[ "checked" ] = False

	def doInvertSelection(self, *args, **kwargs):
		for cb in self.checkboxes:
			if cb[ "checked" ] == False:
				cb[ "checked" ] = True
			else:
				cb[ "checked" ] = False

class SelectFieldsAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( SelectFieldsAction, self ).__init__( translate("Select fields"), *args, **kwargs )
		self["class"] = "icon selectfields"
		self["disabled"] = self.isDisabled = True

	def onClick(self, sender=None):
		SelectFieldsPopup( self.parent().parent() )

	def onAttach(self):
		super(SelectFieldsAction,self).onAttach()
		self.parent().parent().tableChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().tableChangedEvent.unregister( self )
		super(SelectFieldsAction,self).onDetach()

	def onTableChanged(self, table, count):
		if count > 0:
			self["disabled"] = self.isDisabled = False
		elif not self.isDisabled:
			self["disabled"] = self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="selectfields"

actionDelegateSelector.insert( 1, SelectFieldsAction.isSuitableFor, SelectFieldsAction )

class ReloadAction( html5.ext.Button ):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), *args, **kwargs )
		self["class"] = "icon reload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if "is_loading" in self["class"]:
			self["class"].remove("is_loading")


actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class ListSelectFilterAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs ):
		super( ListSelectFilterAction, self ).__init__( translate("Select Filter"), *args, **kwargs )
		self["class"] = "icon selectfilter"
		self.urls = None
		self.filterSelector = None

	def onAttach(self):
		super(ListSelectFilterAction,self).onAttach()
		modul = self.parent().parent().module
		if self.parent().parent().filterID:
			#Its a predefined search - we wont override this
			self["disabled"] = True
		if modul in conf["modules"].keys():
			modulConfig = conf["modules"][modul]
			if "disabledFunctions" in modulConfig.keys() and modulConfig[ "disabledFunctions" ] and "fulltext-search" in modulConfig[ "disabledFunctions" ]:
				# Fulltext-Search is disabled
				if not "views" in modulConfig.keys() or not modulConfig["views"]:
					#And we dont have any views to display
					self["disabled"] = True

	def onClick(self, sender=None):
		if isinstance(self.parent().parent().sideBar.getWidget(), FilterSelector):
			self.parent().parent().sideBar.setWidget(None)
			self.filterSelector = None
		else:
			self.filterSelector = FilterSelector(self.parent().parent().module)
			self.parent().parent().sideBar.setWidget(self.filterSelector)

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="selectfilter"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-view" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "view" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

actionDelegateSelector.insert( 1, ListSelectFilterAction.isSuitableFor, ListSelectFilterAction )

class RecurrentDateAction( html5.ext.Button ):
	"""
		Allows editing an entry in a list-module.
	"""

	def __init__(self, *args, **kwargs):
		super( RecurrentDateAction, self ).__init__( translate("Recurrent Events"), *args, **kwargs )
		self["class"] = "icon createrecurrent_small"
		self["disabled"]= True
		self.isDisabled=True

	def onAttach(self):
		super(RecurrentDateAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(RecurrentDateAction,self).onDetach()

	def onSelectionChanged(self, table, selection ):
		if len(selection)>0:
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"]= False
		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="repeatdate"
		correctHandler = handler == "list.calendar" or handler.startswith("list.calendar.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-edit" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "edit" in conf["modules"][module]["disabledFunctions"]

		return correctAction and correctHandler and hasAccess and not isDisabled

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return
		for s in selection:
			self.openEditor( s["key"] )

	def openEditor(self, key):
		pane = Pane(translate("Recurrent Events"), closeable=True, iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = RepeatDatePopup(self.parent().parent().module, key=key)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, RecurrentDateAction.isSuitableFor, RecurrentDateAction )

class CreateRecurrentAction( html5.ext.Button ):
	def __init__(self, *args, **kwargs):
		super(CreateRecurrentAction, self ).__init__( translate("Save-Close"), *args, **kwargs )
		self["class"] = "icon save close"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="create.recurrent"

	def onClick(self, sender=None):
		self["class"].append("is_loading")
		self.parent().parent().doSave(closeOnSuccess=True)

actionDelegateSelector.insert( 1, CreateRecurrentAction.isSuitableFor, CreateRecurrentAction)

class ExportCsvAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(ExportCsvAction, self).__init__(translate("CSV Export"), *args, **kwargs)
		self["class"] = "icon download"

	def onClick(self, sender = None):
		ExportCsvStarter(self.parent().parent())

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "exportcsv" and (handler == "list" or handler.startswith("list."))

actionDelegateSelector.insert(1, ExportCsvAction.isSuitableFor, ExportCsvAction)

class SelectAllAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(SelectAllAction, self ).__init__(translate("Select all"), *args, **kwargs)
		self["class"] = "icon selectall"
		self["disabled"] = self.isDisabled = True

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "selectall" and (handler == "list" or handler.startswith("list."))

	def onClick(self, sender=None):
		cnt = self.parent().parent().table.table.selectAll()
		conf["mainWindow"].log("info", translate(u"{items} items had been selected", items=cnt))

	def onAttach(self):
		super(SelectAllAction,self).onAttach()
		self.parent().parent().tableChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().tableChangedEvent.unregister( self )
		super(SelectAllAction,self).onDetach()

	def onTableChanged(self, table, count):
		if count > 0:
			self["disabled"] = self.isDisabled = False
		elif not self.isDisabled:
			self["disabled"] = self.isDisabled = True

actionDelegateSelector.insert(1, SelectAllAction.isSuitableFor, SelectAllAction)


class UnSelectAllAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(UnSelectAllAction, self ).__init__(translate("Unselect all"), *args, **kwargs)
		self["class"] = "icon unselectall"
		self["disabled"] = self.isDisabled = True

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "unselectall" and (handler == "list" or handler.startswith("list."))

	def onClick(self, sender=None):
		cnt = self.parent().parent().table.table.unSelectAll()
		conf["mainWindow"].log("info", translate(u"{items} items had been unselected", items=cnt))

	def onAttach(self):
		super(UnSelectAllAction,self).onAttach()
		self.parent().parent().tableChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().tableChangedEvent.unregister( self )
		super(UnSelectAllAction,self).onDetach()

	def onTableChanged(self, table, count):
		if count > 0:
			self["disabled"] = self.isDisabled = False
		elif not self.isDisabled:
			self["disabled"] = self.isDisabled = True

actionDelegateSelector.insert(1, UnSelectAllAction.isSuitableFor, UnSelectAllAction)

class SelectInvertAction(html5.ext.Button):
	def __init__(self, *args, **kwargs):
		super(SelectInvertAction, self ).__init__(translate("Invert selection"), *args, **kwargs)
		self["class"] = "icon selectinvert"
		self["disabled"] = self.isDisabled = True

	@staticmethod
	def isSuitableFor(modul, handler, actionName):
		return actionName == "selectinvert" and (handler == "list" or handler.startswith("list."))

	def onClick(self, sender=None):
		(added, removed) = self.parent().parent().table.table.invertSelection()

		if removed and added:
			conf["mainWindow"].log("info", translate(u"{added} items selected, {removed} items deselected",
			                                            added=added, removed=removed))
		elif removed == 0:
			conf["mainWindow"].log("info", translate(u"{items} items had been selected", items=added))
		elif added == 0:
			conf["mainWindow"].log("info", translate(u"{items} items had been unselected", items=removed))

	def onAttach(self):
		super(SelectInvertAction,self).onAttach()
		self.parent().parent().tableChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().tableChangedEvent.unregister( self )
		super(SelectInvertAction,self).onDetach()

	def onTableChanged(self, table, count):
		if count > 0:
			self["disabled"] = self.isDisabled = False
		elif not self.isDisabled:
			self["disabled"] = self.isDisabled = True

actionDelegateSelector.insert(1, SelectInvertAction.isSuitableFor, SelectInvertAction)