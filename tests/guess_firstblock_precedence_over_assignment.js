// This test checks the precedence rules of guessing functions.
// specifically the first block should be considered the module
// documentation, even when there's assignment in the code chunk
// after it.

/**
 * Allows one to control fullscreen view for the main application window
 */

var mainWin = require("window-utils");

/**
 * Size the main application window to consume the full screen
 */
exports.enable = function() {
    mainWin.activeWindow.fullScreen=true;
};

/**
 * Disable fullscreen mode (noop if it wasn't enabled)
 */
exports.disable = function() {
    mainWin.activeWindow.fullScreen=false;
};

/**
 * Toggle fullscreen.
 */
exports.toggle = function() {
    mainWin.activeWindow.fullScreen=!mainWin.activeWindow.fullScreen;
};
