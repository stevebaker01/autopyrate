#!/usr/bin/python

import re
from collectors.amazon import Amazon

genres = ['Alternative Rock', 'Dance & Electronic', 'Hard Rock & Metal', 'Indie', 'Jazz', 'Pop', 'Rap & Hip-Hop', 'Rock']
# genres = ['Alternative Rock']

def main():

    b_re = re.compile(r'\[.*\]')
    amazon = Amazon.collect_new_albums(genres = genres)

if __name__ == '__main__':
    main()
