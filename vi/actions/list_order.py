# -*- coding: utf-8 -*-
from flare import html5
from flare.button import Button
from flare.popup import Confirm
from flare.network import NetworkService
from vi.priorityqueue import actionDelegateSelector
from vi.config import conf
from flare.i18n import translate

# ShopMarkAction -------------------------------------------------------------------------------------------------------
class ShopMarkAction( Button ):
	def __init__(self, action, title, cls="", txtQuestion=None, txtSuccess=None, txtFailure=None, *args, **kwargs):
		super( ShopMarkAction, self ).__init__( translate( title ))

		#self["class"] = "icon order_markpayed"
		self["disabled"] = True
		self.isDisabled = True

		self.action = action
		self.txtQuestion = txtQuestion
		self.txtSuccess = txtSuccess
		self.txtFailure = txtFailure

		self.done = 0
		self.failed = 0
		self.total = 0

	def onAttach(self):
		super(ShopMarkAction,self).onAttach()
		self.parent().parent().selectionChangedEvent.register( self )

	def onDetach(self):
		self.parent().parent().selectionChangedEvent.unregister( self )
		super(ShopMarkAction,self).onDetach()

	def onSelectionChanged(self, table, selection, *args,**kwargs ):
		if len( selection ):
			if self.isDisabled:
				self.isDisabled = False
			self["disabled"] = False
		else:
			if not self.isDisabled:
				self["disabled"] = True
				self.isDisabled = True

	def setPayed(self, order ):
		NetworkService.request( self.parent().parent().module, self.action,
		                            { "key": order[ "key" ] }, secure=True,
									successHandler=self.setPayedSucceeded,
									failureHandler=self.setPayedFailed )

	def setPayedSucceeded(self, response):
		self.done += 1

		if self.done + self.failed == self.total:
			conf["mainWindow"].log("success", translate( self.txtSuccess, count=self.done ) )
			NetworkService.notifyChange( self.parent().parent().module )

	def setPayedFailed(self, response):
		conf["mainWindow"].log( "error", translate( self.txtFailure ) )
		self.failed += 1

	def doMarkPayed( self, *args, **kwargs ):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return

		self.done = 0
		self.total = len( selection )

		for item in selection:
			self.setPayed( item )

	def onClick(self, sender=None):
		selection = self.parent().parent().getCurrentSelection()
		if not selection:
			return

		Confirm( translate( self.txtQuestion, count=len( selection ) ),
							   title=translate( "Mark payed" ), yesCallback=self.doMarkPayed )

# ShopMarkPayedAction --------------------------------------------------------------------------------------------------

class ShopMarkPayedAction( ShopMarkAction ):
	def __init__(self, *args, **kwargs):
		super( ShopMarkPayedAction, self ).__init__(
			"markPayed", "Mark payed", cls="order_markpayed",
			txtQuestion = "Do you really want to mark {{count}} orders as payed?",
			txtSuccess = "{{count}} orders had been successfully set as payed.",
			txtFailure= "Failed to mark order payed" )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName == "markpayed" and handler == "list.order"

actionDelegateSelector.insert( 1, ShopMarkPayedAction.isSuitableFor, ShopMarkPayedAction )

# ShopMarkSentAction ---------------------------------------------------------------------------------------------------

class ShopMarkSentAction( ShopMarkAction ):
	def __init__(self, *args, **kwargs):
		super( ShopMarkSentAction, self ).__init__(
			"markSend", "Mark sent", cls="order_marksent",
			txtQuestion = "Do you really want to mark {{count}} orders as sent?",
			txtSuccess = "{{count}} orders had been successfully set as sent.",
			txtFailure = "Failed to mark order sent" )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName == "marksent" and handler == "list.order"

actionDelegateSelector.insert( 1, ShopMarkSentAction.isSuitableFor, ShopMarkSentAction )

# ShopMarkCanceledAction -----------------------------------------------------------------------------------------------

class ShopMarkCanceledAction( ShopMarkAction ):
	def __init__(self, *args, **kwargs):
		super( ShopMarkCanceledAction, self ).__init__(
			"markCanceled", "Mark canceled", cls="order_markcanceled",
			txtQuestion = "Do you really want to cancel {{count}} orders?",
			txtSuccess = "{{count}} orders had been successfully canceled.",
			txtFailure = "Failed to cancel order" )

	@staticmethod
	def isSuitableFor( module, handler, actionName ):
		return actionName == "markcanceled" and handler == "list.order"

actionDelegateSelector.insert( 1, ShopMarkCanceledAction.isSuitableFor, ShopMarkCanceledAction )
