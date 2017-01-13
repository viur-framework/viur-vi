This software is a part of the ViUR® Information System.
ViUR® is a free software development framework for the Google App Engine™.
More about ViUR can be found at http://www.viur.is/.

DESCRIPTION
===========
The **vi** is a web-based administration tool for ViUR-based applications.

This software is a platform-independent HTML5-web-app that is written in
Python and must be compiled to JavaScript using the PyJS (http://pyjs.org)
toolchain.

It was tested and runs very well with the latest versions of

- Google Chrome
- Apple Safari
- Mozilla Firefox
- Microsoft Internet Explorer >= 9

Pre-compiled and packaged versions can be obtained on the official ViUR
website at http://www.viur.is/.

INSTALLATION
============
The compiled web-app has to be put in a directory "vi" within the ViUR
application directory. The name of the directory can diverge when expressed
into the application's `app.yaml` file also.

Please refer to the ViUR documentation (http://docs.viur.is) to get more
information.

DEPENDENCIES
============
This software is implemented on top of the PyJS framework and uses the
**html5** library which is also part of the ViUR open source project.

- The **html5** library can be found at https://bitbucket.org/viur/html5
- **pyjs** can be obtained from https://github.com/pyjs/pyjs
- **lessc** is required to build securely (http://lesscss.org)

Therefore, a PyJS build-environment has to be configured meeting the above
dependencies.

BUILDING
========
This repository contains a simple Makefile for GNU make to get all compilation
tasks and dependencies done.

By default, it builds into a directory called ``vi`` within the source root
directory. In an advanced setup (project based setup), it builds into the
folder ``../appengine/vi``, up one level of the working directory, which makes
it suitable to use this repository as a submodule of an entire application's
source repository.

After checking out vi, simply move into the working directory and type:

	make

to create a deploy-able and speed-optimized version, run

	make deploy

to remove all generated files and rebuild from scratch, type

	make clean

WHO CREATES VIUR?
=================

ViUR is developed and maintained by Mausbrand Informationssysteme GmbH,
from Dortmund, Germany.

We are a software company consisting of young, enthusiastic software
developers, designers and social media experts, working on exciting
projects for different kinds of customers. All of our newer projects are
implemented with ViUR, from tiny web-pages to huge company intranets with
hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or
way is always appreciated.

LICENSING
=========

Copyright (C) 2012-2017 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of
Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and
conditions of the GNU Lesser General Public License (LGPL).

See the file LICENSE provided in this package for more information.
