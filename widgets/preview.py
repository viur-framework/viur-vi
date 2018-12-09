import html5
from config import conf

class Preview( html5.Div ):
	def __init__(self, urls, entry, modul, *args, **kwargs ):
		super( Preview, self ).__init__( *args, **kwargs )
		self.addClass("vi-widget vi-widget--preview")
		self.urls = urls
		self.entry = entry
		self.module = modul
		containerDiv = html5.Div()
		containerDiv.addClass("actionbar")
		self.appendChild(containerDiv)
		self.urlCb = html5.Select()
		containerDiv.appendChild(self.urlCb)
		self.previewFrame = html5.Iframe()
		self.appendChild(self.previewFrame)
		btnClose = html5.ext.Button("Close", callback=self.doClose)
		btnClose.addClass("icon close")
		containerDiv.appendChild(btnClose)
		currentUrl = None
		for name,url in urls.items():
			o = html5.Option()
			o["value"] = url
			o.appendChild(html5.TextNode(name))
			self.urlCb.appendChild(o)
			if currentUrl is None:
				currentUrl = url
		self.setUrl( currentUrl )
		self.sinkEvent("onChange")
		self.addClass("preview")

	def onChange(self, event):
		event.stopPropagation()
		newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value
		self.setUrl( newUrl )

	def setUrl(self, url ):
		url = url.replace("{{id}}",self.entry["id"]).replace("{{modul}}",self.module )
		self.previewFrame["src"] = url

	def doClose(self, *args, **kwargs ):
		conf["mainWindow"].removeWidget(self)

