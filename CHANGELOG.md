# Change Log

This file documents any relevant changes done to ViUR Vi since version 2.0.0.

## 2.1

Released: Nov 2, 2017

### Major changes

- Made [ViUR logics](https://github.com/viur-framework/logics) permanently available as a Beta feature. Logics can be used for dynamic mask behaviors by providing test expressions that influence bone readonly/visibility states. Check out the [README in ViUR/logics](https://github.com/viur-framework/logics/blob/master/README.md) for more information and examples.
- Generally refactored all supported bones to provide a consistent API (``bone.serializeForPost()``, ``bone.serializeForDocument()``, and much more)
- Extended bones and modules to context-features, which allow to pass context-dependent parameters through to filters, query and add/edit actions and modify application behavior this way.
- Revised login process that allows to display custom masks (e.g. password changing dialog) within the login process.

### Minor changes

- Network communication is now entirely done on the server's vi-renderer (before it was mostly vi, but also admin)
- Full-screen view mode by clicking on the Vi-Logo
- vi-custom.js file included to allow JavaScript customizations
- ``utils.formatString()`` improved to expand selectOneBone and selectMultiBone entries into their values
- Clicking the Vi-Logo (or project logo) in the upper-left corner toggles the Pane-bar visibility on the left.
- New README.md and CHANGELOG.md

## 2.0

Released: Dec 22, 2016

### Major changes

- ViUR server 2.0.x compliance
- "id" was renamed to "key"
- Supporting of universal user module

### Minor changes

- Styling
