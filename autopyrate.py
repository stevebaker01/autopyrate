#!/usr/bin/python

import os, re, sys
from artifacts.artifact import Artifact
from collectors.amazon import Amazon, Album

genres = ['Alternative Rock', 'Dance & Electronic', 'Hard Rock & Metal', 'Indie', 'Jazz', 'Pop', 'Rap & Hip-Hop', 'Rock']
# genres = ['Alternative Rock']
ignore = ['Christian', 'Country', 'Gospel']

def main():

    Artifact.db()
    albums = Amazon.collect_new_albums(genres = genres, ignore = ignore, save = True)
    print(len(albums))
    for title in sorted([album.title for album in albums]): print(title)

if __name__ == '__main__':
	main()
