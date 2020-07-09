# -*- coding: utf-8 -*-
from vi import html5
from vi.framework.components.button import Button
from vi.i18n import translate
class SideBar( html5.Div ):

	def __init__(self, *args, **kwargs):
		super( SideBar, self ).__init__( *args, **kwargs )
		self.isInit = False
		self.currentWidget = None
		self.addClass("vi-sidebar popup popup--ne popup--local box popup-dt-listfilter")

		self.currcords = ["n","e"]

		self.fromHTML("""
			<div class="box-head" [name]="sidebarHead">
				<div class="item input-group" [name]="sidebarHeadItem">
					<div class="item-image">
						<i class="i i--small" [name]="sidebarIcon"></i>
					</div>
					<div class="item-content">
						<div class="item-headline" [name]="sidebarHeadline"></div>
					</div>
				</div>
			</div>
		""")



		moveup = Button(translate("hoch"), self.moveUp, icon="icons-arrow-up", notext = True)
		self.sidebarHeadItem.appendChild(moveup)

		moveup = Button( translate( "runter" ), self.moveDown, icon = "icons-arrow-down", notext = True )
		self.sidebarHeadItem.appendChild( moveup )

		moveup = Button( translate( "links" ), self.moveLeft, icon = "icons-arrow-left", notext = True )
		self.sidebarHeadItem.appendChild( moveup )

		moveup = Button( translate( "rechts" ), self.moveRight, icon = "icons-arrow-right", notext = True )
		self.sidebarHeadItem.appendChild( moveup )

		closeBtn = Button( "&times;", self.close )
		self.sidebarHeadItem.appendChild(closeBtn)

	def moveUp( self,*args,**kwargs ):
		if self.currcords[0]=="s":
			self.currcords[0]="n"
		self.moveSetClass()

	def moveDown( self,*args,**kwargs ):
		if self.currcords[0]=="n":
			self.currcords[0]="s"
		self.moveSetClass()
	def moveLeft( self,*args,**kwargs ):
		if self.currcords[ 1 ] == "e":
			self.currcords[ 1 ] = "w"
		self.moveSetClass()
	def moveRight( self,*args,**kwargs ):
		if self.currcords[ 1 ] == "w":
			self.currcords[ 1 ] = "e"
		self.moveSetClass()

	def moveSetClass( self ):
		self.removeClass( "popup--ne" )
		self.removeClass( "popup--nw" )
		self.removeClass( "popup--sw" )
		self.removeClass( "popup--se" )
		self.addClass("popup--%s%s"%(self.currcords[0],self.currcords[1]))

	def onAttach(self):
		super( SideBar, self ).onAttach()
		self.isInit = True
		if self.currentWidget is not None:
			cw = self.currentWidget
			self.currentWidget = None
			self.setWidget( cw )

	def onDetach(self):
		if self.currentWidget:
			self.removeChild( self.currentWidget )
			self.currentWidget = None
			self.removeClass("is-active")
		super( SideBar, self ).onDetach()
		self.isInit = False

	def setWidget(self, widget):
		if not self.isInit:
			self.currentWidget = widget
			return

		if self.currentWidget:
			self.removeChild( self.currentWidget )
			if widget is None:
				self.removeClass("is-active")

		elif widget is not None:
			self.addClass( "is-active")

		self.currentWidget = widget

		if widget is not None:
			self.appendChild( widget )


	def getWidget(self):
		return( self.currentWidget )

	def close(self, *args, **kwargs):
		if self.currentWidget:
			self.removeChild( self.currentWidget )
			self.currentWidget = None
			self.removeClass("is-active")
