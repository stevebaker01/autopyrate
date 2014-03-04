#!/usr/bin/python

from collectors.amazon import Amazon

# genres = ['Alternative Rock', 'Dance & Electronic', 'Hard Rock & Metal', 'Indie', 'Jazz', 'Pop', 'Rap & Hip-Hop', 'Rock']
genres = ['Alternative Rock']

def main():

	amazon = Amazon.collect_new_albums(genres = genres)


if __name__ == '__main__':
    main()
