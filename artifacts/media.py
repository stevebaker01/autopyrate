#!/usr/bin/python

import re
from copy import copy
from datetime import timedelta

class Media(object):

    def __init__(self):

        self.title = None

class Album(Media):

    def __init__(self, title = None, artist = None, genres = []):
        super(Media, self).__init__()
        self.id = None
        if title: self.title = title
        self.artist = artist
        self.tracks = []
        self.source = None
        self.url = None

        self.format = None
        self.issue = None
        self.release = None
        self.genres = []
        if isinstance(genres, basestring):
            self.genres.append(genres)
        elif isinstance(genres, list) or isinstance(genres, tuple):
            self.genres += list(genres)
        self.tags = []
        self.label = None
        self.time = None
        self.volumes = None

    def __str__(self):

        string = ''
        album_fields = ['title', 'artist', 'label', 'issue', 'release', 'time', 'source', 'url', 'volumes']
        field_length = max([len(f) for f in album_fields])
        album_values = []
        for field in album_fields:
            value = copy(getattr(self, field))
            if field == 'time': value = timedelta(seconds = value) if value else None
            if field == 'title' and self.format: value = '%s [%s]' % (value, self.format)
            if field == 'source': value = '%s (%s)' % (self.source, self.id)
            value = str(value) if value else ''
            album_values.append(value)
        value_length = max([len(v) for v in album_values])
        album_fmt = '{:%d}: {:%d}\n' % (field_length, value_length)
        for i in range(len(album_fields)):
            if album_values[i]: string += album_fmt.format(album_fields[i], album_values[i])

        if self.tags: string += 'tags (%d):\n' % len(self.tags)
        for tag in self.tags: string += '    %s' % tag

        if self.tracks: string += 'tracks (%d):\n' % len(self.tracks)
        track_fields = ['order', 'title', 'time']
        track_fmt = [1 for f in track_fields]
        tracks = []
        for track in self.tracks:
            fields = []
            for field in track_fields:
                value = getattr(track, field)
                if field == 'time':
                    value = ' %s' % str(timedelta(seconds = value)) if value else ''
                else: value = str(value)
                fmt_index = track_fields.index(field)
                if len(value) > track_fmt[fmt_index]: track_fmt[fmt_index] = len(value)
                fields.append(value)
            tracks.append(fields)
        margin = 1 if not self.volumes or self.volumes < 2 else 2
        track_fmt = '{:%d}{:>%d}. {:%d}{:%d}\n' % tuple([margin * 4] + track_fmt)
        volume = 0
        for track in tracks:
            if margin == 2 and track[0] == '1':
                volume += 1
                string += '    volume: %d\n' % volume
            string += track_fmt.format('', *track)

        if self.genres: string += 'genres (%d):\n' % len(self.genres)
        for genre in self.genres: string += '    %s\n' % genre
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