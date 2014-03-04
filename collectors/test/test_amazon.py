#!/usr/bin/python

import os, pytest, sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from amazon import Amazon

class TestAmazon:

    def test_collect_tracks(self):

        tracks = Amazon.Tracks('B00H312W4G')
        print tracks