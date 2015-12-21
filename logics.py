#-*- coding: utf-8 -*-
"""
Implements the tiny dependency check language "viurLogic" that can be compiled
into JavaScript or directly executed within an interpreter. It is entirely
written in pure Python.
"""

from pynetree import Parser

class viurLogicsParser(Parser):

	def __init__(self):
		super(viurLogicsParser, self).__init__(
			"""
			$			/\\s+|#.*\n/											%skip;
			$NAME		/[A-Za-z_][A-Za-z0-9_]*/ 								%emit;
			$STRING 	/"[^"]*"|'[^']*'/ 										%emit;
			$NUMBER 	/[0-9]+\.[0-9]*|[0-9]*\.[0-9]+|[0-9]+/ 					%emit;

			test %goal	: if_else
						| or_test                            					%emit
						;

			if_else     : or_test 'if' or_test 'else' test   					%emit;

			or_test		: and_test ('or' and_test)+ 							%emit
						| and_test
						;

			and_test	: not_test ('and' not_test)+ 							%emit
						| not_test
						;

			not_test	: 'not' not_test 										%emit
						| comparison
						;
			comparison	: expr (("<" | ">" | "==" | ">=" | "<=" |
									"<>" | "!=" | "in" | not_in |
										"is" | is_not) expr)+ 					%emit
						| expr
						;

			not_in		: 'not' 'in' 											%emit;
			is_not		: 'is' 'not' 											%emit;

			expr		: add | sub | term;
			add			: expr '+' term 										%emit;
			sub			: expr '-' term 										%emit;

			term		: mul | div | mod | idiv | factor;
			mul			: term '*' factor										%emit;
			div			: term '/' factor										%emit;
			mod			: term '%' factor										%emit;
			idiv		: term '//' factor										%emit;

			factor		: ("+"|"-"|"~") factor									%emit
						| power
						;
			power		: atom "**" factor 										%emit
						| atom
						;

			atom		: NUMBER | strings | NAME | '(' test ')';
			strings		: STRING+												%emit;
			""")

	def traverse(self, ast):
		"""
		A modified version of the AST traversal function.
		"""

		if not ast:
			return

		if isinstance(ast, tuple):
			if isinstance(ast[1], list) or isinstance(ast[1], tuple):
				self.traverse(ast[1])

			nname = ast[0][0] if isinstance(ast[0], tuple) else ast[0]

			if nname in dir(self) and callable(getattr(self, nname)):
				getattr(self, nname)(ast)

		else:
			for i in ast:
				self.traverse(i)


class viurLogicsJS(viurLogicsParser):
	"""
	Compiler to turn viurLogics into JavaScript code.
	"""
	stack = None

	def compile(self, src, fields = None):
		self.stack = []

		t = self.parse(src)
		#self.dump(t)
		self.traverse(t)

		return self.stack.pop()

	def test(self, node):
		self.stack.append("(%s)" % self.stack.pop())

	def if_else(self, node):
		alt = self.stack.pop()
		expr = self.stack.pop()
		res = self.stack.pop()

		self.stack.append("%s ? %s : %s" % (expr, res, alt))

	def or_test(self, node):
		for i in range(1, len(node[1]), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append("%s || %s" % (l, r))

	def and_test(self, node):
		for i in range(1, len(node[1]), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append("%s && %s" % (l, r))

	def not_test(self, node):
		self.stack.append("!%s" % self.stack.pop())

	def comparison(self, node):
		for i in range(1, len(node[1]), 2):
			op = node[1][i][0]
			r = self.stack.pop()
			l = self.stack.pop()

			if op == "in":
				pass #todo
				#self.stack.append(l in r)
			elif op == "not_in":
				pass #todo
				#self.stack.append(l not in r)
			elif op == "is":
				pass #todo
				#self.stack.append(l is r)
			elif op == "is_not":
				pass #todo
				#self.stack.append(l is not r)
			else:
				if op == "<>":
					op = "!="

				self.stack.append("%s %s %s" % (l, op, r))

	def add(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s + %s" % (l, r))

	def sub(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s - %s" % (l, r))

	def mul(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s * %s" % (l, r))

	def div(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s / %s" % (l, r))

	def idiv(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s // %s" % (l, r)) #todo

	def mod(self, node):
		r = self.stack.pop()
		l = self.stack.pop()
		self.stack.append("%s %% %s" % (l, r))

	def factor(self, node):
		op = self.stack.pop()

		if isinstance(op, (str, unicode)):
			self.stack.append(op)
		elif node[1][0][0] == "+":
			self.stack.append(+op)
		elif node[1][0][0] == "-":
			self.stack.append(-op)
		else:
			self.stack.append(~op)

	def NAME(self, node):
		if node[1] in ["True", "False"]:
			self.stack.append(node[1].lower())
		else:
			self.stack.append("getfield(\"%s\")" % node[1])

	def STRING(self, node):
		self.stack.append("\"%s\"" % node[1][1:-1])

	def strings(self, node):
		s = ""
		for i in range(len(node[1])):
			s = str(self.stack.pop()[1:-1]) + s

		self.stack.append("\"%s\"" % s)

	def NUMBER(self, node):
		if "." in node[1]:
			self.stack.append(float(node[1]))
		else:
			self.stack.append(int(node[1]))


class viurLogicsExecutor(viurLogicsParser):
	"""
	Interpreter class for the viurLogics.
	"""

	def __init__(self):
		super(viurLogicsExecutor, self).__init__()
		self.stack = []
		self.fields = {}

	def getOperands(self, onlyNumeric = True):
		r = self.stack.pop()
		l = self.stack.pop()

		if isinstance(l, str) or isinstance(r, str):
			if onlyNumeric:
				try:
					l = float(l)
				except:
					l = 0

				try:
					r = float(r)
				except:
					r = 0
			else:
				l = str(l)
				r = str(r)

		return l, r

	def execute(self, src, fields = None):
		if self.stack:
			self.stack = []

		if isinstance(fields, dict):
			self.fields = fields

		t = self.parse(src)
		#vil.dump(t)
		self.traverse(t)

		return self.stack.pop()

	def or_test(self, node):
		for i in range(1, len(node[1]), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l or r)

	def and_test(self, node):
		for i in range(1, len(node[1]), 2):
			r = self.stack.pop()
			l = self.stack.pop()
			self.stack.append(l and r)

	def not_test(self, node):
		self.stack.append(not self.stack.pop())

	def comparison(self, node):
		for i in range(1, len(node[1]), 2):
			op = node[1][i][0]
			r = self.stack.pop()
			l = self.stack.pop()

			if op == "<":
				self.stack.append(l < r)
			elif op == ">":
				self.stack.append(l > r)
			elif op == "==":
				self.stack.append(l == r)
			elif op == ">=":
				self.stack.append(l >= r)
			elif op == "<=":
				self.stack.append(l <= r)
			elif op == "<>" or op == "!=":
				self.stack.append(l != r)
			elif op == "in":
				self.stack.append(l in r)
			elif op == "not_in":
				self.stack.append(l not in r)
			elif op == "is":
				self.stack.append(l is r)
			elif op == "is_not":
				self.stack.append(l is not r)


	def add(self, node):
		l, r = self.getOperands(False)
		self.stack.append(l + r)

	def sub(self, node):
		l, r = self.getOperands()
		self.stack.append(l - r)

	def mul(self, node):
		l, r = self.getOperands(False)
		if (isinstance(l, (str, unicode))
			and isinstance(r, (str, unicode))):
			l = 0

		self.stack.append(l * r)

	def div(self, node):
		l, r = self.getOperands()
		self.stack.append(l / r)

	def idiv(self, node):
		l, r = self.getOperands()
		self.stack.append(l // r)

	def mod(self, node):
		l, r = self.getOperands()
		self.stack.append(l % r)

	def factor(self, node):
		op = self.stack.pop()

		if isinstance(op, (str, unicode)):
			self.stack.append(op)
		elif node[1][0][0] == "+":
			self.stack.append(+op)
		elif node[1][0][0] == "-":
			self.stack.append(-op)
		else:
			self.stack.append(~op)

	def NAME(self, node):
		if node[1] in ["True", "False"]:
			self.stack.append(True if node[1] == "True" else False)
		else:
			self.stack.append(self.fields.get(node[1], ""))

	def STRING(self, node):
		self.stack.append(node[1][1:-1])

	def strings(self, node):
		s = ""
		for i in range(len(node[1])):
			s = str(self.stack.pop()) + s

		self.stack.append(s)

	def NUMBER(self, node):
		if "." in node[1]:
			self.stack.append(float(node[1]))
		else:
			self.stack.append(int(node[1]))


if __name__ == "__main__":
	#vile = viurLogicsExecutor()
	#print(vile.execute("2 + 2 * 3 + (5.3 + 'hello' 'world')"))

	viljs = viurLogicsJS()
	print(viljs.compile("a if 1 and (2 or 3) else b == \"neun\""))
