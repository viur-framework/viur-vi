#-*- coding: utf-8 -*-

import html5
from network import NetworkService, DeferredCall
from i18n import translate
from event import EventDispatcher
from config import conf

class LoginInputField(html5.Input):

	def __init__(self, notifier, *args, **kwargs):
		super(LoginInputField, self).__init__(*args, **kwargs)
		self.sinkEvent("onKeyPress")

		self.onKeyPressEvent = EventDispatcher("keyPress")
		self.onKeyPressEvent.register(notifier)

	def onKeyPress(self, event):
		self.onKeyPressEvent.fire(event)

class LoginLoader(html5.Div):

	def __init__(self, parent = None, *args, **kwargs):
		super(LoginLoader, self).__init__(*args, **kwargs)

		self.addClass("vi-login-screen-loader")

		img = html5.Img()
		img[ "src" ] = "icons/is_loading.gif"
		self.appendChild(img)

		self.text = html5.Span()
		self.appendChild(self.text)

		if parent:
			parent.appendChild(self)

		self.update()

	def update(self):
		self.text.removeAllChildren()
		self.text.appendChild(html5.TextNode(translate("Please wait...")))

class LoginHandler(html5.Li):
	method = None

	def __init__(self, loginScreen, *args, **kwargs):
		assert self.method, "Method must be set in class!"
		assert isinstance(loginScreen, LoginScreen)
		super(LoginHandler, self).__init__(*args, **kwargs)

		self.methodClass = self.method.replace("X-VIUR-AUTH-", "").lower()

		self.loginScreen = loginScreen

		self.addClass("vi-login-handler-%s" % self.methodClass)
		self.sinkEvent("onClick")

		self.loginScreen.loginMethodSelector.appendChild(self)

		self.appendChild(html5.TextNode(translate("vi.login.handler.%s" % self.methodClass)))

		self.mask = html5.Div()
		self.mask.addClass("vi-login-mask-%s" % self.methodClass)
		loginScreen.appendChild(self.mask)

	def onClick(self, event):
		self.loginScreen.selectHandler(self)

	def enable(self):
		self.addClass("is-active")
		self.mask.show()

	def disable(self):
		self.removeClass("is-active")
		self.mask.hide()

	def reset(self):
		pass

class LoginHandler_UserPassword(LoginHandler):
	method = "X-VIUR-AUTH-User-Password"

	def __init__(self, loginScreen, *args, **kwargs):
		super(LoginHandler_UserPassword, self).__init__(loginScreen, *args, **kwargs)

		# Standard Login Form
		self.pwform = html5.Form()
		self.mask.appendChild(self.pwform)

		self.username = LoginInputField(self)
		self.username["name"] = "username"
		self.username["placeholder"] = translate("Username")
		self.pwform.appendChild(self.username)

		self.password = LoginInputField(self)
		self.password["type"] = "password"
		self.password["name"] = "password"
		self.password["placeholder"] = translate("Password")
		self.pwform.appendChild(self.password)

		self.loginBtn = html5.ext.Button(translate("Login"), callback=self.onLoginClick)
		self.pwform.appendChild(self.loginBtn)

		# One Time Password
		self.otpform = html5.Form()
		self.otpform.hide()
		self.mask.appendChild(self.otpform)

		self.otp = LoginInputField(self)
		self.otp["name"] = "otp"
		self.otp["placeholder"] = translate("One Time Password")
		self.otpform.appendChild(self.otp)

		self.verifyBtn = html5.ext.Button(translate("Verify"), callback=self.onVerifyClick)
		self.otpform.appendChild(self.verifyBtn)

	def onKeyPress(self, event):
		if event.keyCode == 13:
			if html5.utils.doesEventHitWidgetOrChildren(event, self.username):
				if self.username["value"]:
					self.password.element.focus()
			elif html5.utils.doesEventHitWidgetOrChildren(event, self.password):
				if self.username["value"] and self.password["value"]:
					self.onLoginClick()
			elif html5.utils.doesEventHitWidgetOrChildren(event, self.otp):
				if self.otp["value"]:
					self.onVerifyClick()

			event.stopPropagation()
			event.preventDefault()

	def onLoginClick(self, sender = None):
		if not (self.username["value"] and self.password["value"]):
			return # fixme

		self.loginBtn["disabled"] = True
		self.loginScreen.loader.show()

		NetworkService.request("user", "auth_userpassword/login",
		                        params={"name": self.username["value"],
		                                "password": self.password["value"]},
		                        secure=True,
		                        successHandler=self.doLoginSuccess,
		                        failureHandler=self.doLoginFailure)

	def doLoginSuccess(self, req):
		answ = NetworkService.decode(req)
		print(answ)

		self.loginScreen.loader.hide()
		self.loginBtn["disabled"] = False

		if answ == "OKAY":
			self.reset()
			self.loginScreen.invoke()
		elif answ == "ONE-TIME-PASSWORD":
			self.pwform.hide()
			self.otpform.show()
			self.otp.focus()
		else:
			self.password.focus()

	def doLoginFailure(self, *args, **kwargs):
		alert("Fail")

	def onVerifyClick(self, sender = None):
		if not self.otp["value"]:
			return # fixme

		self.verifyBtn["disabled"] = True
		self.loginScreen.loader.show()

		NetworkService.request("user", "f2_otp2factor/otp",
		                        params={"otptoken": self.otp["value"]},
		                        secure=True,
		                        successHandler=self.doVerifySuccess,
		                        failureHandler=self.doVerifyFailure)

	def doVerifySuccess(self, req):
		self.loginScreen.loader.hide()
		self.verifyBtn["disabled"] = False

		if NetworkService.isOkay(req):
			self.reset()
			self.doLoginSuccess(req)
		else:
			self.otp["value"] = ""
			self.otp.focus()

	def doVerifyFailure(self, *args, **kwargs):
		self.reset()
		self.enable()

	def reset(self):
		self.loginBtn["disabled"] = False
		self.verifyBtn["disabled"] = False

		self.otp["value"] = ""
		self.username["value"] = ""
		self.password["value"] = ""

	def enable(self):
		self.pwform.show()
		self.otpform.hide()

		super(LoginHandler_UserPassword, self).enable()
		DeferredCall(self.focusLaterIdiot)

	def focusLaterIdiot(self):
		self.username.focus()

class LoginHandler_GoogleAccount(LoginHandler):
	method = "X-VIUR-AUTH-Google-Account"

	def __init__(self, loginScreen, *args, **kwargs):
		super(LoginHandler_GoogleAccount, self).__init__(loginScreen, *args, **kwargs)

		self.loginBtn = html5.ext.Button(translate("Login with Google"), callback=self.onLoginClick)
		self.mask.appendChild(self.loginBtn)

	def onLoginClick(self, sender = None):
		self.loginScreen.loader.show()
		eval("window.top.preventViUnloading = false;")
		eval("window.top.location = \"/vi/user/auth_googleaccount/login\"")

class LoginScreen(html5.Div):
	possibleHandlers = [LoginHandler_UserPassword, LoginHandler_GoogleAccount]

	def __init__(self, parent, *args, **kwargs):
		super(LoginScreen, self).__init__(*args, **kwargs)
		parent.appendChild(self)

		self.loginEvent = EventDispatcher("login")
		self.loginEvent.register(parent)

		self.addClass("vi-login")

		# --- Loader ---
		self.loader = LoginLoader(self)

		# --- Header ---

		header = html5.Div()
		header.addClass("vi-login-header")
		self.appendChild(header)

		# Login
		h1 = html5.H1()
		h1.appendChild(html5.TextNode(translate("vi.login.title")))
		header.appendChild(h1)

		# Logo
		img = html5.Img()
		img["src"] = "login/login-logo.png"
		header.appendChild(img)

		# --- Dialog ---

		dialog = html5.Div()
		dialog.addClass("vi-login-dialog")
		self.appendChild(dialog)

		self.loginMethodSelector = html5.Ul()
		self.loginMethodSelector.addClass("vi-login-method")
		dialog.appendChild(self.loginMethodSelector)

		NetworkService.request("user", "getAuthMethods",
		                        successHandler=self.onGetAuthMethodsSuccess,
		                        failureHandler=self.onGetAuthMethodsFailure)
		self.hide()

	def invoke(self, logout = False):
		self.loader.show()

		conf["currentUser"] = None

		#Enforce logout
		if logout:
			NetworkService.request("user", "logout",
					                successHandler=self.onLogoutSuccess,
					                secure=True)
			return

		#Check if already logged in!
		NetworkService.request( "user", "view/self",
		                        secure=True,
		                        successHandler=self.doSkipLogin,
		                        failureHandler=self.doShowLogin)


	def onLogoutSuccess(self, req):
		self.invoke()

	def doShowLogin(self, *args, **kwargs):
		self.loader.hide()
		self.show()
		self.selectHandler()

	def doSkipLogin(self, req):
		answ = NetworkService.decode(req)
		if answ.get("action") != "view":
			self.doShowLogin()
			return

		self.hide()

		conf["currentUser"] = answ["values"]
		if not any([x in conf["currentUser"].get("access", []) for x in ["admin", "root"]]):
			self.reset()
			self.loginScreen.redirectNoAdmin()

		print("User already logged in")
		self.loginEvent.fire()

	def onGetAuthMethodsSuccess(self, req):
		answ = NetworkService.decode(req)

		methods = []
		for method in answ:
			if method[0] not in methods:
				methods.append(method[0])

		for method in methods:
			for handler in self.possibleHandlers:
				if method == handler.method:
					handler(self)

		self.loader.hide()

	def selectHandler(self, handler = None):
		for h in self.loginMethodSelector._children:
			if handler is None or h is handler:
				h.enable()
				handler = h
			else:
				h.disable()

	def onGetAuthMethodsFailure(self, *args, **kwargs):
		alert("Fail")

	def redirectNoAdmin(self):
		eval("window.top.preventViUnloading = false;")
		eval("window.top.location = \"/\"")

