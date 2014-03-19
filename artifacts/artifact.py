#!/usr/bin/python

class Artifact(object):

    __attrs__ = ['source', 'id']
    __lists__ = []

    def __init__(self, id = None):

        self.__form__()
        if id: self.id = id

    def __form__(self):

        for g in ('__attrs__', '__lists__'):
            group = getattr(self, g)
            bases = self.__class__.__bases__
            while bases:
                for base in bases:
                    if issubclass(base, Artifact) and g in dir(base()):
                        group = getattr(base(), g) + group
                        setattr(self, g, group)
                    bases = base.__bases__

        for a in self.__attrs__:
            setattr(self, a, None)
        for l in self.__lists__:
            setattr(self, l, [])

    def __str__(self):

        identity = ('source', 'id')
        len_attr = max([len(str(a)) for a in self.__attrs__ if a not in identity])
        len_val = max([len(str(getattr(self, a))) for a in self.__attrs__ if a not in identity])
        fmt_attr = '{:%d} {:%d}\n' % (len_attr + 1, len_val)
        string = fmt_attr.format('source:', ('%s (%s)' % (self.source, self.id)))
        for a in self.__attrs__:
            if a in identity or not getattr(self, a): continue
            string += fmt_attr.format('%s:' % a, str(getattr(self, a)))
        for l in self.__lists__:
            if not getattr(self, l): continue
            if '%s_str' % l in dir(self): 
                string += getattr(self, '%s_str' % l)()
            else:
                string += '%s (%d):\n' % (l, len(getattr(self, l)))
                for x in getattr(self, l):
                    string += '    %s\n' % str(x)
        return string

    def translate(self, dialect = 'utf8'):

        def decypher(item):
            if isinstance(item, Artifact):
                item.translate(dialect = dialect)
            elif isinstance(item, list):
                for i in range(len(item)):
                    item[i] = decypher(item[i])
            elif isinstance(item, basestring):
                item = item.encode(dialect)
            return item

        for a in self.__attrs__ + self.__lists__:
            setattr(self, a, decypher(getattr(self, a)))

