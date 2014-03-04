#!/usr/bin/python

import re, requests
from collector import Collector
from artifacts.media import Media
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup as bs

class Amazon(Collector):

    source = 'amazon'
    datum = 'http://www.amazon.com'

    @classmethod
    def collect_new_albums(cls, genres = []):

        genre_colls = NewMusic().collect()
        if genres: genre_colls = filter(lambda g: g.name in genres, genre_colls)
        a_colls = []
        for genre_coll in genre_colls: a_colls += genre_coll.collect()
        album_colls = []
        for album_coll in a_colls:
            if album_coll.grid not in [a.grid for a in album_colls]: album_colls.append(album_coll)
        with ThreadPoolExecutor(max_workers = 5) as collector:
            albums = []
            for album_coll in album_colls: albums.append(collector.submit(album_coll.collect))
            return [album.result() for album in albums]

class Album(Amazon):

    datum = 'dp'
    culture = Media.Album

    def __init__(self, grid, genres = []):

        self.genres = genres
        super(Amazon, self).__init__(grid = grid)

    def collect(self):

        self.excavate()
        main = self.get('div', {'class': 'buying', 'style': None, 'id': None})
        album = self.artifact
        album.title = main.find('span', attrs = {'id': 'btAsinTitle'}).text
        album.artist = main.find('a').text
        album.tracks = self.Tracks(grid = self.grid).collect()
        print album
        print
        return album

    class Tracks(Amazon):

        datum = 'dp/tracks'
        culture = Media.Album.Track
        
        def collect(self):

            track_re = re.compile(r'^\D*(\d+)\.(.*)$')

            def trackify(strings):

                tracks = []
                volume = 0
                for string in strings:
                    track = track_re.match(string)
                    order = int(track.group(1))
                    if order == 1: volume += 1
                    title = track.group(2).strip()
                    tracks.append(self.culture(order = order, title = title, volume = volume))
                return tracks

            def tracklist():
                row_re = re.compile(r'listRow(Odd|Even)')
                return trackify([t[0] for t in self.get_all('tr', {'class': row_re}, attrs = ['text'])])

            def playlist():

                tracks = trackify([t[0] for t in self.get_all('td', {'class': 'titleCol'}, attrs = ['text'])])
                times = [t[0] for t in self.get_all('td', {'class': 'runtimeCol'}, attrs = ['text'])]
                for i in range(len(tracks)):
                    tracks[i].time = ((int(times[i].split(':')[0]) * 60) + int(times[i].split(':')[0]))
                return tracks

            self.excavate()
            if self.get('h2', {'id': 'MusicTracksHeader'}):
                return tracklist()
            return playlist()

class NewMusic(Amazon):

    # Returns NewMusicGenre colectors
    datum = 'New-Future-Releases-Music-Pre-Order/b/ref=sv_m_4?ie=UTF8&node=465672'

    def collect(self):

        re_href = re.compile(r'^/gp/(|/)new-releases/music/(\d+)$')
        self.excavate()
        finds = self.get_all('a', {'href': re_href}, attrs = ('text', 'href'))
        genres = []
        for find in finds:
            grid = int(re_href.match(find[1]).group(2))
            if grid not in [genre.grid for genre in genres]:
                genres.append(NewMusicGenre(grid = grid, name = str(find[0])))
        genres.sort(key = lambda x: x.name)
        return genres

class NewMusicGenre(Amazon):

    # Returns Album collectors.
    datum = 'gp/new-releases/music'

    def collect(self):

        def excavate(url):

            ids = []
            id_re = re.compile(r'^http://www\.amazon\.com/.+/dp/(.+)(|/.+)$')
            zts = bs(requests.get(url).text).find_all('div', attrs = {'class': 'zg_title'})
            ids += [id_re.match(zt.find('a')['href'].strip()).group(1) for zt in zts]
            print ids
            return [Album(str(i), genres = [self.name]) for i in ids]

        ajax = '?ie=UTF8&pg=%d&ajax=1&isAboveTheFold=%d'
        grid = []
        for page in range(1, 6):
            for fold in range(2):
                grid.append('%s/%s/%s' % (self.site, self.grid, ajax % (page, fold)))
        albums = []
        with ThreadPoolExecutor(max_workers = 10) as collector:
            matrix, finds = (list(), list())
            for unit in grid: matrix.append(collector.submit(excavate, unit))
            for find in matrix: finds += find.result()
            return finds

Amazon.Album = Album
Amazon.NewMusic = NewMusic
Amazon.NewMusicGenre = NewMusicGenre