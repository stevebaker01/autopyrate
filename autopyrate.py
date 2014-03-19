#!/usr/bin/python

import re
from collectors.amazon import Amazon

genres = ['Alternative Rock', 'Dance & Electronic', 'Hard Rock & Metal', 'Indie', 'Jazz', 'Pop', 'Rap & Hip-Hop', 'Rock']
# genres = ['Alternative Rock']

def main():

    b_re = re.compile(r'\[.*\]')
    amazon = Amazon.collect_new_albums(genres = genres)
    these = set()
    those = set()
    for a in amazon: 
        if a.genre: these.add(a.genre)
        if a.genres: those = those.union(a.genres)
    these = list(these)
    those = list(those)
    these.sort()
    those.sort()
    for g in these:
        print g
    print
    for g in those:
        print g

if __name__ == '__main__':
    main()
