## The Warning

This is an idea for a project and some pretty rough code.  When you
don't see this message anymore, that shall indicate that this might
acutally be useful.

## What

**docstract** parses documentation out of JavaScript source and
outputs JSON.  It is built for JavaScript, it won't ever work with
other languages.  Nor will it ever render documentation, that's your
job.

## A Tirade

Most existing documentation generators work with multiple languages,
and many generate documentation in many different formats.  The
problem with applying these tools to a language as dynamic as
JavaScript, is that they never do a great job.  Most non-trivial
JavaScript APIs include custom conventions and idioms that confuse the
snot out of your average documentation extractor.

Further the problem with documentation extractors that generate their
own human readable output (i.e. in PDF or HTML) is that there's never
any one format that will please everyone.  It may be desired to render
output in a custom format, or at least to allow multiple different
rendering frameworks.  Breaking the tasks of extraction and rendering
apart, allows for more flexibility in both phases.

**docstract** does less.  It's goal is to be as small as possible to
solve the problem of extraction: flexibly parsing human generated
in-source comments, and turning them into well structured computer
readable JSON output.

## (Desired) Features

 * command line or programmatic usage (from python)
 * (not yet) extensible to add support for custom tags
 * developer-ergonomic parsing - lets you be sloppy wherever possible.
 * (not yet) highly configurable
 * super fun unit test system.

## Example

Input:

    /**
     * My simple module that is really, really awesome.  Really.
     */
    
    /**
     * A function which can	join members of an array together with strings
     * @param {array} strings Strings to join together
     */
    exports.join = function join(strings) {
        return strings.join(",");
    };

Output:

    {
      "desc": "My simple module that is really, really awesome.  Really.",
      "filename": "my_module.js",
      "functions": [
        {
          "desc": "A function which can join members of an array together with strings",
          "name": "join",
          "params": [
            {
              "desc": "Strings to join together",
              "name": "strings",
              "type": "array"
            }
          ]
        }
      ],
      "module": "my_module"
    }

## Usage

From the command line:

    ./docstract.py myfile.js

or from a python program:

    from docstract import DocStract
    ds = DocStract()
    docsFromString = ds.extract(javascriptFileContents)
    docsFromFile = ds.extractFromFile(javascriptFileName)

## Documentation

See the tests/ directory for now.  Better docs?  Real soon now.

## Shout-Outs

[YUIDOC](http://developer.yahoo.com/yui/yuidoc/) provided inspiration and
some regular expressions that are used in docstract.

## License

Copyright (c) 2011, Lloyd Hilaiel <lloyd@hilaiel.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
