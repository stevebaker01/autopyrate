#!/usr/bin/python

import os, re, sys
from collectors.amazon import Amazon, Album

genres = ['Alternative Rock', 'Dance & Electronic', 'Hard Rock & Metal', 'Indie', 'Jazz', 'Pop', 'Rap & Hip-Hop', 'Rock']
# genres = ['Alternative Rock']
ignore = ['Christian', 'Country', 'Gospel']

def main():

    a = Album(grid = 'B00000K092').collect()
    print(a)
    # b_re = re.compile(r'\[.*\]')
    # amazon = Amazon.collect_new_albums(genres = genres, ignore = ignore)
    # these = set()
    # those = set()
    # for a in amazon: 
    #     if a.genre: these.add(a.genre)
    #     if a.genres: those = those.union(a.genres)
    # these = list(these)
    # those = list(those)
    # these.sort()
    # those.sort()
    # for g in these:
    #     print(g)
    # print
    # for g in those:
    #     print(g)

    # print(len(amazon))

if __name__ == '__main__':
	main()
