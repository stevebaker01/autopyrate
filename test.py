#!/usr/bin/python

from collectors.amazon import Amazon

a = Amazon.Album('B00GJ6NNSU', genres = 'foo').collect()
print a
