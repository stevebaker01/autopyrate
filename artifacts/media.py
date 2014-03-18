#!/usr/bin/python

import re
from copy import copy
from datetime import timedelta
from artifacts.artifact import Artifact

class Media(Artifact):

    __attrs__ = ['title']

class Album(Media):

    __attrs__ = ['artist', 'genre', 'format', 'issue', 'release', 'label', 'time', 'volumes']
    __lists__ = ['tracks', 'genres', 'tags']

    def __init__(self, title = None, artist = None):
        super(Media, self).__init__()
        if title: self.title = title
        if artist: self.artist = artist

    def tracks_str(self):
        if not self.tracks: return ''
        buf = 8 if (self.volumes and self.volumes > 1) else 4
        volume = 0
        total_time = [track.time for track in self.tracks]
        total_time = ' ' if list(set(total_time)) == [None] else str(timedelta(seconds = sum(total_time)))
        string = 'tracks (%d): %s\n' % (len(self.tracks), total_time)
        lens = [buf, 0, 0, 8]
        for track in self.tracks:
            if len(str(track.order)) > lens[1]: lens[1] = len(str(track.order))
            if len(str(track.title)) > lens[2]: lens[2] = len(str(track.title))
        fmt_track = '{:%d}{:>%d}. {:%d} {:%d}\n' % tuple(lens)
        for track in self.tracks:
            if buf == 8 and track.order == 1:
                volume = track.volume
                volume_time = [t.time for t in self.tracks if t.volume == volume]
                volume_time = ' ' if list(set(volume_time)) == [None] else str(timedelta(seconds = sum(volume_time)))
                string += '    volume %d: %s\n' % (volume, volume_time)
            time = str(timedelta(seconds = track.time)) if track.time else ' '
            string += fmt_track.format(' ', track.order, track.title, time)
        return string

    class Track(Media):

        __attrs__ = ['order', 'time', 'volume']

        def __init__(self, title = None, volume = 1, order = None):
            super(Media, self).__init__()
            if title: self.title = title
            if order: self.order = order
            self.volume = volume

        def __str__(self):

            string = '%d. %s' % (self.order, self.title)
            if self.time: string += ' %s' % str(timedelta(seconds = self.time))
            return string

Media.Album = Album
