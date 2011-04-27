// docstract supports a somewhat generic notion of "events".  These may
// be associated with a class or the top level file.  An event has a
// name, description, and payload.  That's it.

/** @class EventEmittingClass */

/**
 * @event progress
 * Allows the listener to understand approximately how much of the
 * page has loaded.
 * @payload {number} The percentage (0..100) of page load that is complete
 */
this.eventEmitter._emit("progress", curProgress);

/**
 * @event foo
 * A foo event, duh.
 * @payload {string} A string with lotsa foo inside!
 */
this.eventEmitter._emit("foo", bar);

/** @endclass */
