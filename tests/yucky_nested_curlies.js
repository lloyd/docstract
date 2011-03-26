/**
 * @class Request
 * The `Request` object is used to make `GET` or `POST` network requests. It is
 * constructed with a URL to which the request is sent. Optionally the user may
 * specify a collection of headers and content to send alongside the request and
 * a callback which will be executed once the request completes.
 *
 * Once a `Request` object has been created a `GET` request can be executed by
 * calling its `get()` method, or a `POST` request by calling its `post()` method.
 *
 * When the server completes the request, the `Request` object emits a "complete"
 * event.  Registered event listeners are passed a `Response` object.
 *
 * Each `Request` object is designed to be used once. Once `GET` or `POST` are
 * called, attempting to call either will throw an error.
 *
 * Since the request is not being made by any particular website, requests made
 * here are not subject to the same-domain restriction that requests made in web
 * pages are subject to.
 *
 * With the exception of `response`, all of a `Request` object's properties
 * correspond with the options in the constructor. Each can be set by simply
 * performing an assignment. However, keep in mind that the same validation rules
 * that apply to `options` in the constructor will apply during assignment. Thus,
 * each can throw if given an invalid value.
 *
 * The example below shows how to use Request to get the most recent public tweet.
 *
 *     var Request = require('request').Request;
 *     var latestTweetRequest = Request({
 *       url: "http://api.twitter.com/1/statuses/public_timeline.json",
 *       onComplete: function (response) {
 *         var tweet = response.json[0];
 *         console.log("User: " + tweet.user.screen_name);
 *         console.log("Tweet: " + tweet.text);
 *       }
 *     });
 *
 *     // Be a good consumer and check for rate limiting before doing more.
 *     Request({
 *       url: "http://api.twitter.com/1/account/rate_limit_status.json",
 *       onComplete: function (response) {
 *         if (response.json.remaining_hits) {
 *           latestTweetRequest.get();
 *         } else {
 *           console.log("You have been rate limited!");
 *         }
 *       }
 *     }).get();
 * @endclass
 */

