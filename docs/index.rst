Welcome to the example-doc documentation!
=========================================

This project serves as an example project to demonstrate
how to use the *sphinx* documentation generator for Python and provide
a template to make starting out easier.

How to prepare the template and get started
-------------------------------------------
If you do not know how to write .rst, you should have a look at a tutorial or a reference first:
`Restructured Text Reference: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_

How to set up your Table of Contents
-------------------------------------

Have a look at our starting code from the index.rst ::

    .. toctree::
       :maxdepth: 1
       :glob:
       :caption: Example

       *

This directive will tell sphinx to generate a table of contents automatically.
Right after the toctree directive we are passing three options:

* \:maxdepth\: This restricts the generator to only dive into the tree by the number of levels you configure here.
* \:glob\: This is an important option to set, in order to make the generator recursively pick up all .rst files using wildcards
* \:caption\: This sets a headline for the entire table of contents. It should probably be your project name.
* After setting the options you must leave a blank line before configuring the paths to your .rst files.
  In our case we use an asterisk, but you can specify exact paths here as well.

.. toctree::
   :maxdepth: 1
   :glob:
   :caption: Vi

   *

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`