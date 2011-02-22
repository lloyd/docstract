// __defineGetter__ / __defineSetter__ suggests a property, name is first
// arg to function.

  /**
   * True iff the stream is closed.
   */
stream.__defineGetter__("closed", function stream_closed() {
    return !self.opened;
});

  /**
   * True iff the stream is open.
   */
stream.__defineSetter__('opened', function(x) {
    self.opened = x;
});
