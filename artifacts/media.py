#!/usr/bin/python

import re
from datetime import timedelta

class Media(object):

    def __init__(self):

        self.title = None

class Album(Media):

    def __init__(self, title = None, artist = None):
        super(Media, self).__init__()
        if title: self.title = title
        self.artist = artist
        self.tracks = []
        self.date = None
        self.release = None

    def __str__(self):

        string = 'title:  %s\nartist: %s\n' % (self.title, self.artist)
        string += 'tracks (%d):\n' % len(self.tracks)

        track_fields = ['volume', 'order', 'title', 'time']
        track_fmt = [1 for f in track_fields]
        tracks = []
        for track in self.tracks:
            fields = []
            for field in track_fields:
                value = getattr(track, field)
                if field == 'time':
                    value = ' (%s)' % str(timedelta(seconds = value)) if value else ''
                else: value = str(value)
                fmt_index = track_fields.index(field)
                if len(value) > track_fmt[fmt_index]: track_fmt[fmt_index] = len(value)
                fields.append(value)
            tracks.append(fields)
        track_fmt = '    ({:%d}) {:>%d}. {:%d}{:%d}' % tuple(track_fmt)
        string += '\n'.join([track_fmt.format(*track) for track in tracks])
        return string


    class Track(Media):

        def __init__(self, title = None, volume = 1, order = None):
            super(Media, self).__init__()
            if title: self.title = title
            self.volume = volume
            self.order = order
            self.time = None

        def __str__(self):

            string = '(%d) %d. %s' % (self.volume, self.order, self.title)
            if self.time: string += ' (%s)' % str(timedelta(seconds = self.time))
            print string
            return string

Media.Album = Album