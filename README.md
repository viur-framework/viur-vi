# DESCRIPTION #

Vi is the web-based administration tool for ViUR-based appliances.
To get Vi run, it has to be built in your projects appengine folder.

The conceptional best approach is to add the vi build-directory as a submodule
to your repository, and build it within this directory for your ViUR-based
Google App Engine appliance.

# DEPENDENCIES #

Vi is a HTML5-based web-application implemented on top of the PyJS framework.

Therefore, a PyJS build-environment must exist. To build all related files,
there is also a compiler for the LESS overlay language required (lessc).

# BUILDING #

Vi comes with a simple Makefile run by GNU make to get the compilation tasks
and dependencies done.

By default, Vi is built into a directory called "vi" within the source root directory. In an advanced setup (project based setup), Vi can also be built into the folder ../appengine/vi, up one level of the working directory, which makes Vi suitable as a submodule of a ViUR appliance for the Google App Engine.

After checking out Vi, simply move into the working directory and type:

	make setup
	make

To get all basic setup steps done.

# ADDITIONAL TARGETS #

To clean the Vi output folder, run

	make clean

To build an optimized version without debugging output, type

	make deploy

Have fun! :)

