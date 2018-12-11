# Changelog

This file documents any relevant changes done to ViUR Vi since version 2.

## [develop]

This is the current development version.

- Several modifications required to use new, minimized html5 library
- Allow for file preview popup also in file widget.
- Bugfix: `StringViewBoneDelegate` does not fail on `stringBone(multiple=True, language=["de", "en"])` anymore.

## [2.3] Kilauea

Release date: Oct 2, 2018

- Prints the path to the current module or entity into the address bar.
- Improvements of the List-module handler (ListHandler); Please check out
  [the corresponding wiki](https://github.com/viur-framework/vi/wiki/adminInfo-in-List-modules) entry for usage and code examples.
  - ListHandler views are now inheriting ``"icon"``, ``"columns"``,
    ``"filter"`` and ``"context"`` from the provided adminInfo, if not
	explicitly overridden.
  - ListHandler views can now be extended using the parameters ``"+name"``,
    ``"+columns"``, ``"+filter"``, ``"+context"``, ``"+actions"``, which is
	then appended or merged into their appropriate positions.
  - The parameter ``"views.request"`` can be used to additionally load views
    on demand from the server by calling a function, returning a "views"-like
	list of views configuration as in a standard adminInfo. The function is
	invoked when the user clicks on a view with appropriate position, with
	only a short delay.
  - The parameter ``"mode"`` can be set to ``"normal"`` (default), ``"hidden"``
    or ``"group"`` to let List-modules behave like Groups, where the
	underlying views provide the neccessary module functionalities.
- The ``adminInfo["sortIndex"]`` value is now ordered correctly in ascending
  order, and works as expected on all browsers.
- File selector is cached globally for a better user experience (you don't have
  to navigate to the previous location again and again and again...)
- ViUR logics integration updated and made their rendering smoother.
- Bugfix: FileWidget which wasn't recognized by moduleHandlerSelector.
- Bugfix: Reset the actionbar loading state in tree module.

## [2.2] Etna

Release date: Apr 23, 2018

- v2.2.1: Bugfix on the bones configured as ``visible=False`` feature
- Reload-button in edit masks with changes checking
- Support of the new *selectBone* feature, replacing the former *selectOneBone* and *selectMultiBone* in server
- Refactored image file preview and new image detail viewer
- Bones configured as ``visible=False`` are rendered as hidden objects now, instead of ignoring them
- Improved context editing features and editViews feature (still in beta)
  - Context-editing actions
  - New widget selector for embedded widgets
  - Evaluation of "title" and "class" attributes in editViews
- [ViUR logics](https://github.com/viur-framework/logics) v2.2 integrated
- Improved network communication module (network.py) with manual request kickoff and generic error handling
- Bugfixes
  - relatonalBone(multiple=True) loose values when unserialize() is called twice (happens under some cirumstances)
  - Counting of "And X more..." in relationalBone(multiple=True) and selectBone(multiple=True) was incorrect
  - Making AdminScreen instances re-usable with different users
  - Tooltips shall always be expandable

## [2.1]

Release date: Nov 2, 2017

- Made [ViUR logics](https://github.com/viur-framework/logics) permanently available as a Beta feature. Logics can be used for dynamic mask behaviors by providing test expressions that influence bone readonly/visibility states. Check out the [README in ViUR/logics](https://github.com/viur-framework/logics/blob/master/README.md) for more information and examples.
- Generally refactored all supported bones to provide a consistent API (``bone.serializeForPost()``, ``bone.serializeForDocument()``, and much more)
- Extended bones and modules to context-features, which allow to pass context-dependent parameters through to filters, query and add/edit actions and modify application behavior this way.
- Revised login process that allows to display custom masks (e.g. password changing dialog) within the login process.
- Network communication is now entirely done on the server's vi-renderer (before it was mostly vi, but also admin)
- Full-screen view mode by clicking on the Vi-Logo
- vi-custom.js file included to allow JavaScript customizations
- ``utils.formatString()`` improved to expand selectOneBone and selectMultiBone entries into their values
- Clicking the Vi-Logo (or project logo) in the upper-left corner toggles the Pane-bar visibility on the left.
- New README.md and CHANGELOG.md
- v2.1.1: File add button was not working

## [2.0]

Release date: Dec 22, 2016

- ViUR server 2.0.x compliance
- "id" was renamed to "key"
- Supporting of universal user module
- Styling


[develop]: https://github.com/viur-framework/vi/compare/v2.3.0...develop
[2.3]: https://github.com/viur-framework/vi/compare/v2.2.0...v2.3.0
[2.2]: https://github.com/viur-framework/vi/compare/v2.1.0...v2.2.0
[2.1]: https://github.com/viur-framework/vi/compare/v2.0.0...v2.1.0
[2.0]: https://github.com/viur-framework/vi/compare/v1.1.0...v2.0.0
