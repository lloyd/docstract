// a function which accepts arguments embedded inside an object

/**
 * @function foo
 *
 * This function ... blah blah blah
 *
 * @param options {object
 *
 *   @prop url {string}
 *   This is the url to which the request will be made.
 *
 *   @prop [onComplete] {function}
 *
 *   This function will be called when the request has received a response (or in
 *   terms of XHR, when `readyState == 4`). The function is passed a `Response`
 *   object.
 *
 *   @prop [headers] {object}
 *   An unordered collection of name/value pairs representing headers to send
 *   with the request.
 *
 *   @prop [content] {string,object}
 *
 *   The content to send to the server. If `content` is a string, it
 *   should be URL-encoded (use `encodeURIComponent`). If `content` is
 *   an object, it should be a collection of name/value pairs. Nested
 *   objects & arrays should encode safely.
 *
 *   For `GET` requests, the query string (`content`) will be appended
 *   to the URL. For `POST` requests, the query string will be sent as
 *   the body of the request.
 *
 *   @prop [contentType] {string}
 *
 *   The type of content to send to the server. This explicitly sets the
 *   `Content-Type` header. The default value is `application/x-www-form-urlencoded`.
 * }
 */
