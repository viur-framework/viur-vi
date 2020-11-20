from flare import html5
from flare.observable import StateHandler
from flare.views.helpers import removeView
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
			<span [name]="itemRemove" class="is-hidden" @click="RemoveAction">
				<svgicon value="icon-cross"></svgicon>
			</span>
			
		</div>
		<div [name]="subItem" class="list list--sub">
		</div>
		'''

	def __init__(self,name,icon=None,view=None,nav=None,closeable=False):
		super().__init__()
		self.view = view
		self.nav = nav
		self.closeable = closeable
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

		if self.closeable:
			self.itemRemove.removeClass("is-hidden")


	def navigationAction( self,e=None,wdg=None):
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

	def RemoveAction( self,e=None ):
		'''
		remove this Nav Element
		'''
		#get previous Navigation Point
		previousItem = self.nav.getPreviousNavigationPoint(self.view)

		#remove associated View and switch to previous View
		removeView(self.view, targetView=previousItem.view)

		#remove navpoint
		del self.nav.navigationPoints[self.view]


		print("AAAAA")
		print(previousItem)
		print(previousItem.view)


		self.parent().removeChild( self )
		if self.nav:
			self.nav.state.updateState( "activeNavigation", previousItem )

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
		self.navigationPoints = {}


	def getPreviousNavigationPoint(self, view ):
		aNav = self.navigationPoints[view]
		try:
			idx = aNav.parent()._children.index( aNav ) + 1
			indexOfItem = max( idx, 0 )

			previousItem = aNav.parent()._children[ indexOfItem ]
		except:
			# Point not in Section
			previousItem = self.navigationPoints[list(self.navigationPoints)[-2]] #get last element in the dict

		return previousItem


	def getNavigationPoint( self,view ):
		aNav = self.navigationPoints[ view ]
		return aNav

	def addNavigationBlock( self, name ):
		aBlock = Navigationblock(name)
		aBlock.addSeperator()
		self.appendChild(aBlock)
		return aBlock

	def addNavigationPoint( self,name,icon,view=None,parent=None,closeable=False ):
		aNav = NavigationElement(name,icon,view,self,closeable=closeable)
		if not parent:
			parent = self

		if isinstance(parent,NavigationElement):
			parent.appendSubChild(aNav)
		else:
			parent.appendChild(aNav)
		self.navigationPoints.update({view:aNav})
		if closeable:
			aNav.navigationAction()
		return aNav

	def addNavigationPointAfter( self,name,icon,view=None,beforeElement=None,closeable=False ):
		aNav = NavigationElement( name, icon, view, self,closeable=closeable )
		if beforeElement:
			beforeElement.parent().insertAfter( aNav, beforeElement )
		else:
			self.appendChild(aNav) #append at the end

		self.navigationPoints.update({view:aNav})
		if closeable:
			aNav.navigationAction()
		return aNav

	def removeNavigationPoint( self,view ):
		aNav = self.navigationPoints[view]
		aNav.RemoveAction()
		del self.navigationPoints[view]



