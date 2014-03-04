#!/usr/bin/python

import os, pytest, sys

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if path not in sys.path: sys.path.append(path)

from collectors.amazon import Amazon
from artifacts.media import Media

class TestAmazon:

    def test_init_tracks_empty(self):

        t = Amazon.Album.Tracks()
        assert(t.source == 'amazon')
        assert(t.datum  == 'dp/tracks')
        assert(t.grid == None)
        assert(t.site == 'http://www.amazon.com/%s' % t.datum)
        assert(t.url == t.site)
        assert(t.culture == Media.Album.Track)
        assert(isinstance(t.artifact, t.culture))

    def test_init_tracks_grid(self):

        g = 'B00H312W4G'
        t = Amazon.Album.Tracks(g)
        assert(t.source == 'amazon')
        assert(t.datum  == 'dp/tracks')
        assert(t.grid == g)
        assert(t.site == 'http://www.amazon.com/%s' % t.datum)
        assert(t.url == '%s/%s' % (t.site, g))
        assert(t.culture == Media.Album.Track)
        assert(isinstance(t.artifact, t.culture))

    def test_collect_tracks_playlist(self):

        g = 'B00H312W4G'
        ts = Amazon.Album.Tracks(g).collect()
        assert(len(ts) == 10)
        for i in range(len(ts)):
            t = ts[i]
            assert(isinstance(t, Media.Album.Track))
            assert(t.order == i + 1)
            assert(t.volume == 1)
            assert(isinstance(t.title, unicode))
            assert(isinstance(t.time, int))
            assert(t.time > 0)

    def test_collect_tracks_tracklist(self):

        g = 'B004ZN9RWK'
        ts = Amazon.Album.Tracks(g).collect()
        assert(len(ts) == 10)
        for i in range(len(ts)):
            t = ts[i]
            assert(isinstance(t, Media.Album.Track))
            assert(t.order == i + 1)
            assert(t.volume == 1)
            assert(isinstance(t.title, unicode))
            assert(t.time is None)

    @pytest.mark.skipif(True, reason = 'todo')
    def test_collect_tracks_playlist_multivolume(self):
        pass

    @pytest.mark.skipif(True, reason = 'todo')
    def test_collect_tracks_tracklist_multivolume(self):
        pass
