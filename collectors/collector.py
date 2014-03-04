#!/usr/bin/python

import re, requests
from bs4 import BeautifulSoup as bs

class Collector(object):

    datum = None
    culture = None
    artifact = None

    def __init__(self, grid = None, name = None):

        self.grid = grid
        self.name = name
        if 'datum' in dir(self): self.site = self.datum
        self.locus()
        self.url = self.site
        if self.grid: self.drop_grid()
        if self.culture: self.artifact = self.culture()

    def locus(self):

        bases = self.__class__.__bases__
        path = [self.datum]
        while bases:
            for base in bases:
                if issubclass(base, Collector) and 'datum' in dir(base()):
                    path.append(base().datum)
                bases = base.__bases__
        path.reverse()
        self.site = '/'.join(filter(lambda x: x is not None, path))

    def drop_grid(self):

        self.url = '%s/%s' % (self.site, self.grid)

    def excavate(self):

        self.matrix = bs(requests.get(self.url).text)
        return self.matrix

    def get_all(self, these, conditions, attrs = ()):

        these = self.matrix.find_all(these, attrs = conditions)
        if not attrs: return these
        layers = []
        for this in these:
            layer = []
            for attr in attrs:
                value = this.text.strip() if attr == 'text' else this[attr]
                layer.append(value)
            layers.append(layer)
        return layers

    def get(self, this, conditions, attrs = ()):

        this = self.matrix.find(this, attrs = conditions)
        if not attrs: return this
        layer = []
        for attr in attrs:
            value = this.text.strip() if attr == 'text' else this[attr]
        return layer
