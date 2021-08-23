from vi import html5
from vi.framework.observable import StateHandler
#from vi.framework.components.icon import Icon

class TreeNode(html5.Div):
	# language=HTML
	tpl = '''
		<div [name]="item" class="item has-hover">
			<a class="item-link" @click="navigationAction">
				<div class="item-content" [name]="itemContent">

				</div>
			</a>

			<span [name]="itemArrow" class="item-open is-hidden" @click="ArrowAction">

			</span>
		</div>
		<div [name]="subItem" class="list list--sub is-hidden"  style="margin-left:10px" >
		</div>
		'''

	def __init__(self, name, *args, **kwargs):
		super().__init__()
		self["class"] = "itemGroup"
		self.kwargs = kwargs

		self.state = StateHandler( ["hasSubItems"] ,self )
		self.state.register("hasSubItems" ,self)

		self.fromHTML(
			self.tpl,
			vars={
				#icon = icon,
				#"name":name
			}
		)

		if isinstance(name,str):
			adiv = html5.Div()
			adiv.addClass("item-headline")
			adiv.appendChild(name)

			self.itemContent.appendChild(adiv)
		else:
			self.itemContent.appendChild(name)

		if "action" in kwargs:
			self.action = kwargs["action"]
		else:
			self.action = None


		self.state.updateState( "hasSubItems", False )


	def navigationAction(self,e,wdg=None):
		self.ArrowAction(e,wdg)

		if self.action:
			self.action(self,**self.kwargs)

	def ArrowAction( self ,e, wdg=None ):
		self.subItem.toggleClass("is-hidden")
		self.itemArrow.toggleClass("is-hidden")

	def onHasSubItemsChanged( self ,e ,wdg ):
		'''
			If subChild is added, show itemArrow, hide if no subitem present
		'''
		if e:
			self.itemArrow.show()
		else:
			self.itemArrow.hide()

	def appendSubChild( self ,element ):
		self.state.updateState("hasSubItems" ,True)
		self.subItem.appendChild(element)

class Tree(html5.Div):

	def __init__(self, treeStructure):
		super().__init__()
		self.treeStructure = treeStructure

		self.buildTree(self.treeStructure)
		print("GGGG")


	def buildTree(self, tree, parent=None):
		if not parent:
			parent = self

		for entry in tree:
			entryWidget = TreeNode(**entry)

			parent.appendChild(entryWidget)

			if "children" in entry and entry["children"]:
				self.buildTree(entry["children"],entryWidget.subItem)


















