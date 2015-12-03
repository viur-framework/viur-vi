
DESCRIPTION
===========

pynetree is a simple, light-weight parsing toolkit for and written in Python.

The toolkit has been developed in the course of implementing a top-down parser supporting left-recursive grammars. Therefore, pynetree is a parser that implements a modified version of the well-known packrat parsing algorithm, but with the approach to provide true BNF-styled grammars, as known from other parsing frameworks.

The following example already defines a simple grammar and runs a parser on the input "1+2*(3+4)+5":

	from pynetree import Parser

	p = Parser({
		"factor": ["INT", "( expr )"],
		"mul": "term * factor",
		"term": ["mul", "factor"],
		"add": "expr + term",
		"expr": ["add", "term"],
		"calc$": "expr"
	})

	p.ignore(r"\s+")
	p.token("INT", r"\d+")
	p.emit(["INT", "mul", "add"])

	p.dump(p.parse("1 + 2 * (3 + 4) + 5"))


When this program is ran from a console, a proper abstract syntax tree is printed:

	add
	  add
		INT (1)
		mul
		  INT (2)
		  add
			INT (3)
			INT (4)
	  INT (5)


Grammars may also be expressed in a BNF-styled grammar definition language, including AST construction information.
The code below produces exactly the same parser with the same output as shown above.

	from pynetree import Parser
	p = Parser("""	$INT /\\d+/ %emit;
					$/\\s+/ %skip;
					f: INT | '(' e ')';
					mul: t '*' f %emit;
					t: mul | f;
					add: e '+' t %emit;
					e %goal: add | t;""")

	p.dump(p.parse("1 + 2 * (3 + 4) + 5"))


The pynetree project is currently under heavy development, so changes in the function names and syntax may occur and follow. Have fun!


FEATURES
========

The parsing toolkit so far provides

- A top-down packrat parser with support of direct and indirect left recursive grammars
- Mostly linear parsing time, even for left-recursive grammars
- Grammars can be expressed as dict objects or parsed from a BNF grammar
- Functions for abstract syntax tree (AST) definition and traversion
- Lexical analysis is performed via regular expressions (re), string or as callables

Please check out https://bitbucket.org/codepilot/pynetree to get the newest updates on pynetree.


AUTHOR
======

pynetree is developed and maintained by Jan Max Meyer, Phorward Software Technologies.

This project is one result of a several years experience in parser development systems, and is currently worked out as some kind of sub-project of a C-library called libphorward (https://bitbucket.org/codepilot/phorward), which is also developed at Phorward Software Technologies. Therefore, the BNF-styled grammar definition language of both pynetree and libphorward are similar.

Help of any kind to extend and improve or enhance this product in any kind or way is always appreciated.


LICENSING
=========

Copyright (C) 2015 by Phorward Software Technologies, Jan Max Meyer.

You may use, modify and distribute this software under the terms and conditions of the MIT license. The full license terms can be obtained from the file LICENSE.

THIS SOFTWARE IS PROVIDED BY JAN MAX MEYER (PHORWARD SOFTWARE TECHNOLOGIES) AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL JAN MAX MEYER (PHORWARD SOFTWARE TECHNOLOGIES) BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

