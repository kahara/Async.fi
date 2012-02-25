#!/usr/bin/env python


import sys, os, datetime, time, json, uuid
from lxml import etree
from operator import itemgetter


def usage():
    print 'usage: %s [preview|deploy]'
    exit()

try:
    action = sys.argv[1]
except:
    usage()
    

datetimefmt_in = '%Y-%m-%d %H:%M:%S'
datetimefmt_out = '%B %e, %Y'


posts = []  # individual posts, sorted form newest to oldest; items below refer to post's 'id's
site = {
    'posts': [],       # same list as above, cut into chunks of ten
    'categories': {},  # key is a category, contains a list of post ids
    'tags': {},        # key is a tag, contains a list of post ids
    'years': {},       # each year contains a dict of n months; each month contains a list of n posts
    }

for post in etree.parse('./source/posts.xml').getroot().xpath('post'):
    
    try:
        published = post.xpath('published')[0].text
        published = datetime.datetime.strptime(published, datetimefmt_in)
    except:
        continue
    
    posts.append({
            'id': uuid.uuid4().hex,
            'published': published,
            'category': post.xpath('category')[0].text,
            'tags': [tag.text for tag in post.xpath('tags')[0]],
            'slug': post.xpath('slug')[0].text,
            'title': post.xpath('title')[0].text,
            'body': post.xpath('body')[0].text,
            })
posts.sort(key = lambda post: post['published'], reverse=True)


# http://stackoverflow.com/a/1751478
def chunks(l):
    return [l[i:i+10] for i in range(0, len(l), 10)]

def getpost(postid):
    return filter(lambda post: post['id'] == postid, posts)[0]


for post in posts:
    #
    # categories
    #
    try:
        x = site['categories'][post['category']]
    except(KeyError):
        site['categories'][post['category']] = []
        x = site['categories'][post['category']]    
    x.append(post['id'])
    
    #
    # tags
    #
    for tag in post['tags']:
        try:
            x = site['tags'][tag]
        except(KeyError):
            site['tags'][tag] = []
            x = site['tags'][tag]
        x.append(post['id'])

for tag, tagposts in site['tags'].items():
    site['tags'][tag] = chunks(tagposts)

for category, categoryposts in site['categories'].items():
    site['categories'][category] = chunks(categoryposts)

site['posts'] = chunks([post['id'] for post in posts])
