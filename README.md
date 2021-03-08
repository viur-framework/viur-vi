[![release](https://github.com/viur-framework/viur-vi/actions/workflows/main.yml/badge.svg)](https://github.com/viur-framework/viur-vi/actions/workflows/main.yml)

# ViUR Vi

This is the web-based administration client for the [ViUR framework](https://www.viur.dev).

This program is entirely built using [Pyodide](https://github.com/iodide-project/pyodide), a Python 3.7 interpreter compiled to WebAssembly and entirely running in the browser.

## Usage

Vi can be used as a submodule (see https://github.com/viur-framework/viur-base for an example) to be included into a ViUR project. 

## Development

When you add or remove any files from the Vi repo, don't forget to call

```bash
gen-files-json.py
```

to rebuild the file `files.json` which is used to pre-fetch the Vi into Pyodide. This is also necessary when writing Vi-Plugins. See viur-base for a detailed and pre-configured setup.

## Contributing

We take great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your vision or questions with us and participate in ongoing discussions.

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
