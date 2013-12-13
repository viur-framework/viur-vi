import html5

class Preview( html5.Div ):
	def __init__(self, urls, entry, modul, *args, **kwargs ):
		super( Preview, self ).__init__( *args, **kwargs )
		self.urls = urls
		self.entry = entry
		self.modul = modul
		self.urlCb = html5.Select()
		self.appendChild(self.urlCb)
		self.previewFrame = html5.Iframe()
		self.appendChild(self.previewFrame)
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
		self["class"].append("preview")

	def onChange(self, event):
		event.stopPropagation()
		newUrl = self.urlCb["options"].item(self.urlCb["selectedIndex"]).value
		self.setUrl( newUrl )

	def setUrl(self, url ):
		url = url.replace("{{id}}",self.entry["id"]).replace("{{modul}}",self.modul )
		self.previewFrame["src"] = url


