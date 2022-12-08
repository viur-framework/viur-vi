# Changelog

This file documents any relevant changes done to ViUR Vi since version 2.

## [3.0.29]- 2022-11-23

- Updated Flare
- Show an appropiate error message in case no login method is implemented
- Fixed login with OTP as second factor (#132)
- Fixing access right checks of some actions, clone only when add-right is set

## [3.0.28]- 2022-11-17

- Fixing rootnode selector (#130)
- Parametrizable scriptor URL
- Display custom preview name on preview button

## [3.0.27] - 2022-11-10
- Fixing hierarchy.add
- customActions
  - several fixes
  - with "success"-info & "then"-action
  - Use NiceError functionality
- Fixing "?" location href reload
- Updating Flare to latest version

## [3.0.26] - 2022-10-21
- Fix: Removing -m build option to fix #121

## [3.0.25] - 2022-10-04
- Fix: Improving context support for TreeWidget

## [3.0.24] - 2022-10-04
- Fix: Updated Flare to fix RawViewWidget

## [3.0.23] - 2022-09-28
- Fix: Select image/file function in Summernote WYSIWYG-editor for TextBones fixed 

## [3.0.22] - 2022-06-03
- Feat: added params to customAction view call

## [3.0.21] - 2022-05-25
- Feat: added grouped skels
- Fix: viewactions now not merged by default, customActions now can be defined in a view
- Fix: Handler for add.node action in tree widgets
- Fix: HierarchyWidget getAction() returning "add"-action twice
- Fix: Flare update for performance and security reasons
- Fix: EditWidget accepts skel for unserialization again

## [3.0.20] - 2022-04-14
- Fix: Corrected version number
- Fix: Updated README
- Fix: Updated .gitattributes

## [3.0.19] - 2022-04-14
- Fix: Group parameter handling
- Fix: Flare update to fix various TreeWidget issues
- Fix: TreeWidget improvements and fixes causing double node listing

## [3.0.18] - 2022-04-07
- Fix: summernote re-added missing styles

## [3.0.17] - 2022-04-07
- Fix: summernote re-added missing styles
- Feat: serversideactions can now trigger a confirm popup
- Feat: navigation and main-view can now reloaded
- Fix: added a hierarchy specific add button

## [3.0.16] - 2022-03-23
- Fix: searchfilter now behaved as it should for relationalbones

## [3.0.15] - 2022-03-22
- Fix: Foldernavigation in fileBones working again
- Fix: Selection for filtered lists remains 

## [3.0.14] - 2022-03-22
- Feat: added Azure login
- Fix: admininfo actions can now start with "\n"

## [3.0.13] - 2022-03-14

- Fix: submodule vi working again
- Fix: formcontrols working again

## [3.0.12] - 2022-03-11

- Fix: zipped releases now working again

## [3.0.11] - 2022-03-07

- Fix: Flare update
- Fix: editViews now work again
- Feat: often used icons are loaded on start
- Feat: Vi and Core Version now shown in Topbar
- Fix: Embeding Images in Summernote is now disabled

## [3.0.10] - 2022-01-14
- Fix: Flare update
- Fix: Edit Form update
- Fix: Ignite update
- Fix: Messages fix

## [3.0.9] - 2021-12-16
- Feat: EditWidget with improved error reporting in ViurForm
- Feat: Styling and icons updated
- Fix: EditWidget speed increasement due bug with accordion rendering

## [3.0.8] - 2021-12-03
- Feat: modules now can have display:open
- Feat: Updated to Flare 1.0.8 with new form classes
- Feat: Rewrote EditWidget to work as a container for a Flare `ViurForm`, re-enabling conditional field behaviors
- Fix: Renamed several imports from Flare 1.0.8

## [3.0.7] - 2021-11-10
- Feat: updated to Flare 1.0.8
- Fix: EvalFormatStrings now work properly again

## [3.0.6] - 2021-09-30
- Feat: updated to Flare 1.0.7
- Fix: RelationalBones and RecordBone now work again as expected

## [3.0.5] - 2021-09-29
- Feat: updated to Flare 1.0.6
- Fix: Texteditor now available in relationalbones and recordbones
- Feat: the modulepipe is now disabled, but can be configured

## [3.0.4] - 2021-09-21
- Feat: added Icon Caching
- Feat: added SyncHandler
- Feat: hash getter und setter can now accept parameters
- Feat: direct FileUpload is now possible, use `"widget":"direct"` as parameter
- Feat: Update get-pyodide.py with configurable Version
- Fix: File and Folder names are displayed again
- Fix: Multiple SelectBones can be set to ReadOnly again

## [3.0.3] - 2021-08-20
- Fix: updated relational style

## [3.0.2] - 2021-08-20
- Fix: edit widget for relational bone didn't work properly due unclosed <div>-tag

## [3.0.1] - 2021-08-19
- Fix: webworker now supported
- Feat: added some build options (develop, zip, pyc, min)

## [3.0.0] - 2021-08-13
- Fix: deleting entries from a list works again
- Feat(**BREAKING**): uses pyodide 0.18
- Feat: new buildscripts
- Feat: new topbar action scripter

## [3.0.0-rc.7] - 2021-07-23
- Fix: File upload now works again.

## [3.0.0-rc.6] - 2021-07-21
- Fix: modulesGoups now useable again
- Updated: Flare

## [3.0.0-rc.5] - 2021-07-02
- Fix: File upload now works again.

## [3.0.0-rc.4] - 2021-07-01
- Fix: last 50 log entries are now stored in indexedDB again 
- Feature: new Version handling.

## [3.0.0-rc.3] - 2021-06-30
- Fix: tree selection works again, multi-selection only allowed in browser-trees
- Fix: file actions works again

## [3.0.0-rc.2] - 2021-06-30
- Fix: tree edit action works again
- docu: updated urllib3

## [3.0.0-rc.1] - 2021-06-24
- Feature(**BREAKING**): formatStrings now safeEval expressions
- removed(**BREAKING**): AdminInfo options `disabledFunctions`, `rootNodeOf`, `extendedFilters`, `visibleName`, `checkboxSelction`, `indexes`, `entryActions`, `disableInternalPreview`, `hideInMainBar`
- added(**BREAKING**): AdminInfo options `display`, `moduleGroup`, `changeInvalidates`, `disabledActions`
- changed(**BREAKING**): AdminInfo option `actions` now by default left oriented. user `|` at the beginning and end to center actions

## [3.0.0-b.10] - 2021-04-22

- Security: Formatstring won't be unescaped anymore.

## [3.0.0-b.9] - 2021-04-21

- Feature: Tree handler now can use shift-click multiselection
- Fix: reworked upload process
- Fix: reworked file and folder delete action
- Fix: lists are now reloaded correctly when they are dettached 

## [3.0.0-b.8] - 2021-04-15

- Feature: Lists are now lazy loading again
- Feature: added `adminInfo[mode]`
- Feature: added +filter, +columns etc...

- fix for missing modulgroup configuration

## [3.0.0-b.7] - 2021-04-13

- fix for missing modulgroup configuration

## [3.0.0-b.6] - 2021-04-08

- fix for ISO-Dates in views
- fix updated files.json

## [3.0.0-b.5] - 2021-04-07

- added support for ISO-Dates

## [3.0.0-b.4] - 2021-03-26

- flare svg icon base path is now "flare.icon.svg.embedding.path"
- icon rendering changed.

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
