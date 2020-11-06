from flare import html5
from flare.observable import StateHandler
from vi.config import conf

class NavigationElement(html5.Div):
	# language=HTML
	tpl = '''
		<div [name]="item" class="item has-hover">
			<a class="item-link" @click="navigationAction">
				<div class="item-image">
					<icon value="{{icon}}" ></icon>
				</div>

				<div class="item-content">
					<div class="item-headline">{{name}}</div>
				</div>
			</a>
			
			<span [name]="itemArrow" class="item-open is-hidden" @click="ArrowAction">
				<svgicon value="icon-arrow-left"></svgicon>
			</span>
			
		</div>
		<div [name]="subItem" class="list list--sub">
		</div>
		
		
		'''

	def __init__(self,name,icon=None,view=None,nav=None):
		super().__init__()
		self.view = view
		self.nav = nav
		self["class"] = "itemGroup"
		#register state handler
		nav.state.register("activeNavigation",self)

		self.state = StateHandler( ["hasSubItems"],self )
		self.state.register("hasSubItems",self)

		self.appendChild(
			self.tpl,
			icon = icon,
			name = name
		)
		self.state.updateState( "hasSubItems", False )

	def navigationAction( self,e,wdg=None):
		'''
			Handle Click on Navigation Button
		'''
		if self.state.getState("hasSubItems"):
			self.subItem.toggleClass( "is-active" )
			self.itemArrow.toggleClass( "is-active" )
		else:
			#if we have a linked view, update the view State
			if self.view:
				conf["views_state"].updateState("activeView", self.view)

			#if this element is part of a Navigation, update active State
			if self.nav:
				self.nav.state.updateState("activeNavigation",self)

	def ArrowAction( self,e, wdg=None ):
		self.subItem.toggleClass("is-active")
		self.itemArrow.toggleClass("is-active")

	def onActiveNavigationChanged( self,e,wdg ):
		'''
			What should happen if the State from the surrounding Navigation gets an update
		'''
		if wdg == self:
			self.item.addClass("is-active")
		else:
			self.item.removeClass("is-active")

	def onHasSubItemsChanged( self,e,wdg ):
		'''
			If subChild is added, show itemArrow, hide if no subitem present
		'''
		if e:
			self.itemArrow.show()
		else:
			self.itemArrow.hide()

	def appendSubChild( self,element ):
		self.state.updateState("hasSubItems",True)
		self.subItem.appendChild(element)

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
					<svgicon value="icon-arrow-left"></svgicon>
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

	def seperatorAction( self,e, wdg=None ):
		self.seperator.toggleClass("is-active")

class AppNavigation(html5.Nav):

	def __init__(self):
		super().__init__()
		self.state = StateHandler()
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

		if isinstance(parent,NavigationElement):
			parent.appendSubChild(aNav)
		else:
			parent.appendChild(aNav)
		return aNav
