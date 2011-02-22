// assignment to an object property should be name-guessable, this test
// has two examples.

  /**
   * Closes both the stream and its backing stream.  If the stream is already
   * closed, an exception is thrown.  For TextWriters, this first flushes the
   * backing stream's buffer.
   */
  stream.close = function stream_close() {
    self.ensureOpened();
    self.unload();
  };

  /**
   * Writes a string to the stream.  If the stream is closed, an exception is
   * thrown.
   *
   * @param str
   *        The string to write.
   */
  this.write = function TextWriter_write(str) {
    manager.ensureOpened();
    let istream = uconv.convertToInputStream(str);
    let len = istream.available();
    while (len > 0) {
      stream.writeFrom(istream, len);
      len = istream.available();
    }
    istream.close();
  };
