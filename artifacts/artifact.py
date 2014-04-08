#!/usr/bin/python

import os
from traceback import extract_stack
from collections import OrderedDict
from mongoengine import connect, Document, StringField, URLField

class Artifact(Document):

    source = StringField()
    grid = StringField()
    url = URLField()
    meta = {'allow_inheritance': True}

    @classmethod
    def db(cls, name = None):
        if not name: name = os.path.splitext(os.path.basename(extract_stack()[0][0]))[0]
        connect(name)

    def __str__(self):

        identity = ('source', 'grid')
        len_attr = max([len(str(a)) for a in self._fields_ordered if a not in identity])
        len_val = max([len(str(getattr(self, a))) for a in self._fields_ordered if not isinstance(getattr(self, a), list)])
        fmt_attr = '{:%d} {:%d}\n' % (len_attr + 1, len_val)
        string = fmt_attr.format('source:', ('%s (%s)' % (self.source, self.grid)))
        for a in self._fields_ordered:
            if a in identity: continue
            v = getattr(self, a)
            if not v: continue
            if isinstance(v, list):
                if '%s_str' % a in dir(self): 
                    string += getattr(self, '%s_str' % a)()
                else:
                    string += '%s (%d):\n' % (a, len(v))
                    for x in v:
                        string += '    %s\n' % str(x)
                continue
            string += fmt_attr.format('%s:' % a, str(v).strip())
        return string
