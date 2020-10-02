# -*- coding: utf-8 -*-
from flare import html5


class SideBar( html5.Div ):

	def __init__(self, *args, **kwargs):
		super( SideBar, self ).__init__( *args, **kwargs )
		self.isInit = False
		self.currentWidget = None
		self.addClass("vi-sidebar popup popup--ne popup--local box")

		self.fromHTML("""
			<div class="box-head" [name]="sidebarHead">
				<div class="item" [name]="sidebarHeadItem">
					<div class="item-image">
						<i class="i i--small" [name]="sidebarIcon"></i>
					</div>
					<div class="item-content">
						<div class="item-headline" [name]="sidebarHeadline"></div>
					</div>
				</div>
			</div>
		""")

		closeBtn = Button("&times;", self.close, className="item-action")
		closeBtn.removeClass("btn")
		self.sidebarHeadItem.appendChild(closeBtn)

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
