# -*- coding: utf-8 -*-
import os,json,logging,re

'''

'''

def html5Object(name):
	obj=""
	if name:
		camelname=name[0].upper()+name[1:]

		classdef='class '+camelname+'( Widget ):\n\t_baseClass = "'+name+'"\n\n'
		initdef = '\tdef __init__(self,*args,**kwargs):\n\t\tsuper('+camelname+",self).__init__(*args,**kwargs)\n\n"
		obj = classdef+initdef
	return obj




htm5objectlist=[
	"abbr",
	"address",
	"article",
	"aside",
	"b",
	"bdi",
	"br",
	"caption",
	"cite",
	"code",
	"datalist",
	"dfn",
	"em",
	"figcaption",
	"figure",
	"footer",
	"header",
	"h1",
	"h2",
	"h3",
	"h4",
	"h5",
	"h6",
	"hr",
	"i",
	"kdb",
	"legend",
	"mark",
	"noscript",
	"p",
	"rq",
	"rt",
	"ruby",
	"s",
	"samp",
	"section",
	"small",
	"strong",
	"sub",
	"summery",
	"sup",
	"u",
	"var",
	"wbr"


]






def main():
	##Clean file
	##Write html5.py

	html5py = open("elements.py","r+")
	html5py.truncate()
	html5py.write("from html5.widget import Widget\n\n")
	for html5objname in htm5objectlist:
		html5py.write(html5Object(html5objname))
	html5py.close()


	##init.py
	initpy = open("__init__.py","r+")
	newfile = "";
	for line in initpy:
		if line.find("from html5.elements")==-1:
			newfile+=line
	initpy.close()
	initpy = open("__init__.py","w").close() ##delete whole content in __init__.py
	initpy = open("__init__.py","r+")
	initpy.write(newfile)
	initpy.close()

	initpy = open("__init__.py","a")

	imports = ','.join(x.capitalize() for x in htm5objectlist)

	initpy.write("from html5.elements import "+imports)
	initpy.close()



if __name__ == '__main__':
	main()