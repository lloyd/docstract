#!/usr/bin/env python
#
# Copyright (c) 2011, Lloyd Hilaiel <lloyd@hilaiel.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# running this file from the command line executes its self tests.
import re
import os
import json
import sys
import difflib
import traceback
from docstract import DocStract

ds = DocStract()

# because docextractor embeds filenames into output files, let's
# change into the directory of the script for consistency
os.chdir(os.path.dirname(os.path.abspath(__file__)))

testDir = "tests"

# create a list of the tests to run (.js files in tests/ dir)
tests = []

# allow invoker on command line to pass in tests explicitly for
# selective testing
if len (sys.argv) > 1:
    for x in sys.argv[1:]:
        x = os.path.basename(x)
        tests.append(x[:-3] if x.endswith(".js") else x)
else:
    for x in os.listdir(testDir):
        if x.endswith(".js"):
            tests.append(x[:-3])

# now run!
ranTests = 0
failedTests = 0
for test in tests:
    print "Running '%s'..." % test
    failed = False
    try:
        got = ds.extractFromFile(os.path.join(testDir, test + ".js"))
    except Exception as e:
        stack = []
        l = traceback.extract_tb(sys.exc_info()[2])
        for x in l:
            stack.append([ x[2], x[3] ])
        got = { "exception_type": str(type(e)), "args": e.args, "stack": stack }
    want = None
    try:
        with open(os.path.join(testDir, test + ".out"), "r") as f:
            want = json.loads(f.read())
    except:
        pass

    gotJSON = json.dumps(got, indent=2, sort_keys=True) + "\n"

        # now let's compare actual with expected
    if want == None:
        print  "  FAILED: no expected test output file available (%s.out)" % test
        failed = True
    else:
        wantJSON = json.dumps(want, indent=2, sort_keys=True) + "\n"

        diff = difflib.unified_diff(wantJSON.splitlines(1), gotJSON.splitlines(1), "expected.out", "actual.out")

        # diff does poorly when newlines are ommitted, let's fix that
        diff = [l if len(l) > 0 and l[-1] == '\n' else l + "\n" for l in diff]
        diffText = '    '.join(diff)

        if len(diffText):
            diffText = '    ' + diffText
            print "  FAILED: actual output doesn't match expected:"
            print diffText
            failed = True
        else:
            print "  ... passed."

    if failed:
        failedTests += 1
        # write actual output to disk, so that it's easy to write new tests
        actualPath = os.path.join(testDir, test + ".outactual")
        with open(actualPath, "w+") as f:
            f.write(gotJSON)

        print "  (expected output left in '%s')" % actualPath

print "Complete, (%d/%d) tests passed..." % (len(tests) - failedTests, len(tests))
sys.exit(failedTests)
