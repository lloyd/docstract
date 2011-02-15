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

import re
import os

class DocStract():
    def __init__(self):
        # the pattern for extracting a documentation block and the next line
        self.docBlockPat = re.compile('(/\*\*)(.*?)(\*/)([\s\n]*[^\/\n]*)?', re.S)

        # after extracting the comment, fix it up (remove *s and leading spaces)
        self.blockFilterPat = re.compile('^\s*\* ?', re.M)

        # the pattern used to split a comment block to create our token stream
        # this will currently break if there are ampersands in the comments if there
        # is a space before it
        self.tokenizePat = re.compile('^\s?(@\w+)', re.M);

        # parse a function/module/class:
        # @function [name]
        # [description]
        self.functionPat = re.compile('^(\w+)$|^(?:([\w.\[\]]+)\s*\n)?\s*(.*)$', re.S);

        # parse properties or params.
        # We support three forms:
        #   @property <name> <{type}> [description]
        #   @property <{type}> <name> [description]
        #   @property [name]
        #   [description]
        self.propPat =  re.compile(
            '(?:^([\w.\[\]]+)\s*(?:{(\w+)})\s*(.*)$)|' +
            '(?:^{(\w+)}\s*([\w.\[\]]+)\s*(.*)$)|' +
            '(?:^([\w.\[\]]+)?\s*(.*)$)',
            re.S);

        # heuristic type and name guessing stuff, applied to the first non-whitespace
        # line after the doc block.  designed for commonjs modules (note the 'exports').
        self.findExportsPat = re.compile('(?:^|\s)exports\.(\w+)\s', re.M);

        # tags that are allowed inside documentation blocks.
        self.classMarker = "@class"
        self.classEndMarker = "@endclass"
        self.constructorMarker = "@constructor"
        self.functionMarker = "@function"
        self.moduleMarker = "@module"
        self.propertyMarker = "@property"

        # block types.  Each document block is of one of these types.
        # XXX: this should become an array of classes, like self.tags 
        self.blockTypes = (
            self.classMarker,
            self.classEndMarker,
            self.constructorMarker,
            self.functionMarker,
            self.moduleMarker,
            self.propertyMarker
            )

        # tag aliases, direct equivalences.  Note, RHS is normal form.
        self.aliases = {
            '@func': '@function',
            '@params': '@param',
            '@parameter': '@param',
            '@parameters': '@param',
            '@returns': '@return',
            '@description': '@desc',
            '@seealso': '@see',
            '@see_also': '@see'
            }

        # lookup table of tag handlers, lil' object that can parse and inject
        # for different tags.
        self.tags = {
            '@param':  self.ParamTagHandler('@param'),
            '@desc':   self.DescTagHandler('@desc'),
            '@return': self.ReturnTagHandler('@return'),
            '@see':    self.SeeTagHandler('@see'),
            '@throws': self.ThrowsTagHandler('@throws'),
            '@type':   self.TypeTagHandler('@type'),
            }

        # a little bit of context that allows us to understand when we're parsing classes
        # XXX: we could make this an array and a couple code tweaks if we cared
        # about nested classes at some point
        self._currentClass = None

    def _isMarker(self, tok):
        return tok in self.blockTypes or tok in self.tags or tok in self.aliases

    def _popNonMarker(self, toks):
        nxt = None
        if (len(toks) == 0):
            return None
        if not self._isMarker(self._peekTok(toks)):
            nxt = toks.pop(0)
        return nxt

    def _peekTok(self, toks):
        if (len(toks)):
            return toks[0]
        return None

    def _consumeToks(self, tokens, currentObj, data):
        cur = tokens.pop(0)

        if cur == self.moduleMarker:
            currentObj["type"] = 'module'
            nxt = self._popNonMarker(tokens)
            if nxt:
                # nxt describes the module
                m = self.functionPat.match(nxt)
                if not m:
                    raise RuntimeError("Malformed args to %s: %s" %
                                       (self.moduleMarker, (cur[:20] + "...")))
                if m.group(1):
                    currentObj["name"] = m.group(1)
                else:
                    if m.group(2):
                        currentObj["name"] = m.group(2)
                    if m.group(3):
                        if 'desc' in currentObj:
                            currentObj['desc'] = currentObj['desc'] + "\n\n" + m.group(3)
                        else:
                            currentObj['desc'] = m.group(3)
            else:
                # in this case we'll have to guess the function name
                pass

        elif cur == self.classMarker:
            currentObj["type"] = 'classstart'
            nxt = self._popNonMarker(tokens)
            if nxt:
                # nxt describes the module
                m = self.functionPat.match(nxt)
                if not m:
                    raise RuntimeError("Malformed args to %s: %s" %
                                       (self.classMarker, (cur[:20] + "...")))
                if m.group(1):
                    currentObj["name"] = m.group(1)
                else:
                    if m.group(2):
                        currentObj["name"] = m.group(2)
                    else:
                        raise RuntimeError("A class must have a name")

                    if m.group(3):
                        if 'desc' in currentObj:
                            currentObj['desc'] = currentObj['desc'] + "\n\n" + m.group(3)
                        else:
                            currentObj['desc'] = m.group(3)
            else:
                # in this case we'll have to guess the function name
                pass

        elif cur == self.classEndMarker:
            currentObj["type"] = 'classend'

        elif cur == self.constructorMarker:
            currentObj["type"] = 'constructor'
            if self._currentClass == None:
                raise RuntimeError("A constructor must be defined inside a class")

            nxt = self._popNonMarker(tokens)
            if nxt:
                currentObj['desc'] = nxt

        elif cur == self.functionMarker:
            currentObj["type"] = 'function'
            nxt = self._popNonMarker(tokens)
            if nxt:
                # nxt describes the function
                m = self.functionPat.match(nxt)
                if not m:
                    raise RuntimeError("Malformed args to %s: %s" %
                                       (self.functionMarker, (cur[:20] + "...")))
                if m.group(1):
                    currentObj['name'] = m.group(1)
                else:
                    if m.group(2):
                        currentObj['name'] = m.group(2)
                    if m.group(3):
                        currentObj['desc'] = m.group(3)
            else:
                # in this case we'll have to guess the function name
                pass
        elif cur == self.propertyMarker:
            currentObj["type"] = 'property'
            nxt = self._popNonMarker(tokens)
            if nxt:
                # nxt now describes the property
                m = self.propPat.match(nxt)
                if not m:
                    raise RuntimeError("Malformed args to %s: %s" %
                                       (self.propertyMarker, (nxt[:20] + "...")))
                if m.group(1):
                    currentObj['name'] = m.group(1)
                    currentObj['dataType'] = m.group(2)
                    if m.group(3):
                        currentObj['desc'] = m.group(3)
                elif m.group(4):
                    currentObj['dataType'] = m.group(4)
                    currentObj['name'] = m.group(5)
                    if m.group(6):
                        currentObj['desc'] = m.group(6)
                else:
                    if m.group(7):
                        currentObj['name'] = m.group(7)
                    if m.group(8):
                        currentObj['desc'] = m.group(8)
            else:
                # in this case we'll have to guess the function name
                pass
        else:
            # do we have a handler for this type of marker?
            if (self.tags.has_key(cur)):
                arg = None

                # get argument if required
                if self.tags[cur].takesArg:
                    arg = self._popNonMarker(tokens)

                    if arg == None and not self.tags[cur].argOptional:
                        raise RuntimeError("%s tag requires an argument" % cur)

                ctx = self.tags[cur].parse(arg)
                self.tags[cur].attach(ctx, currentObj)
            else:
                raise RuntimeError("unrecognized tag: %s" % cur)

    def _analyzeContext(self, context):
        guessedName = None
        guessedType = None
        # first let's see if there's an exports statement after the block
        m = self.findExportsPat.search(context)
        if m:
            guessedName = m.group(1)

            # we'll only try to guess type if there's an exports statement
            if context.find("function") >= 0: 
                guessedType = 'function'
            else:
                guessedType = 'property'
        return guessedName, guessedType

    def _analyzeBlock(self, block, context, firstBlock, data):
        # Ye' ol' block analysis process.  block at this point contains
        # a chunk of text that has already had comment markers stripped out.

        # when we're parsing classes, we'll modify the classes nested
        # data structure rather than the global data structure for
        # this module
        globalData = data
        if not self._currentClass == None:
            data = data['classes'][self._currentClass]

        # Step 1: split the chunk of text into a token stream, each token
        # is either a tag /@\w+/ or a chunk of text (tag argument).
        # whitespace on either side of tokens is stripped
        tokens = self.tokenizePat.split(block)
        tokens = [n.strip() for n in tokens if n.strip()]

        # Step 2: initialize an object which will hold the resultant JSON
        # representation of this content block.
        curObj = {}

        # Step 3: Treat initial text as if it were a description. 
        if not self._isMarker(tokens[0]):
            tokens.insert(0, '@desc')

        # Step 4: collapse aliases
        tokens = [self.aliases[n] if self.aliases.has_key(n) else n for n in tokens]

        # Step 5: parse all tokens from the token stream, populating the
        # output representation as we go.
        while len(tokens):
            self._consumeToks(tokens, curObj, data)

        # Step 6: If the content block type is not known ('property', 'class',
        #         'function', etc), then let's apply some heuristics to guess
        #         what the documentation author *really* meant.
        (guessedName, guessedType) = self._analyzeContext(context)

        if not 'name' in curObj and guessedName:
            curObj['name'] = guessedName

        if not 'type' in curObj and guessedType:
            curObj['type'] = guessedType

        # in the first block case we'll guess that this is a module doc block
        if not 'type' in curObj and firstBlock:
            curObj['type'] = 'module'

        # Step 6: Fixup phase!  Depending on the docblock type, we may wish to perform
        #         some mutations to the output representation (like remove certain
        #         properties that are redundant, or improve the names of properties that
        #         were ambiguous until now (@type can be property type or return type)
        if 'type' in curObj:
            if curObj['type'] == 'function':
                del curObj['type']
                if 'functions' not in data:
                    data['functions'] = [ ]
                data['functions'].append(curObj)
            elif curObj['type'] == 'constructor':
                del curObj['type']
                data['constructor'] = curObj
            elif curObj['type'] == 'property':
                if 'dataType' in curObj:
                    curObj['type'] = curObj['dataType']
                    del curObj['dataType']
                else:
                    del curObj['type']

                if 'properties' not in data:
                    data['properties'] = [ ]
                data['properties'].append(curObj)
            elif curObj['type'] == 'classstart':
                if not 'classes' in data:
                    data['classes'] = [ ]

                self._currentClass = len(data['classes'])

                # XXX: check for redefinition?
                del curObj['type']
                data['classes'].append(curObj)

            elif curObj['type'] == 'classend':
                self._currentClass = None

            elif curObj['type'] == 'module':
                if 'desc' in curObj:
                    if 'desc' in globalData:
                        curObj['desc'] = "\n\n".join([globalData['desc'], curObj['desc']])
                    globalData['desc'] = curObj['desc']
                if 'name' in curObj:
                    globalData['module'] = curObj['name']
                if 'see' in curObj:
                    globalData['see'] = curObj['see']
            else:
                raise RuntimeError("I don't know what to do with a: %s" % curObj['type'])

        # Step 7: Validation phase!  Not all tags are allowed in all types of documentation blocks.
        # like '@returns' inside a '@classend' block would just be nutty.  let's scrutinize this
        # block to make sure it's sane.

        # XXX: write this phase!

        # Step 8: Addition to output document

        # XXX: write this phase!

    def extractFromFile(self, filename):
        # next read the whole file into memory
        contents = ""
        with open(filename, "r") as f:
            contents = f.read()

        data = self.extract(contents)

        # first determine the module name, it's always the same as the file name
        mod = os.path.basename(filename)
        dotLoc = mod.rfind(".")
        if (dotLoc > 0):
            mod = mod[:dotLoc]
        if not "module" in data:
            data["module"] = mod
        if not "filename" in data:
            data["filename"] = filename

        return data

    def extract(self, contents):
        # the data structure we'll build up
        data = {}

        # clear the lil' context flag that lets us know when we're parsing
        # classes (class definitions cannot span files)
        self._currentClass = None

        # now parse out and combine comment blocks
        firstBlock = True
        for m in self.docBlockPat.finditer(contents):
            block = self.blockFilterPat.sub("", m.group(2)).strip()
            context = m.group(4)
            # data will be mutated!
            self._analyzeBlock(block, context, firstBlock, data)
            firstBlock = False

        return data

    # begin definition of Tag Handler classes.

    # TagHandler is the base class for a handler of tags.  This is an
    # object that is capable of parsing tags and merging them into
    # the output JSON document.
    class TagHandler(object):
        # if takesArg is true, then text may occur after the tag
        # (it "accepts" a single text blob as an argument)
        takesArg = False
        # if takesArg is True, argOptional specifies whether the
        # argument is required
        argOptional = False
        # if mayRecur is True the tag may be specified multiple times
        # in a single document text blob.
        mayRecur = False
        def __init__(self, tagname):
            self.tagName = tagname

        # the parse method attempts to parse the text blob and returns
        # any representation of it that it likes.  This method should throw
        # if there's a syntactic error in the text argument.  text may be
        # 'None' if the tag accepts no argument.
        def parse(self, text):
            return text

        # attach merges the results of parsing a tag into the output
        # JSON document for a documentation block. `obj` is the value
        # returned by parse(), and parent is the json document that
        # the function should mutate
        def attach(self, obj, parent):
            parent[self.tagName[1:]] = obj

    class ParamTagHandler(TagHandler):
        takesArg = True

        # We support three forms:
        #   @property <name> <{type}> [description]
        #   @property <{type}> <name> [description]
        #   @property [name]
        #   [description]
        _pat = re.compile(
            '(?:^([\w.\[\]]+)\s*(?:{(\w+)})\s*(.*)$)|' +
            '(?:^{(\w+)}\s*([\w.\[\]]+)\s*(.*)$)|' +
            '(?:^([\w.\[\]]+)?\s*(.*)$)',
            re.S);

        def parse(self, text):
            m = self._pat.match(text)
            if not m:
                raise RuntimeError("Malformed args to %s: %s" %
                                   (tag, (text[:20] + "...")))
            p = { }
            if m.group(1):
                p['name'] = m.group(1)
                p['type'] = m.group(2)
                if m.group(3):
                    p['desc'] = m.group(3)
            elif m.group(4):
                p['type'] = m.group(4)
                p['name'] = m.group(5)
                if m.group(6):
                    p['desc'] = m.group(6)
            else:
                if m.group(7):
                    p['name'] = m.group(7)
                if m.group(8):
                    p['desc'] = m.group(8)
            return p

        def attach(self, obj, current):
            if not 'params' in current:
                current['params'] = [ ]
            current['params'].append(obj)

    class SeeTagHandler(TagHandler):
        takesArg = True
        mayRecur = True
        def attach(self, obj, current):
            if not 'see' in current:
                current['see'] = [ ]
            current['see'].append(obj)

    class DescTagHandler(TagHandler):
        takesArg = True
        mayRecur = True
        def attach(self, obj, current):
            if 'desc' in current:
                current['desc'] = current['desc'] + "\n\n" + obj
            else:
                current['desc'] = obj

    class ReturnTagHandler(TagHandler):
        takesArg = True
        _pat = re.compile('^\s*(?:{(\w+)})?\s*(.*)$', re.S);

        def parse(self, text):
            m = self._pat.match(text)
            if not m:
                raise RuntimeError("Malformed args to %s: %s" %
                                   (self.tagName, (text[:20] + "...")))
            rv = { }
            if m.group(1):
                rv['type'] = m.group(1)
            rv['desc'] = m.group(2)

            return rv

        def attach(self, obj, current):
            current['returns'] = obj

    class ThrowsTagHandler(ReturnTagHandler):
        def attach(self, obj, current):
            if 'throws' not in current:
                current['throws'] = [ ]
            current['throws'].append(obj)

    class TypeTagHandler(TagHandler):
        takesArg = True
        _pat = re.compile('^{?(.*?)}?$')

        def parse(self, text):
            # strip off { } if present
            return self._pat.match(text).group(1)

        def attach(self, obj, current):
            current['dataType'] = obj

if __name__ == '__main__':
    import sys
    import json
    ds = DocStract()

    docs = None
    if len (sys.argv) == 2:
        docs = ds.extractFromFile(sys.argv[1])
    elif len (sys.argv) == 1:
        docs = ds.extract(sys.stdin.read())
    else:
        print >> sys.stderr, "Usage: docstract [file]"
        sys.exit(1)

    print json.dumps(docs, indent=2, sort_keys=True) + "\n"
