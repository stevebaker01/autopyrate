#!/usr/bin/python

import re, requests, time
from artifacts.media import Album
from bs4 import BeautifulSoup as bs
from collectors.collector import Collector
from concurrent.futures import ThreadPoolExecutor
from dateutil import parser as date_parser

class Amazon(Collector):

    source = 'amazon'
    datum = 'http://www.amazon.com'

    @classmethod
    def collect_new_albums(cls, genres = [], ignore = [], vinyl = False):

        genre_colls = NewMusic().collect()
        if genres: genre_colls = filter(lambda g: g.name in genres, genre_colls)
        a_colls = []
        for genre_coll in genre_colls: a_colls += genre_coll.collect()
        album_colls = []
        for album_coll in a_colls:
            if album_coll.grid not in [a.grid for a in album_colls]: album_colls.append(album_coll)

        for c in album_colls:
            a = c.collect()
            # if a: print a
        exit()
        return [a for a in [c.collect() for c in album_colls] if a]

        albums = []
        with ThreadPoolExecutor(max_workers = 10) as collector:
            for album_coll in album_colls: albums.append(collector.submit(album_coll.collect))
            albums = [album.result() for album in albums if album]

        composite = {}
        for album in albums:
            if not album or (not vinyl and album.format == 'vinyl'): continue
            for genre in album.genres:
                if genre in ignore:
                    break
            else:
                if album.id not in composite:
                    composite[album.id] = album
                    continue
                composite[album.id].genres += album.genres
        for album in composite.values():
            album.categorize()
        return composite.values()

class Album(Amazon):

    datum = 'dp'
    culture = Album

    def __init__(self, grid, genres = []):

        self.genres = genres
        super(Amazon, self).__init__(grid = grid)

    def collect(self):

        print(self.grid)
        self.excavate()
        retries = 0
        while not self.get('ul', {'data-category': re.compile(r'.*')}):
            if retries == 5:
                raise collector.exceptions.ExcavateFail(self.url)
            time.sleep(2)
            retries += 1
            print('retrying excavate (%d): %s' % (retries, self.url))
            excavate()

        # ignore things that are not albums
        if not self.get('ul', {'data-category': 'music'}):
            print('not an album: %s' % self.url)
            return None

        main = self.get('div', {'class': 'buying', 'style': None, 'id': None})
        if main is None:
            print('retrying collect: %s' % self.url)
            time.sleep(2)
            return self.collect()

        album = self.artifact
        album.source = self.source
        album.grid = self.grid
        album.url = self.url
        album.title = main.find('span', attrs = {'id': 'btAsinTitle'}).text
        try:
            album.artist = main.find('a').text
        except AttributeError:
            album.artist = 'various'
        details = self.get('table', {'id': 'productDetailsTable'})
        if details is None:
            print('retrying collect details: %s' % self.url)
            time.sleep(2)
            return self.collect()

        rockify = ['Punk', 'Indie', 'Alternative', 'Glam']
        if self.genres:
            if not isinstance(self.genres, list) and not isinstance(self.genres, tuple):
                self.genres = [self.genres]
            genres = []
            for genre in self.genres: genres += genre.split(' & ')
            self.genres = genres
        for i in range(len(self.genres)):
            if self.genres[i] in rockify: self.genres[i] += ' Rock'
        album.genres = self.genres

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
                ignore = ['CD', 'Original recording', 'Double CD', 'Value Price', 'Vinyl', 'General']
                # genres
                if detail.startswith('#'):
                    genres = [h for h in [g.strip() for g in detail.split('>')[1:]] if h not in ignore]
                    for genre in genres:
                        genre = list(genre.replace(' Music', '').split(' & '))
                        for g in genre:
                            if g in rockify: g += ' Rock'
                            album.genres.append(g)
                # tags
                elif detail.startswith('Format:'):
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
                    runtime = detail.split(None, 2)[2].strip().split()[0].split('.')
                    seconds = int(runtime[0]) * 60
                    if len(runtime) == 2: seconds += int(runtime[1])
                    album.time = seconds
                # volumes
                elif detail.startswith('Number of Discs:'):
                    album.volumes = int(detail.split(None, 3)[3].strip())

        # collect tracks
        album.tracks = self.Tracks(grid = self.grid).collect()
        if album.tracks and not album.volumes:
            album.volumes = max([t.volume for t in album.tracks])
        if album.tracks and not album.time:
            time = sum([t.time for t in album.tracks if t.time])
            if time: album.time = time
        print(album)
        return album

    class Tracks(Amazon):

        datum = 'dp/tracks'
        culture = Album.Track
        
        def collect(self):

            track_re = re.compile(r'^\D*(\d+)\.(.*)$')

            def trackify(strings):

                tracks = []
                volume = 0
                for string in strings:
                    track = track_re.match(string)
                    if not track: continue
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
                    tracks[i].time = ((int(times[i].split(':')[0]) * 60) + int(times[i].split(':')[1]))
                return tracks

            self.excavate()
            try:
                if self.get('h2', {'id': 'MusicTracksHeader'}):
                    return tracklist()
                return playlist()
            except RuntimeError:
                print('retrying collect: %s' % self.url)
                self.collect()

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
            return [Album(str(i).strip(), genres = self.name) for i in ids]

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
