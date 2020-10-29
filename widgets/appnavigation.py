from flare import html5
from flare.observable import StateHandler
from vi.config import conf

class NavigationElement(html5.Template):

	def __init__(self,name,icon=None,view=None,nav=None):
		super().__init__()
		self.view = view
		self.nav = nav
		#register state handler
		nav.state.register("activeNavigation",self)

		#language=HTML
		self.appendChild('''
			<div [name]="item" class="item has-hover">
				<a class="item-link" @click="navigationAction">
					<div class="item-image">
						<icon value="{{icon}}" ></icon>
					</div>
	
					<div class="item-content">
						<div class="item-headline">{{name}}</div>
						
					</div>
				</a>
			</div>
			''',
			 icon = icon,
			 name = name
		)

	def navigationAction( self,e,wdg):
		'''
			Handle Click on Navigation Button
		'''
		#if we have a linked view update the view State
		if self.view:
			conf["views_state"].updateState("activeView", self.view)

		#if this element is part of a Navigation update active State
		if self.nav:
			self.nav.state.updateState("activeNavigation",self)

	def onActiveNavigationChanged( self,e,wdg ):
		'''
			What should happen if the State from the surrounding Navigation gets an update
		'''
		if wdg == self:
			self.item.addClass("is-active")
		else:
			self.item.removeClass("is-active")



@html5.tag
class NavigationSeperator(html5.Div):

	def __init__(self, name=None):
		super().__init__()
		self.name = name
		self[ "class" ] = [ "list-separator", "list-separator--accordion", "is-active" ]

		if self.name:
			self.buildSeperator()

	def buildSeperator( self ):
		# language=HTML
		self.appendChild( '''
					<svgicon value="icon-dashboard"></svgicon>
					<span class="list-separator-content">%s</span>
					<svgicon value="icon-arrow-down"></svgicon>
			''' % self.name )

	def _setValue( self,value ):
		self.name = value
		self.buildSeperator()

class Navigationblock(html5.Div):

	def __init__(self, name):
		super().__init__()
		self.name = name
		self.seperator = None
		self[ "class" ] = [ "vi-modulelist", "list" ]

	def addSeperator( self ):
		#language=HTML
		self.appendChild('''
			<navigationseperator [name]="seperator" @click="seperatorAction" value="{{name}}"></navigationseperator>
		''',
		 name=self.name)

	def seperatorAction( self,e, wdg ):
		wdg.toggleClass("is-active")

class AppNavigation(html5.Nav):

	def __init__(self):
		super().__init__()
		self.state = StateHandler( self )
		self.state.updateState( "activeNavigation", None )


	def addNavigationBlock( self, name ):
		aBlock = Navigationblock(name)
		aBlock.addSeperator()
		self.appendChild(aBlock)
		return aBlock

	def addNavigationPoint( self,name,icon,view=None,parent=None ):
		aNav = NavigationElement(name,icon,view,self)
		if not parent:
			parent = self
		parent.appendChild(aNav)
