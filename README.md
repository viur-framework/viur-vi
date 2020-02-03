# ViUR Vi

**WARNING: THIS IS AN UNSTABLE PYTHON3 / PYODIDE PORT, WORK IN PROGRESS!**

**Vi** is a web-based administration client for the [ViUR framework](https://www.viur.dev).

This is the current development version 3.0 of the Vi which aims to be running both with [ViUR 2](https://github.com/viur-framework/server) and [ViUR 3](https://github.com/viur-framework/viur-core). 

This program is now entirely established on [Pyodide](https://github.com/iodide-project/pyodide), the official Python 3.7 interpreter compiled to WebAssembly. Therefore it is necessary to "install" Pyodide as described below.

## Usage

Vi can be used as a submodule (see https://github.com/viur-framework/viur-base for an example) to be included into a ViUR project. 

After cloning or extracting Vi, run

```bash
get-pyodide.py
```

to download and install the latest Pyodide version as WebAssembly runtime environment.

When you add or remove any files from the Vi repo, don't forget to call

```bash
gen-files-json.py
```

to rebuild the file `files.json` which is used to pre-fetch the Vi into Pyodide. Latter one is also necessary when writing Vi-Plugins. See viur-base for a detailed and pre-configured setup.

## Contributing

We take a great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your visions or questions with us and participate in ongoing discussions.

- [ViUR](https://www.viur.dev)
- [#ViUR on freenode IRC](https://webchat.freenode.net/?channels=viur)
- [ViUR on GitHub](https://github.com/viur-framework)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

Copyright (C) 2012-2020 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the GNU Lesser General Public License (LGPL). See the file LICENSE provided within this package for more information.
