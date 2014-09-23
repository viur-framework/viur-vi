__author__ = 'stefan'

from datetime import datetime
from html5.div import Div
from html5.textnode import TextNode
from widgets.table import DataTable
from network import NetworkService
from priorityqueue import viewDelegateSelector, actionDelegateSelector
from html5.ext.popup import YesNoDialog
from html5.ext.button import Button
from html5.a import A

class CsvExport(Div):

	_batchSize = 20  #How many row we fetch at once
	def __init__( self,  *args, **kwargs ):
		"""
			@param modul: Name of the modul we shall handle. Must be a list application!
			@type modul: string
		"""
		super(CsvExport, self ).__init__(  )
		self.table = DataTable()
		self.appendChild( self.table )
		self._currentCursor = None
		#self._currentSearchStr = None
		self._structure = None
		self._currentRequests = []
		self.columns = []
		self.table.setDataProvider(self)
		self.filter =  {"state_rts":"1"}
		self.columns = ["base_name", "base_bezerp", "pother", "base_artnr", "base_preis", "base_produkt", "base_sc_variant", "base_menge",
		                "base_menge_ganzzahl", "base_image", "gallery_images", "bestand", "kl_groesse", "abmessung",
		                "hoehe", "breite", "durchmesser", "material", "farbe", "optiken", "leistung", "verbrauch", "typ", "data_state"]
		self.skelData = None
		self._tableHeaderIsValid = False
		#Proxy some events and functions of the original table
		self.emptyNotificationDiv = Div()
		self.emptyNotificationDiv.appendChild(TextNode("Currently no entries"))
		self.emptyNotificationDiv["class"].append("emptynotification")
		self.appendChild(self.emptyNotificationDiv)
		#self.search = Search()
		#self.appendChild(self.search)
		#self.search.startSearchEvent.register( self )
		self.emptyNotificationDiv["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		self.exportBtn = Button("Export", self.on_btnExport_released)
		self.appendChild( self.exportBtn )
		self.markSendBtn = Button("Als versendet markieren", self.on_btnMarkSend_released)
		self.appendChild( self.markSendBtn )
		self.reloadData()

	def onNextBatchNeeded(self, *args, **kwargs):
		pass

	def showErrorMsg(self, req=None, code=None):
		"""
			Removes all currently visible elements and displayes an error message
		"""
		self.actionBar["style"]["display"] = "none"
		self.table["style"]["display"] = "none"
		#self.search["style"]["display"] = "none"
		errorDiv = Div()
		errorDiv["class"].append("error_msg")
		if code and (code==401 or code==403):
			txt = "Access denied!"
		else:
			txt = "An unknown error occurred!"
		errorDiv["class"].append("error_code_%s" % (code or 0))
		errorDiv.appendChild( TextNode( txt ) )
		self.appendChild( errorDiv )

	#def onStartSearch(self, searchTxt):
	#	self._currentSearchStr = searchTxt
	#	self.reloadData()

	def DIS_onNextBatchNeeded(self):
		"""
			Requests the next rows from the server and feed them to the table.
		"""
		if self._currentCursor:
			filter = self.filter.copy()
			filter["amount"] = self._batchSize
			if self._currentCursor is not None:
				filter["cursor"] = self._currentCursor
			self._currentRequests.append( NetworkService.request( "order", "list", filter, successHandler=self.onCompletion, failureHandler=self.showErrorMsg ) )
			self._currentCursor = None

	def reloadData(self):
		"""
			Removes all currently displayed data and refetches the first batch from the server.
		"""
		self.table.clear()
		self._currentCursor = None
		self._currentRequests = []
		filter = self.filter.copy()
		filter["amount"] = self._batchSize
		#if self._currentSearchStr:
		#	filter["search"] = self._currentSearchStr
		self.table.setDataProvider( self )
		self._currentRequests.append( NetworkService.request( "order", "list", filter, successHandler=self.onCompletion, failureHandler=self.showErrorMsg ) )


	def onCompletion(self, req):
		"""
			Pass the rows received to the datatable.
			@param req: The network request that succeed.
		"""
		if not req in self._currentRequests:
			return
		self._currentRequests.remove( req )
		#self.search.resetLoadingState()
		data = NetworkService.decode( req )
		if data["structure"] is None:
			if self.table.getRowCount():
				self.table.setDataProvider(None) #We cant load any more results
			else:
				self.table["style"]["display"] = "none"
				self.emptyNotificationDiv["style"]["display"] = ""
			#self.element.innerHTML = "<center><strong>Keine Ergebnisse</strong></center>"
			return
		self.table["style"]["display"] = ""
		self.emptyNotificationDiv["style"]["display"] = "none"
		self._structure = data["structure"]
		tmpDict = {}
		for key, bone in data["structure"]:
			tmpDict[ key ] = bone
		if not self._tableHeaderIsValid:
			if not self.columns:
				self.columns = []
				for boneName, boneInfo in data["structure"]:
					if boneInfo["visible"]:
						self.columns.append( boneName )
			self.setFields( self.columns )
		if "cursor" in data.keys():
			self._currentCursor = data["cursor"]
		self.skelData = data["skellist"]
		self.table.extend( data["skellist"] )

	def setFields(self, fields):
		if not self._structure:
			self._tableHeaderIsValid = False
			return
		boneInfoList = []
		tmpDict = {}
		for key, bone in self._structure:
			tmpDict[ key ] = bone
		fields = [x for x in fields if x in tmpDict.keys()]
		self.columns = fields
		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( "order", boneName, tmpDict )( "order", boneName, tmpDict )
			self.table.setCellRender( boneName, delegateFactory )
			boneInfoList.append( boneInfo )
		self.table.setHeader( [x["descr"] for x in boneInfoList])
		self.table.setShownFields( fields )
		rendersDict = {}
		for boneName in fields:
			boneInfo = tmpDict[boneName]
			delegateFactory = viewDelegateSelector.select( "order", boneName, tmpDict )( "order", boneName, tmpDict )
			rendersDict[ boneName ] = delegateFactory
			boneInfoList.append( boneInfo )
		self.table.setCellRenders( rendersDict )
		self._tableHeaderIsValid = True



	#####################################################################################################################

	def calcProductCode( self, data ):
		prodKey = ""
		if data["shipping_country"].upper() == "DE":
			return( "EPN" )
		elif data["shipping_country"].upper() in self.europeanCountry:
			return( "BPI" )
		#return( "EPI" )
		else:
			return( "BPI" )

	def calcGewicht(self, data):
		return( str(1*2.9) ) #FIXME !!!!!!! float( data["amt"])

	def getNachname(self, data):
		if( data["payment_type"] == "nachnahme" ):
			return("1")
		return("")

	def getNachnamePrice(self, data):
		return(str(float(data["price"])-2.0))

	def on_btnExport_released(self, *args, **kwargs ):
		if not self.skelData:
			return
		data = self.skelData
		resStr = ""
		idx = 1
		for recipient in data:
			values = [ 	"%010i" % idx ,  #Ordnungsnummer
			              "DPEE-SHIPMENT",  # Satzart
			              self.calcProductCode( recipient ), #Produktcode
			              datetime.now().strftime("%Y%m%d"),  #Sendungsdatum
			              self.calcGewicht( recipient ), # Gewicht
			              "", #Volumen
			              "", #Versicherungswert
			              "", #Versicherungswährung
			              "", #Referenz
			              "", #Leerfeld
			              "", #Senderreferenz
			              "", #Service Nachname? # self.getNachname( recipient )
			              self.getNachnamePrice( recipient ) if self.getNachname( recipient ) else "" ,
			              "EUR" if self.getNachname( recipient ) else "", #Nachname währung
			              "CHEQUE" if self.getNachname( recipient ) else "", #Nachname Type
			              "", #Unfrei
			              "", #Express10
			              "", #Express12
			              "", #Express9
			              "", #Gefahrgut
			              "", #Höherversichert
			              "", #Sperrgut
			              "", #Sperrugt Type
			              "", #Nachtservice
			              "", #Zustelldatum
			              "", #Warenwert
			              "", #Warenwährung
			              "", #Sperrgut alternateBase
			              "", #Gefahrgutklasse
			              "", #Handelsbedingungen
			              "", #Sondersendung
			              "", #Empfänger Zahlt
			              "", #Samstagszustellung
			              "01", #Teilnahme
			              "", #Beleglose nachname #self.getNachname( recipient ) if self.getNachname( recipient ) else ""
			              "", #Zeitpunktzustellung
			              "", #Zustellzeitpunkt
			              "", #Sonderfrüh
			              "", #Nachmittagszustellung
			              "", #Abendzustellung
			              "", #Sonn u Feiertag
			              "", #EPN Mehrpacket
			              "", #Indent
			              "", #Eigenhändig
			              "", #Rückschein
			              "", #Samstagsabholung
			              "", #Spätabholung
			              "", #Abliefernachweis
			              "", #Unfrei Zahlungstyp
			              "", #Unfrei Kundennnr
			              "", #Kennzahl Fracht Straße
			              "", #Service selbstabholung
			              "", #Economy
			              "", #Premium
			              "", #Seepacket
			              "", #Service Rolle
			              "", #Anzahl Int.
			              "", #Vorausverfügung
			              "", #Vorausverfügung Typ
			              "", #* Transport
			              "", #Leerfeld 61
			              "", #Leerfeld 62
			              "", #Leerfeld 63
			              "", #Leerfeld 64
			              "", #Leerfeld 65
			              "", #Leerfeld 66
			              "", #Leerfeld 67
			              "", #Leerfeld 68
			              "", #Leerfeld 69
			              "", #Leerfeld 70
			              "", #Leerfeld 71
			              "", #Leerfeld 72
			              "", #Go Green
			              "", #SMSAVISO
			              "", #Ident Extrag
			              "", #Prokative Prüfung
			              "", #Indet & Age
			              "", #BYPASS
			              "", #Directinject
			              "", #Vertragsvorlagen
			              "", #Leerfeld
			              "", #Teillieferung
			              "", #Delivery Time From Hour
			              "", #Delivery Time From Min
			              "", #Delivery Time To Hour
			              "", #Delivery Time To Min
			              "", #Hold
			              "", #Handover
			              "", #Bonded
			              "", #Breakbulk
			              "", #Storage
			              "", #Dispo
			              "", #Nopart delivery
			              "", #Delivery Notification
			              "", #NDS
			              "", #Distribute
			              "", #Duties Taxes Paid
			              "", #Split Vat
			              "", #Stretch
			              "", #Remote delivery
			              "", #Transport collection
			              "", #Prealert
			              "", #Drop at Facility
			              "", #Ident Premium
			              "" #Sendungs Avise
			]
			## Satzart Sendung
			line = "|".join( values )+"\n"
			resStr += line #.encode("CP1252", "ignore")
			## Satzart Absender
			values = [
				"%010i" % idx ,  #Ordnungsnummer
				"DPEE-SENDER", #Satzart
				"6250641885",  #KundenNR
				"jerry-s.com", #Firmenname
				"", #*2
				"Dr. Alexander Berlin", #Kontakt
				u"Edelweißstraße", #Straße
				"36", #Hausnr
				"", #Zusatz
				"13158", #PLZ
				"Berlin", #Stadt
				"DE", #Land
				"", #Comment
				"", #email
				"00493053799201", #Telefon
				"", #Code Branch
				"", #Zusatz 1
				"", #Zusatz 2
				"", #Zusatz 3
				"", #Leer
				"", #Leer
				"50010517", #BLZ
				"540793691", #KontoNR
				"ING Diba", #Bankname
				"Alexander Berlin", #KontoInh.
				"Best %s" % recipient["idx"], #Verwendungszweck
				"", #Leer
				"", #Leer
				"DE276952027", #UST-ID
				"DE11500105175407936916", #IBAN
				"INGDDEFF", #BIC/SWIFT
				"", #Mobile
				"", #Cust Reg Nr
				"", #Add. Address 2
				"", #Customer Ref Nr
				"",  #Fax
				"" # Broken 1
			]
			line = "|".join( values )+"\n"
			resStr += line #.encode("CP1252", "ignore")
			values = [
				"%010i" % idx ,  #Ordnungsnummer
				"DPEE-RECEIVER", #Satzart
				"%s %s" % (recipient["shipping_firstname"], recipient["shipping_lastname"] ), #Firma 1
				"", #Firma 2
				"", #Firma 3
				"", #KundenNR
				"%s %s" % (recipient["shipping_firstname"], recipient["shipping_lastname"] ), #Kontakt
				recipient["shipping_street"][ : recipient["shipping_street"].rfind(" ") ], #Straße
				recipient["shipping_street"][ recipient["shipping_street"].rfind(" ") +1: ],  #Hausnr
				"", #Addr 2
				str(recipient["shipping_zip"]), #PLZ
				str(recipient["shipping_city"]), #Stadt
				str(recipient["shipping_country"]), #Land
				"", #EmpfängerNR
				"", #Email
				"", #TeleNR
				"", #UST-ID
				"", #Matchcode
				"", #Zusatz 1
				"", #Zusatz 2
				"", #Zusatz 3
				"", #Bemerkung
				"", #Notiz
				"", #Empfänger Kndnr
				"", #Leer
				"", #Handy
				"", #ISO State
				"", #Zusatz
				"", #Ref NR
				"",  #Fax
				"" # Broken 1
			]
			#Satzart Empfänger
			line = "|".join( values )+"\n"
			resStr += line #.encode("CP1252", "ignore")
			values = [
				"%010i" % idx ,  #Ordnungsnummer
				"DPEE-ITEM", #Satzart
				self.calcGewicht( recipient ), # Gewicht
				"", #Länge
				"", #Breite
				"", #Höhe
				"Jerry-s", #Descr
				"PK", #Packart
				"O%s" % recipient["idx"],  #Ref
				"",  #Broken 1
				"" #Broken 2
			]
			#Satzart Packstück
			line = "|".join( values )+"\n"
			resStr += line #.encode("CP1252", "ignore")
			# ExportDokument
			if not recipient["shipping_country"].upper() in self.europeanCountry or 1:
				prodDict = {}
				for prod in recipient["product"]:
					if prod["id"] in prodDict.keys():
						prodDict[ prod["id"] ]["amt"] += 1
					else:
						prodDict[ prod["id"] ] = prod.copy()
						prodDict[ prod["id"] ]["amt"] = 1
				for prod in prodDict.values():
					values = [
						"%010i" % idx ,  #Ordnungsnummer
						"DPEE-EXPORT-ITEM", #Satzart
						prod["name"], #Bescr
						str(prod["amt"]), #Anzahl #FIXME: !!!!! str( int( recipient["amt"] ) )
						str(prod["preis"]), #Wert pro Stück
						str(float(prod["gewicht_netto"])*prod["amt"]), # Nettogewicht
						str(float(prod["gewicht_brutto"])*prod["amt"]), # Bruttogewicht
						"DE", #Ursprungsland
						"" #ZolltariefNR
					]
					line = "|".join( values )+"\n"
					resStr += line #.encode("CP1252", "ignore")
			idx += 1
		tmpA = A()
		encFunc = eval("encodeURIComponent");
		tmpA["href"] = "data:text/plain;charset=utf-8,"+encFunc(resStr)
		tmpA["download"] = "DHL-Export.csv"
		tmpA.element.click()
		print( resStr )

	def onAttach(self):
		super( CsvExport, self ).onAttach()
		NetworkService.registerChangeListener( self )

	def onDetach(self):
		super( CsvExport, self ).onDetach()
		NetworkService.removeChangeListener( self )

	def onDataChanged(self, modul):
		"""
			Refresh our view if element(s) in this modul have changed
		"""
		if modul and modul!="order":
			return
		self.reloadData( )


	def on_btnMarkSend_released(self, *args, **kwargs ):
		if not self.skelData:
			return
		YesNoDialog("%s Bestellungen als versendet markieren?" % len(self.skelData),title="Versendet markieren?",yesCallback=self.markSend)

	def markSend( self, *args, **kwargs ):
		if not self.skelData:
			return
		for item in self.skelData:
			NetworkService.request("order","markSend",{"id":  item["id"] }, secure=True, modifies=True)
		#self.request.addQuery( NetworkService.request( "/order/markSend", {"id":  item["id"] }, secure=True ) )
		#self.connect( self.request, QtCore.SIGNAL("finished(PyQt_PyObject)"), self.onFinished )

	def onFinished(self, req ):
		if self.request.isIdle():
			self.request.deleteLater()
			self.request = None
		self.overlay.inform( self.overlay.SUCCESS )

	def on_btnReload_released(self, *args, **kwargs ):
		self.model.requestedPage = 0
		self.model.reloadData()
