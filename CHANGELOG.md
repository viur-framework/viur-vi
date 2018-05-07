# Changelog

This file documents any relevant changes done to ViUR Vi since version 2.

## 2.2 Etna

Release date: Apr 23, 2018

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

## 2.1

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

## 2.0

Release date: Dec 22, 2016

- ViUR server 2.0.x compliance
- "id" was renamed to "key"
- Supporting of universal user module
- Styling
