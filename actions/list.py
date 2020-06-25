# -*- coding: utf-8 -*-
from vi import html5

from vi.network import NetworkService
from vi.priorityqueue import actionDelegateSelector
from vi.widgets.edit import EditWidget
from vi.config import conf
from vi.pane import Pane
from vi.widgets.csvexport import ExportCsvStarter
from vi.sidebarwidgets.internalpreview import InternalPreview
from vi.sidebarwidgets.filterselector import FilterSelector
from vi.i18n import translate
from vi.embedsvg import embedsvg
from vi.framework.components.button import Button
from vi.framework.utils import DeferredCall


class EditPane(Pane):
	pass

"""
	Provides the actions suitable for list applications
"""
class AddAction(Button):
	"""
		Allows adding an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( AddAction, self ).__init__(translate("Add"), icon="icons-add", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--add-list btn--primary"

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
		pane = EditPane(translate("Add"), closeable=True, iconURL="icons-add",
		                iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_add" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appList, context=self.parent().parent().context)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, AddAction.isSuitableFor, AddAction )


class EditAction(Button):
	"""
		Allows editing an entry in a list-module.
	"""

	def __init__(self, *args, **kwargs):
		super( EditAction, self ).__init__( translate("Edit"), icon="icons-edit", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--edit"
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
		if len(selection) == 1:
			self.openEditor(selection[0]["key"])

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
		pane = Pane(translate("Edit"), closeable=True, iconURL="icons-edit", iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane, focus=True )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appList, key=key,
		                    context=self.parent().parent().context)
		pane.addWidget( edwg )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, EditAction.isSuitableFor, EditAction )


class CloneAction(Button):
	"""
		Allows cloning an entry in a list-module.
	"""

	def __init__(self, *args, **kwargs):
		super( CloneAction, self ).__init__( translate("Clone"), icon="icons-clone", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--clone"
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
		pane = Pane(translate("Clone"), closeable=True, iconURL="icons-clone", iconClasses=["modul_%s" % self.parent().parent().module, "apptype_list", "action_edit" ])
		conf["mainWindow"].stackPane( pane )
		edwg = EditWidget(self.parent().parent().module, EditWidget.appList, key=key, clone=True,
		                    context=self.parent().parent().context)
		pane.addWidget( edwg )
		pane.focus()

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, CloneAction.isSuitableFor, CloneAction )



class DeleteAction(Button):
	"""
		Allows deleting an entry in a list-module.
	"""
	def __init__(self, *args, **kwargs):
		super( DeleteAction, self ).__init__( translate("Delete"), icon="icons-delete", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--delete"
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
		d.addClass( "delete" )

	def doDelete(self, dialog):
		deleteList = dialog.deleteList
		for x in deleteList:
			NetworkService.request( self.parent().parent().module, "delete", {"key": x},
									secure=True, modifies=True,
									successHandler = self.deletedSuccess,
									failureHandler = self.deletedFailed )


	def deletedSuccess( self, req=None, code=None ):
		conf["mainWindow"].log("success",translate("Eintrag gelöscht"),modul=self.parent().parent().module,action="delete" )

	def deletedFailed( self, req=None, code=None ):
		conf["mainWindow"].log("error",translate("Eintrag konnte nicht gelöscht werden (status: %s)"%code),modul=self.parent().parent().module,action="delete" )

	def resetLoadingState(self):
		pass

actionDelegateSelector.insert( 1, DeleteAction.isSuitableFor, DeleteAction )

class ListPreviewAction(html5.Span):

	def __init__(self, module, handler, actionName, *args, **kwargs ):
		super(ListPreviewAction, self ).__init__(*args, **kwargs)

		self.urls = conf["defaultPreview"]

		self.addClass("input-group")

		self.urlCb = html5.ignite.Select()
		self.appendChild(self.urlCb)

		btn = Button(translate("Preview"), callback=self.onClick, icon="icons-preview")
		btn["class"] = "bar-item btn btn--small btn--preview"
		self.appendChild(btn)

		self["disabled"] = True
		self.isDisabled = True

	def onChange(self, event):
		event.stopPropagation()
		newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value
		self.setUrl(newUrl)

	def rebuildCB(self, *args, **kwargs):
		self.urlCb.removeAllChildren()

		if isinstance(self.urls, list):
			self.urls = {x: x for x in self.urls}

		if not isinstance(self.urls, dict) or len(self.urls.keys()) == 1:
			self.urlCb.addClass("is-hidden")
			return

		for name, url in self.urls.items():
			o = html5.Option()
			o["value"] = url
			o.appendChild(html5.TextNode(name))
			self.urlCb.appendChild(o)

		self.urlCb.removeClass("is-hidden")

	def onAttach(self):
		super(ListPreviewAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register(self)

		module = self.parent().parent().module
		if module in conf["modules"].keys():
			moduleConfig = conf["modules"][module]

			urls = moduleConfig.get("preview", moduleConfig.get("previewurls"))
			if urls:
				self.urls = urls

		if self.urls:
			self.rebuildCB()

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister(self)
		super(ListPreviewAction, self).onDetach()

	def onSelectionChanged(self, table, selection):
		if len(selection) > 0:
			if self.isDisabled:
				self.isDisabled = False
				self["disabled"] = False

		else:
			if not self.isDisabled:
				self["disabled"]= True
				self.isDisabled = True

	def onClick(self, sender=None):
		if not self.urls:
			return

		selection = self.parent().parent().getCurrentSelection()

		if not selection:
			return

		for entry in selection:
			if isinstance(self.urls, str):
				newUrl = self.urls
			elif len(self.urls.keys()) == 1:
				newUrl = list(self.urls.values())[0]
			else:
				newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value

			newUrl = newUrl \
						.replace( "{{modul}}", self.parent().parent().module)\
							.replace("{{module}}", self.parent().parent().module)

			if "updateParams" in conf and conf[ "updateParams" ]:
				for k, v in conf[ "default_params" ].items():
					newUrl = newUrl.replace( "{{%s}}"%k, v )

			for k, v in entry.items():
				newUrl = newUrl.replace("{{%s}}" % k, str(v))

			newUrl = newUrl.replace("'", "\\'")

			target = "%s-%s" % (self.parent().parent().module, entry.get("key"))
			html5.window.open(newUrl, target)

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName=="preview"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-view" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "view" in conf["modules"][module]["disabledFunctions"]
		isAvailable = conf["modules"][module].get("preview", conf["modules"][module].get("previewurls"))

		return correctAction and correctHandler and hasAccess and not isDisabled and isAvailable

actionDelegateSelector.insert( 2, ListPreviewAction.isSuitableFor, ListPreviewAction )


class ListPreviewInlineAction(Button):
	def __init__(self, *args, **kwargs ):
		super( ListPreviewInlineAction, self ).__init__( translate("vi.sidebar.internalpreview"), icon="icons-list-item", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--intpreview"
		self.urls = None
		self.intPrevActive = False
		self.addClass("is-disabled")

	def onAttach(self):
		super( ListPreviewInlineAction,self ).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super( ListPreviewInlineAction, self ).onDetach()

	def onSelectionChanged(self, table, selection):
		# Disallow internal preview in selector mode
		if self.parent().parent().selectionCallback:
			return

		if len(selection)>0:
			self.removeClass("is-disabled")
		else:
			self.addClass("is-disabled")

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
		self.toggleIntPrev()

	def onClick(self, sender=None):
		intPrevActive = self.intPrevActive
		if intPrevActive:
			self.intPrevActive = False
			self.removeClass("is-active")
		else:
			self.intPrevActive = True
			self.addClass("is-active")
		self.toggleIntPrev()

	def toggleIntPrev(self):
		intPrevActive = self.intPrevActive
		selection = self.parent().parent().getCurrentSelection()
		if len(selection) == 1 and intPrevActive == True :
			preview = InternalPreview( self.parent().parent().module, self.parent().parent()._structure, selection[0])
			self.parent().parent().sideBar.sidebarHeadline.element.innerHTML = translate("vi.sidebar.internalpreview")
			svg = embedsvg.get("icons-list-item")
			if svg:
				self.parent().parent().sideBar.sidebarIcon.element.innerHTML = svg
			self.parent().parent().sideBar.setWidget(preview)
		else:
			if isinstance( self.parent().parent().sideBar.getWidget(), InternalPreview ):
				self.parent().parent().sideBar.setWidget(None)

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		if module is None or module not in conf["modules"].keys():
			return False

		correctAction = actionName == "intpreview"
		correctHandler = handler == "list" or handler.startswith("list.")
		hasAccess = conf["currentUser"] and ("root" in conf["currentUser"]["access"] or module+"-view" in conf["currentUser"]["access"])
		isDisabled = module is not None and "disabledFunctions" in conf["modules"][module].keys() and conf["modules"][module]["disabledFunctions"] and "view" in conf["modules"][module]["disabledFunctions"]
		generallyDisabled = not bool(conf["modules"][module].get("disableInternalPreview", not conf["internalPreview"]))

		return correctAction and correctHandler and hasAccess and not isDisabled and generallyDisabled

actionDelegateSelector.insert( 1, ListPreviewInlineAction.isSuitableFor, ListPreviewInlineAction )


class CloseAction(Button):
	def __init__(self, *args, **kwargs ):
		super(CloseAction, self).__init__(
			translate("Close"),
			icon="icons-cancel",
			*args, **kwargs
		)
		self.addClass("bar-item btn btn--small btn--close")

	def onClick(self, sender=None):
		conf["mainWindow"].removeWidget(self.parent().parent())

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="close"

actionDelegateSelector.insert(1, CloseAction.isSuitableFor, CloseAction)

class SelectAction(Button):
	def __init__(self, *args, **kwargs ):
		super().__init__(
			translate("Select"),
			icon="icons-select-add",
			*args, **kwargs
		)
		self.addClass("bar-item btn btn--small btn--activateselection")

	def onClick(self, sender=None):
		self.parent().parent().selectorReturn()

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="select"

actionDelegateSelector.insert(1, SelectAction.isSuitableFor, SelectAction)


class SelectFieldsPopup( html5.ext.Popup ):
	def __init__(self, listWdg, *args, **kwargs):
		if not listWdg._structure:
			return

		super( SelectFieldsPopup, self ).__init__( title=translate("Select fields"), *args, **kwargs )

		self.removeClass("popup--center")
		self.addClass("popup--n popup--selectfields")
		self.listWdg = listWdg
		self.checkboxes = []

		ul = html5.Ul()
		ul.addClass("option-group")
		self.popupBody.appendChild( ul )

		for key, bone in self.listWdg._structure:
			li = html5.Li()
			li.addClass("check")

			ul.appendChild( li )

			chkBox = html5.Input()
			chkBox.addClass("check-input")
			chkBox["type"] = "checkbox"
			chkBox["value"] = key

			li.appendChild(chkBox)
			self.checkboxes.append( chkBox )

			if key in self.listWdg.getFields():
				chkBox["checked"] = True
			lbl = html5.Label(bone["descr"],forElem=chkBox)
			lbl.addClass("check-label")
			li.appendChild(lbl)

		# Functions for Selection
		div = html5.Div()
		div[ "class" ].append( "selectiontools input-group" )

		self.popupBody.appendChild( div )

		self.selectAllBtn =  Button( translate( "Select all" ), callback=self.doSelectAll )
		self.selectAllBtn[ "class" ].append( "btn--selectall" )
		self.unselectAllBtn =  Button( translate( "Unselect all" ), callback=self.doUnselectAll )
		self.unselectAllBtn[ "class" ].append( "btn--unselectall" )
		self.invertSelectionBtn =  Button( translate( "Invert selection" ), callback=self.doInvertSelection )
		self.invertSelectionBtn[ "class" ].append( "btn--selectinvert" )

		div.appendChild(self.selectAllBtn)
		div.appendChild(self.unselectAllBtn)
		div.appendChild(self.invertSelectionBtn)

		# Function for Commit
		self.cancelBtn = Button( translate( "Cancel" ), callback=self.doCancel)
		self.cancelBtn.addClass("btn btn--danger")

		self.applyBtn = Button( translate( "Apply" ), callback=self.doApply)
		self.applyBtn.addClass("btn btn--primary")

		self.popupFoot.appendChild(self.cancelBtn)
		self.popupFoot.appendChild(self.applyBtn)

	def doApply(self, *args, **kwargs):
		self.applyBtn.addClass("is-loading")
		self.applyBtn["icon"] = "icons-loader"
		self.applyBtn["disabled"] = True

		res = []
		for c in self.checkboxes:
			if c["checked"]:
				res.append( c["value"] )

		if not res:
			html5.ext.Alert(
				translate("You have to select at least on field to continue!")
			)
			return

		self.applyBtn["class"].append("is_loading")
		self.applyBtn["disabled"] = True

		DeferredCall(self.listWdg.setFields, res, _delay=100, _callback=self.doSetFields)
		#self.listWdg.setFields( res )
		#self.applyBtn.resetIcon()
		#self.close()

	def doSetFields( self,*args,**kwargs ):
		self.applyBtn.resetIcon()
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

class SelectFieldsAction(Button):
	def __init__(self, *args, **kwargs ):
		super( SelectFieldsAction, self ).__init__( translate("Select fields"), icon="icons-list", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--selectfields"
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

class ReloadAction(Button):
	"""
		Allows Reloading
	"""
	def __init__(self, *args, **kwargs):
		super( ReloadAction, self ).__init__( translate("Reload"), icon="icons-reload", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--reload"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="reload"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self.addClass("is-loading")
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")


actionDelegateSelector.insert( 1, ReloadAction.isSuitableFor, ReloadAction )


class TableNextPage(Button):

	def __init__(self, *args, **kwargs):
		super(TableNextPage, self).__init__(translate("next Page"), icon="icons-table", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--next"

	def postInit(self,widget=None):
		self.currentModule = self.parent().parent()

	def onClick(self, sender=None):
		self.addClass("is-loading")
		if self.currentModule:
			self.currentModule.setPage(1)

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		correctAction = actionName == "tablenext"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert(1, TableNextPage.isSuitableFor, TableNextPage)

class TablePrevPage(Button):

	def __init__(self, *args, **kwargs):
		super(TablePrevPage, self).__init__(translate("prev Page"), icon="icons-table", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--prev"

	def postInit(self,widget=None):
		self.currentModule = self.parent().parent()

	def onClick(self, sender=None):
		self.addClass("is-loading")
		if self.currentModule:
			self.currentModule.setPage(-1)

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		correctAction = actionName == "tableprev"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

actionDelegateSelector.insert(1, TablePrevPage.isSuitableFor, TablePrevPage)


class TableItems(html5.Div):

	def __init__(self, *args, **kwargs):
		super( TableItems, self ).__init__( )
		self["class"] = "item"

	def postInit(self,widget=None):
		self.currentModule = self.parent().parent()
		if self.currentModule:
			self.currentModule.table.tableChangedEvent.register(self)

	def onTableChanged(self,table, rowCount):
		if "elementSpan" in dir(self):
			self.removeChild(self.elementSpan)

		pages = self.currentModule.loadedPages
		currentpage = self.currentModule.currentPage
		#print(table._model)
		if table._dataProvider:
			#self.elementSpan = html5.Span(html5.TextNode(translate("current Page {cpg}, loaded elements: {amt}, pages: {pg}",amt=rowCount, pg=pages, cpg=currentpage )))
			self.elementSpan = html5.Span(html5.TextNode(
				translate("loaded elements: {amt}, pages: {pg}", amt=len(table._model), pg=pages)))
		else:
			#self.elementSpan = html5.Span(html5.TextNode(translate("current Page {cpg}, all elements loaded: {amt}, pages: {pg}",amt=rowCount, pg=pages, cpg=currentpage)))
			self.elementSpan = html5.Span(html5.TextNode(
				translate("all elements loaded: {amt}, pages: {pg}", amt=len(table._model), pg=pages)))
		self.appendChild(self.elementSpan)

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		correctAction = actionName == "tableitems"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

actionDelegateSelector.insert(1, TableItems.isSuitableFor, TableItems)


class SetPageRowAmountAction(html5.Div):
	"""
		Load a bunch of pages
	"""
	def __init__(self, *args, **kwargs):
		super( SetPageRowAmountAction, self ).__init__( )
		self["class"].append("input-group")

		self.pages = html5.Select()
		self.pages["class"].append("select ignt-select select--small")

		defaultSizes = [5,10,25,50,75,99]
		if not conf["batchSize"] in defaultSizes:
			defaultSizes.insert(0,conf["batchSize"])

		for x in defaultSizes:
			opt = html5.Option(x)
			opt["value"] = x
			self.pages.appendChild(opt)
		self.appendChild(self.pages)

		self.btn = Button( translate( "amount" ), callback = self.onClick )
		self.btn[ "class" ] = "bar-item btn btn--small btn--amount"
		self.appendChild( self.btn )
		self.sinkEvent("onChange")
		self.currentLoadedPages = 0

	def onClick(self, sender=None):
		if sender == self.btn:
			self.setPageAmount()

	def onChange(self,sender=None):
		self.setPageAmount()

	def setPageAmount(self):
		self.addClass("is-loading")
		currentModule = self.parent().parent()

		amount = int(self.pages["options"].item(self.pages["selectedIndex"]).value)
		currentModule.setAmount(amount)
		NetworkService.notifyChange(currentModule.module)


	@staticmethod
	def isSuitableFor(module, handler, actionName):
		correctAction = actionName == "setamount"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, SetPageRowAmountAction.isSuitableFor, SetPageRowAmountAction )

class LoadNextBatchAction(html5.Div):
	"""
		Load a bunch of pages
	"""
	def __init__(self, *args, **kwargs):
		super( LoadNextBatchAction, self ).__init__( )
		self["class"].append("input-group")

		self.pages = html5.Select()
		self.pages["class"].append("select ignt-select select--small")
		for x in [1,5,10]:
			opt = html5.Option(x)
			opt["value"] = x
			self.pages.appendChild(opt)
		self.appendChild(self.pages)

		self.btn = Button( translate( "load next pages" ), callback = self.onClick )
		self.btn[ "class" ] = "bar-item btn btn--small btn--loadnext"
		self.appendChild( self.btn )
		self.sinkEvent("onChange")
		self.currentLoadedPages = 0

	def onClick(self, sender=None):
		if sender == self.btn:
			self.loadnextPages()

	def onChange(self, sender=None):
		self.loadnextPages()

	def loadnextPages(self):
		self.addClass("is-loading")
		currentModule = self.parent().parent()

		if currentModule and currentModule.table._dataProvider:
			amount = int(self.pages["options"].item(self.pages["selectedIndex"]).value)
			currentModule.setPage(amount)
		#	.targetPage=amount-1
		# currentModule.onNextBatchNeeded()
		else:
			self.removeClass("is-loading")


	@staticmethod
	def isSuitableFor(module, handler, actionName):
		correctAction = actionName == "loadnext"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, LoadNextBatchAction.isSuitableFor, LoadNextBatchAction )

class LoadAllAction(Button):
	"""
		Allows Loading all Entries in a list
	"""
	def __init__(self, *args, **kwargs):
		super( LoadAllAction, self ).__init__( translate("Load all"), icon="icons-table", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--loadall"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="loadall"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		self.addClass("is-loading")
		currentModule = self.parent().parent()

		if currentModule:
			currentModule.table._loadOnDisplay = True #mark to force load whole Dataset
			html5.window.setTimeout( self.loadAllRows, 500 )

	def loadAllRows(self):
		NetworkService.notifyChange( self.parent().parent().module )

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")


actionDelegateSelector.insert( 1, LoadAllAction.isSuitableFor, LoadAllAction )


class PageFindAction(html5.Div):
	"""
		Allows Loading all Entries in a list
	"""
	def __init__(self, *args, **kwargs):
		super( PageFindAction, self ).__init__( )
		self["class"].append("input-group")

		self.searchInput = html5.Input()
		self.searchInput["class"].append("input ignt-input input--small")
		self.appendChild(self.searchInput)


		btn = Button( translate( "Find on Page" ), callback = self.onClick, icon = "icons-search" )
		btn[ "class" ] = "bar-item btn btn--small btn--pagefind"
		self.appendChild( btn )
		self.sinkEvent("onKeyPress")

	def onKeyPress( self, event ):
		if html5.isReturn( event ):
			self.onClick()

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		correctAction = actionName=="pagefind"
		correctHandler = handler == "list" or handler.startswith("list.")
		return correctAction and correctHandler

	def onClick(self, sender=None):
		text = self.searchInput._getValue()
		if not text:
			return 0
		self.addClass("is-loading")
		self.startFind()


	def startFind(self):
		strFound = self.findText()

		if not strFound:
			html5.window.getSelection().empty()
			conf["mainWindow"].log("info", "Nothing found!")

	def findText(self):
		subject = self.searchInput["value"]
		if not subject:
			return False

		parent = self.parent().parent().element
		strFound = html5.window.find(subject, 0, 0, 1)
		jsselection = html5.window.getSelection()

		if strFound and jsselection and not jsselection.anchorNode:
			strFound = html5.window.find(subject, 0, 0, 1)

		if parent and strFound:
			selectionElement = html5.window.getSelection().anchorNode.parentElement

			if selectionElement and parent.contains(selectionElement):
				selectionElement.scrollIntoView()
				strFound = True
			else:
				strFound = False

		self.resetLoadingState()
		return strFound

	def resetLoadingState(self):
		if self.hasClass("is-loading"):
			self.removeClass("is-loading")

actionDelegateSelector.insert( 1, PageFindAction.isSuitableFor, PageFindAction )

class ListSelectFilterAction(Button):
	def __init__(self, *args, **kwargs ):
		super( ListSelectFilterAction, self ).__init__( translate("Select Filter"), icon="icons-search", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--selectfilter"
		self.urls = None
		self.filterSelector = None

	def onAttach(self):
		super(ListSelectFilterAction,self).onAttach()
		module = self.parent().parent().module
		if self.parent().parent().filterID:
			#Its a predefined search - we wont override this
			self["disabled"] = True
		if module in conf["modules"].keys():
			modulConfig = conf["modules"][module]
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
			self.parent().parent().sideBar.sidebarHeadline.element.innerHTML = translate("vi.sidebar.filterselector")
			svg = embedsvg.get("icons-search")
			if svg:
				self.parent().parent().sideBar.sidebarIcon.element.innerHTML = svg
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

class CreateRecurrentAction(Button):
	def __init__(self, *args, **kwargs):
		super(CreateRecurrentAction, self ).__init__( translate("Save-Close"), icon="icons-save-file", *args, **kwargs )
		self["class"] = "bar-item btn btn--small btn--primary btn--save-close"

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName=="create.recurrent"

	def onClick(self, sender=None):
		self.addClass("is-loading")
		self.parent().parent().doSave(closeOnSuccess=True)

actionDelegateSelector.insert( 1, CreateRecurrentAction.isSuitableFor, CreateRecurrentAction)

class ExportCsvAction(Button):
	def __init__(self, *args, **kwargs):
		super(ExportCsvAction, self).__init__(translate("CSV Export"), icon="icons-download-file", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--download"

	def onClick(self, sender = None):
		ExportCsvStarter(self.parent().parent())

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "exportcsv" and (handler == "list" or handler.startswith("list."))

actionDelegateSelector.insert(1, ExportCsvAction.isSuitableFor, ExportCsvAction)

class SelectAllAction(Button):
	def __init__(self, *args, **kwargs):
		super(SelectAllAction, self ).__init__(translate("Select all"), icon="icons-select-add", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--selectall"
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


class UnSelectAllAction(Button):
	def __init__(self, *args, **kwargs):
		super(UnSelectAllAction, self ).__init__(translate("Unselect all"), icon="icons-select-remove", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--unselectall"
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

class SelectInvertAction(Button):
	def __init__(self, *args, **kwargs):
		super(SelectInvertAction, self ).__init__(translate("Invert selection"), icon="icons-select-invert", *args, **kwargs)
		self["class"] = "bar-item btn btn--small btn--selectinvert"
		self["disabled"] = self.isDisabled = True

	@staticmethod
	def isSuitableFor(module, handler, actionName):
		return actionName == "selectinvert" and (handler == "list" or handler.startswith("list."))

	def onClick(self, sender=None):
		(added, removed) = self.parent().parent().table.table.invertSelection()

		if removed and added:
			conf["mainWindow"].log("info", translate(u"{added} items selected, {removed} items deselected",
			                                            added=added, removed=removed), icon="icons-select-invert")
		elif removed == 0:
			conf["mainWindow"].log("info", translate(u"{items} items had been selected", items=added), icon="icons-select-add")
		elif added == 0:
			conf["mainWindow"].log("info", translate(u"{items} items had been unselected", items=removed), icon="icons-select-remove")

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
