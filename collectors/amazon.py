#!/usr/bin/python

import re, requests, time
from artifacts.media import Media
from bs4 import BeautifulSoup as bs
from collector import Collector
from concurrent.futures import ThreadPoolExecutor
from dateutil import parser as date_parser

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

        for c in album_colls:
            a = c.collect()
            print a
        exit()
        return [a for a in [c.collect() for c in album_colls] if a]

        with ThreadPoolExecutor(max_workers = 10) as collector:
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

        print self.grid
        self.excavate()

        # ignore things that are not albums
        if not self.get('ul', {'data-category': 'music'}):
            print 'not an album: %s' % self.url
            return None

        main = self.get('div', {'class': 'buying', 'style': None, 'id': None})
        if main is None:
            print 'retrying collect: %s' % self.url
            time.sleep(2)
            return self.collect()

        album = self.artifact
        album.source = self.source
        album.id = self.grid
        album.url = self.url
        album.title = main.find('span', attrs = {'id': 'btAsinTitle'}).text
        try:
            album.artist = main.find('a').text
        except AttributeError:
            album.artist = 'various'
        details = self.get('table', {'id': 'productDetailsTable'})
        if details is None:
            print 'retrying collect details: %s' % self.url
            time.sleep(2)
            return self.collect()

        # get details from product details
        details = details.find_all('li')
        for i in range(len(details)):
            detail = details[i].text.strip()
            # format (and issue date)
            if i == 0:
                if '(' in detail and ')' in detail:
                    split = detail.split('(')
                    album.format = split[0].replace('Audio', '').strip().lower()
                    issue = split[1].rstrip(')').strip()
                    album.issue = int(issue) if len(issue) == 4 else date_parser.parse(issue).date()
                else:
                    album.format = detail.strip().lower()
            else:
                # genres
                if detail.startswith('#'):
                    album.genres += [g.strip() for g in detail.split('>')[1:-1]]
                # tags
                elif detail.startswith('Format:'):
                    ignore = ['CD', 'Original recording', 'Double CD', 'Value Price', 'Vinyl']
                    tags = [tag.strip().title() for tag in detail.split(None, 1)[1].split(',')]
                    album.tags = [t for t in tags if t not in ignore]
                # label
                elif detail.startswith('Label:'):
                    album.label = detail.split(None, 1)[1].strip()
                # release date
                elif detail.startswith('Original Release Date:'):
                    release = detail.split(None, 3)[3].strip()
                    album.release = date_parser.parse(detail.split(None, 3)[3].strip()).date()
                # runtime
                elif detail.startswith('Run Time:'):
                    time = detail.split(None, 2)[2].strip().split()[0].split('.')
                    seconds = int(time[0]) * 60
                    if len(time) == 2: seconds += int(time[1])
                    album.time = seconds
                # volumes
                elif detail.startswith('Number of Discs:'):
                    album.volumes = int(detail.split(None, 3)[3].strip())

        # collect tracks
        album.tracks = self.Tracks(grid = self.grid).collect()
        if album.tracks and not album.volumes:
            album.volumes = max([t.volume for t in album.tracks])
        if album.tracks and not album.time and [t.time for t in album.tracks if t.time]:
            album.time = sum([t.time for t in album.tracks if t.time])
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
            try:
                if self.get('h2', {'id': 'MusicTracksHeader'}):
                    return tracklist()
                return playlist()
            except AttributeError:
                print 'retrying collect: %s' % self.url

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
            return [Album(str(i).strip(), genres = [self.name]) for i in ids]

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