#-*- coding: utf-8 -*-
import re, json, logging
from flare import html5,utils
from flare.popup import Alert
from flare.button import Button
from flare.event import EventDispatcher

from flare.network import NetworkService, DeferredCall
from flare.i18n import translate
from .config import conf
from .priorityqueue import loginHandlerSelector
from .screen import Screen
from .widgets import InternalEdit


class LoginInputField(html5.Input):

	def __init__(self, notifier, *args, **kwargs):
		super(LoginInputField, self).__init__(*args, **kwargs)
		self.addClass("vi-login-input input")
		self.sinkEvent("onKeyPress")

		self.onKeyPressEvent = EventDispatcher("keyPress")
		self.onKeyPressEvent.register(notifier)

	def onKeyPress(self, event):
		self.onKeyPressEvent.fire(event)


class BaseLoginHandler(html5.Li):
	def __init__(self, loginScreen, *args, **kwargs):
		assert isinstance(loginScreen, LoginScreen)
		super(BaseLoginHandler, self).__init__(*args, **kwargs)

		self.loginScreen = loginScreen

		if not "cssname" in dir(self):
			self.cssname = self.__class__.__name__.lower()

		self.addClass("vi-login-handler btn btn--small ")
		self.addClass("vi-login-handler-%s" % self.cssname)
		self.sinkEvent("onClick")

		self.loginScreen.loginMethodSelector.appendChild(self)

		self.appendChild(html5.TextNode(translate("vi.login.handler.%s" % self.cssname)))

		# --- Surrounding Dialog ---
		self.loginDialog = html5.Div()
		self.loginDialog.addClass("vi-login-dialog popup popup--center")
		self.loginDialog.addClass("vi-login-dialog-%s" % self.cssname)
		self.loginScreen.appendChild(self.loginDialog)

		# --- Dialog ---
		self.loginBox = html5.Div()
		self.loginBox.addClass("box box--content-wide")
		self.loginDialog.appendChild(self.loginBox)

		# --- Header ---
		self.loginHeader = html5.Div()
		self.loginHeader.addClass("vi-login-header")
		self.loginBox.appendChild(self.loginHeader)

		self.mask = html5.Div()
		self.mask.addClass("vi-login-mask")
		self.mask.addClass("vi-login-mask-%s" % self.cssname)
		self.loginBox.appendChild(self.mask)

		# Login
		# h1 = html5.H1()
		# h1.addClass("vi-login-headline")
		# h1.appendChild(html5.TextNode(translate("vi.login.title")))
		# header.appendChild(h1)

		# Logo
		img = html5.Img()
		img.addClass("vi-login-logo")
		img["src"] = "public/images/vi-login-logo.svg"
		self.loginHeader.appendChild(img)


	def onClick(self, event):
		self.loginScreen.selectHandler(self)

	def enable(self):
		self.addClass("is-active")
		self.loginDialog.addClass("is-active")

	def disable(self):
		self.removeClass("is-active")
		self.loginDialog.removeClass("is-active")

	def lock(self):
		self.loginScreen.lock()

	def unlock(self):
		self.loginScreen.unlock()

	def login(self):
		self.reset()
		self.loginScreen.invoke()

	def reset(self):
		pass

	def parseAnswer(self, req):
		res = re.search("JSON\(\((.*)\)\)", req.result)

		if res:
			answ = json.loads(res.group(1))
		else:
			answ = NetworkService.decode(req)

		return answ


class UserPasswordLoginHandler(BaseLoginHandler):
	cssname = "userpassword"

	def __init__(self, loginScreen, *args, **kwargs):
		super(UserPasswordLoginHandler, self).__init__(loginScreen, *args, **kwargs)

		# Standard Login Form
		self.pwform = html5.Form()
		self.mask.appendChild(self.pwform)

		self.username = LoginInputField(self)
		self.username["type"] = "text"
		self.username["name"] = "username"
		self.username["placeholder"] = translate("Username")
		self.pwform.appendChild(self.username)

		self.password = LoginInputField(self)
		self.password["type"] = "password"
		self.password["name"] = "password"
		self.password["placeholder"] = translate("Password")
		self.pwform.appendChild(self.password)

		self.loginBtn = Button(translate("Login"), callback=self.onLoginClick)
		self.loginBtn.addClass("vi-login-btn btn--viur")
		self.pwform.appendChild(self.loginBtn)

		# One Time Password
		self.otpform = html5.Form()
		self.otpform.hide()
		self.mask.appendChild(self.otpform)

		self.otp = LoginInputField(self)
		self.otp["name"] = "otp"
		self.otp["placeholder"] = translate("One Time Password")
		self.otpform.appendChild(self.otp)

		self.verifyBtn = Button(translate("Verify"), callback=self.onVerifyClick)
		self.otpform.appendChild(self.verifyBtn)

		# Universal edit widget
		self.editform = html5.Div()
		self.editform.hide()
		self.mask.appendChild(self.editform)

		self.edit = html5.Div()
		self.editform.appendChild(self.edit)

		self.editskey = self.editaction = self.editwidget = None

		self.sendBtn = Button(translate("Send"), callback=self.onSendClick)
		self.editform.appendChild(self.sendBtn)

	def onKeyPress(self, event):
		if html5.isReturn(event):
			if utils.doesEventHitWidgetOrChildren(event, self.username):
				if self.username["value"]:
					self.password.element.focus()
			elif utils.doesEventHitWidgetOrChildren(event, self.password):
				if self.username["value"] and self.password["value"]:
					self.onLoginClick()
			elif utils.doesEventHitWidgetOrChildren(event, self.otp):
				if self.otp["value"]:
					self.onVerifyClick()

			event.stopPropagation()
			event.preventDefault()

	def onLoginClick(self, sender = None):
		if not (self.username["value"] and self.password["value"]):
			self.loginIncompleteMsg = html5.Div()
			self.loginIncompleteMsg.addClass("msg msg--error is-active")
			self.loginIncompleteMsg
			self.loginHeader.appendChild(self.loginIncompleteMsg)
			return # fixme

		self.loginBtn["disabled"] = True
		self.lock()

		NetworkService.request("user", "auth_userpassword/login",
		                        params={"name": self.username["value"],
		                                "password": self.password["value"]},
		                        secure=True,
		                        successHandler=self.doLoginSuccess,
		                        failureHandler=self.doLoginFailure)

	def doLoginSuccess(self, req):
		self.unlock()
		self.loginBtn["disabled"] = False
		self.sendBtn["disabled"] = False

		answ = self.parseAnswer(req)

		if answ == "OKAY":
			self.login()

		elif isinstance(answ, dict) and "action" in answ:
			if answ["action"] == "otp":
				self.pwform.hide()
				self.editform.hide()
				self.otpform.show()
				self.otp.focus()
			else:
				self.pwform.hide()
				self.otpform.hide()
				self.edit.removeAllChildren()

				self.editaction = "auth_userpassword/%s" % answ["action"]
				self.editwidget = InternalEdit(answ["structure"], answ["values"], defaultCat = None)
				self.edit.appendChild(self.editwidget)

				if answ["params"]:
					self.editskey = answ["params"].get("skey")

				self.editform.show()
		else:
			self.password.focus()

	def doLoginFailure(self, req, code, *args, **kwargs):
		Alert(
				translate("Failure %d" % int(code) ),
				title = translate( "Login error" )
				)

	def onVerifyClick(self, sender = None):
		if not self.otp["value"]:
			return # fixme

		self.verifyBtn["disabled"] = True
		self.lock()

		NetworkService.request("user", "f2_timebasedotp/otp",
		                        params={"otptoken": self.otp["value"]},
		                        secure=True,
		                        successHandler=self.doVerifySuccess,
		                        failureHandler=self.doVerifyFailure)

	def doVerifySuccess(self, req):
		self.unlock()
		self.verifyBtn["disabled"] = False

		answ = self.parseAnswer(req)

		if answ == "OKAY":
			self.login()
			return

		self.otp["value"] = ""
		self.otp.focus()

	def doVerifyFailure(self, *args, **kwargs):
		self.reset()
		self.enable()

	def onSendClick(self, sender=None):
		assert self.editwidget and self.editaction

		self.lock()
		self.sendBtn["disabled"] = True

		params = self.editwidget.doSave()
		if self.editskey:
			params["skey"] = self.editskey

		NetworkService.request("user", self.editaction,
		                        params=params,
		                        secure=not self.editskey,
		                        successHandler=self.doLoginSuccess,
		                        failureHandler=self.doLoginFailure)

	def reset(self):
		self.loginBtn["disabled"] = False
		self.verifyBtn["disabled"] = False

		self.otp["value"] = ""
		self.username["value"] = ""
		self.password["value"] = ""

		self.edit.removeAllChildren()
		self.editskey = self.editwidget = self.editaction = None

	def enable(self):
		self.pwform.show()
		self.otpform.hide()
		self.editform.hide()

		super(UserPasswordLoginHandler, self).enable()
		DeferredCall(self.focusLaterIdiot)

	def focusLaterIdiot(self):
		self.username.focus()

	@staticmethod
	def canHandle(method, secondFactor):
		return method == "X-VIUR-AUTH-User-Password"

loginHandlerSelector.insert(0, UserPasswordLoginHandler.canHandle, UserPasswordLoginHandler)


class GoogleAccountLoginHandler(BaseLoginHandler):
	cssname = "googleaccount"

	def __init__(self, loginScreen, *args, **kwargs):
		super(GoogleAccountLoginHandler, self).__init__(loginScreen, *args, **kwargs)

		self.loginBtn = Button(translate("Login with Google"), callback=self.onLoginClick)
		self.loginBtn.addClass("vi-login-btn btn--viur")
		self.mask.appendChild(self.loginBtn)

	def onLoginClick(self, sender = None):
		self.lock()
		html5.window.location = "/vi/user/auth_googleaccount/login"

	@staticmethod
	def canHandle(method, secondFactor):
		return method == "X-VIUR-AUTH-Google-Account"

loginHandlerSelector.insert(0, GoogleAccountLoginHandler.canHandle, GoogleAccountLoginHandler)


class LoginScreen(Screen):

	def __init__(self, *args, **kwargs):
		super(LoginScreen, self).__init__(*args, **kwargs)
		self.addClass("vi-login-screen")

		self.loginMethodSelector = html5.Ul()
		self.loginMethodSelector.addClass("vi-login-method input-group bar-group--center")
		self.appendChild(self.loginMethodSelector)

		self.haveLoginHandlers = False


	def invoke(self, logout = False):
		self.show()
		self.lock()

		#Enforce logout
		if logout:
			NetworkService.request("user", "logout",
					                successHandler=self.onLogoutSuccess,
					                failureHandler=self.onLogoutSuccess,
					                secure=True)
			return

		conf["currentUser"] = None

		if not self.haveLoginHandlers:
			NetworkService.request("user", "getAuthMethods",
		                            successHandler=self.onGetAuthMethodsSuccess,
		                            failureHandler=self.onGetAuthMethodsFailure)

			return

		#Check if already logged in!
		NetworkService.request( "user", "view/self",
		                        successHandler=self.doSkipLogin,
		                        failureHandler=self.doShowLogin)

	def onLogoutSuccess(self, *args, **kwargs):
		conf["currentUser"] = None
		self.invoke()

	def doShowLogin(self, req, code, *args, **kwargs):
		self.unlock()
		self.show()
		self.selectHandler()

	def insufficientRights(self):
		self.unlock()
		self.hide()

		Alert(translate("vi.login.insufficient-rights"),
		                okLabel=translate("Login as different user"),
		                okCallback=lambda: self.invoke(logout=True))

	def doSkipLogin(self, req):
		answ = NetworkService.decode(req)
		if answ.get("action") != "view":
			self.doShowLogin()
			return

		conf["currentUser"] = answ["values"]

		if conf["vi.access.rights"]:
			if not any([x in conf["currentUser"].get("access", []) for x in conf["vi.access.rights"]]):
				self.insufficientRights()
				return
				#self.loginScreen.redirectNoAdmin()

		logging.info("User already logged in")
		conf["theApp"].admin()

	def onGetAuthMethodsSuccess(self, req):
		answ = NetworkService.decode(req)

		methods = []
		for method in answ:
			handler = loginHandlerSelector.select(method[0], method[1])
			if not handler:
				logging.warning("Login-Handler for %r with second factor %r is not known to Vi", method[0], method[1])
				continue
			# Check if this handler is already inserted!
			if not any([c.__class__.__name__ == handler.__name__ for c in self.loginMethodSelector._children]):
				handler(self)

		if len(answ)>1:
			self.loginMethodSelector.addClass("is-active")
		self.haveLoginHandlers = True
		self.invoke()

	def selectHandler(self, handler = None):
		for h in self.loginMethodSelector._children:
			if handler is None or h is handler:
				h.enable()
				handler = h
			else:
				h.disable()

	def onGetAuthMethodsFailure(self, *args, **kwargs):
		Alert(
				translate( "Fail"),
				title = translate( "error" )
				)

	def redirectNoAdmin(self):
		html5.window.location = "/"
