# Changelog

This file documents any relevant changes done to ViUR Vi since version 2.

## [3.0.0-b.1] - 2021-03-08

- Switched runtime environment to [Pyodide](https://github.com/iodide-project/pyodide)
- Feature: selected multiple entities (range) in a list while holding the shift key
- Restructured the LESS/CSS tool chain
- Added ViUR Ignite LESS/CSS
- Added GULP
- Added .editorconfig
- Restructured submodules
- Removed redundant DOM elements
- Cut vi.less into several element oriented files
- vi.less serves as a catalogue file now
- LESS files are structured into different categories, reflecting the PYJS structure
- Added new ViUR icon set and support for embedded SVG icons
- Removed icon sprites
- Removed most of the old Vi CSS styling and reworked it based on classes -- following ViUR Ignite standards
- Removed most inline styling
- Added many customisable variables in configuration/_appconf.less
- Aligned all status changing CSS classes, e.g.: .is-active, .is-collapsed etc.
- Added a global .is-loading animation
- Completely reworked buttons styling and buttons customisation
- Completely reworked widgets styling based on reusable elements such as .item, .popup and .box
- Added .vi- prefix to Vi exclusive stylings
- Completely reworked bones and edit view styling based on ViUR Ignite form elements such as .input, .label, .select etc.
- Completely reworked login styling
- Completely reworked sidebar and sidebar widgets styling
- Completely reworked alert and messages styling
- Completely reworked data tables
- Added and refined many convenience features like better tooltips, larger drop areas, collapsed module list etc.
- Feature: Allow to parametrize context variable prefixes using `conf["vi.context.prefix"]`
- Feature: Handle `frontend_default_visible`-parameter for bones also in Hierarchy handler
- Feature: Improved structuring of `TreeNodeWidget` and `TreeLeafWidget` for trees
- Feature: Allow for multiple uploads in File.upload action
- Bugfix: Tree `edit`-action should not both edit and switch parent node

## [2.5.0] Vesuv

Release date: Jul 26, 2019

- Feature: Support for new recordBone()
- Bugfix: Improved `textBone.unserialize()` and change-event behavior 
- Bugfix: Widget for `stringBone(multiple=True)` is now cleared on unserialization
- Bugfix: Added missing `serializeForDocument()` to spatialBone
- Bugfix: SelectMultiBoneExtractor.render() works now correctly for `selectBone(multiple=True)`
- Bugfix: Disallow applying SelectFieldsPopup with empty selection (#27)
- Bugfix: Selection in SelectTable works now correctly
- Bugfix: On server version mismatch, allow to continue anyway

## [2.4.1] Agung

Release date: May 24, 2019

- Bugfix: logics 2.4.1 with fixed unary operators
- Bugfix: Order of path items in file module, stop path recognition when key is referenced as parentkey
- Bugfix: Updated icons submodule

## [2.4.0] Agung

Release date: May 17, 2019

- Bugfix: Setting a dateBone empty serialized into a zero-time value, althought the dateBone was configured with time=False.
- Bugfix: `StringViewBoneDelegate` does not fail on `stringBone(multiple=True, language=["de", "en"])` anymore.
- Bugfix: Improved image popup viewer not falling apart when image dimensions are not quadratic.
- Bugfix: Fixed multiple typos, docstring, missing encoding strings.
- Feature: Added the [summernote WYSIWYG editor](https://summernote.org/) as replacement for textBone() editing. 
- Feature: Allow for file preview popup also in file widget.
- Feature: Errors in EditWidget are dumped to the message center also for better recognition when something went wrong.
- Feature: Selected multiple entities (range) in a list while holding the shift key.
- Feature: Improved handling of key-events.
- Feature: Several modifications required to use new, minimized html5 library.
- Feature: Added the possibility to manipulate params via a global function.
- Feature: Improved handling of represented URL in address bar.
- Feature: Lazy-loading of GroupPanes during user navigation for a faster UI experience.
- Removed: Preview Widget (was not used anymore).

## [2.3.0] Kilauea

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
- Bugfix: FileWidget which wasn't recognized by moduleWidgetSelector.
- Bugfix: Reset the actionbar loading state in tree module.

## [2.2.0] Etna

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

## [2.1.0]

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

## [2.0.0]

Release date: Dec 22, 2016

- ViUR server 2.0.x compliance
- "id" was renamed to "key"
- Supporting of universal user module
- Styling


[3.0.0-b.1]: https://github.com/viur-framework/vi/compare/v2.5.0...v3.0.0
[2.5.0]: https://github.com/viur-framework/vi/compare/v2.4.1...v2.5.0
[2.4.1]: https://github.com/viur-framework/vi/compare/v2.4.0...v2.4.1
[2.4.0]: https://github.com/viur-framework/vi/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/viur-framework/vi/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/viur-framework/vi/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/viur-framework/vi/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/viur-framework/vi/compare/v1.1.0...v2.0.0
