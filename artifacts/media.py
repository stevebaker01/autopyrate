#!/usr/bin/python

import re
from copy import copy
from datetime import timedelta
from artifacts.artifact import Artifact
from mongoengine import *

class Album(Artifact):

    class Track(EmbeddedDocument):

        volume = IntField()
        order = IntField()
        title = StringField()
        time = IntField()
        path = StringField()

    artist = StringField()
    title = StringField()
    genre = StringField()
    format = StringField()
    issue = DateTimeField()
    release = DateTimeField()
    label = StringField()
    url = URLField()
    time = IntField()
    volumes = IntField()
    tracks = ListField(EmbeddedDocumentField(Track))
    genres = ListField(StringField())
    tags = ListField(StringField)
    path = StringField()
    meta = {'collection': 'albums'}

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

    def categorize(self):

        if len(self.genres) == 1:
            self.genre = self.genres[0]
        elif self.genres:
            genres = {}
            for genre in self.genres:
                c = self.genres.count(genre)
                if c not in genres: genres[c] = []
                if genre not in genres[c]: genres[c].append(genre)
            m = genres[max(genres.keys())]
            if len(m) == 1:
                self.genre = m[0]
            else:
                for genre in self.genres:
                    if genre in m:
                        self.genre = genre
                        break

        self.genres = list(set(self.genres))

