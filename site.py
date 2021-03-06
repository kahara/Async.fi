#!/usr/bin/env python
from __future__ import generators

import sys, os, shutil, time, datetime, time, json, uuid, pystache, re, cgi, SimpleHTTPServer, SocketServer
from lxml import etree
from BeautifulSoup import BeautifulSoup
from copy import deepcopy
import boto
from boto.s3.bucket import Bucket
from boto.s3.key import Key
from boto.cloudfront import CloudFrontConnection


# http://code.activestate.com/recipes/105873-walk-a-directory-tree-using-a-generator/
def dirwalk(dir):
    "walk a directory tree, using a generator"
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            yield fullpath


def usage():
    print 'usage: %s [preview|deploy|invalidate] <extension>'
    exit()

try:
    action = sys.argv[1]
except:
    usage()
    

datetimefmt_in = '%Y-%m-%d %H:%M:%S'
datetimefmt_formal = '%Y-%m-%dT%H:%M:%S+00:00'
datetimefmt_pretty = '%B %e, %Y'

bucketname = 'www.async.fi'
base = 'http://www.async.fi'

cf_distribution = 'E1556WXIQRXJQ9'

posts = []  # individual posts, sorted form newest to oldest; items below refer to post's 'id's
site = {
    'posts': [],       # same list as above, cut into chunks of ten
    'categories': {},  # key is a category, contains a list of post ids (chunked)
    'tags': {},        # key is a tag, contains a list of post ids (chunked)
    'years': {},       # each year contains a dict of n months; each month contains a list of n posts (chunked)    
    }

for post in etree.parse('./source/posts.xml').getroot().xpath('post'):
    
    try:
        published = post.xpath('published')[0].text
        published = datetime.datetime.strptime(published, datetimefmt_in)
    except:
        continue
    
    posts.append({
            'id': uuid.uuid4().hex,
            'link': '/%04d/%02d/%s/' % (published.year, published.month, post.xpath('slug')[0].text),
            'published': published,
            'category': post.xpath('category')[0].text,
            'tags': [tag.text for tag in post.xpath('tags')[0]],
            'slug': post.xpath('slug')[0].text,
            'title': cgi.escape(post.xpath('title')[0].text),
            'body': post.xpath('body')[0].text,
            #'body': post.xpath('body')[0].text.replace('href="/media/', 'href="%s/media/' % (mediabase, )).replace('src="/media/', 'src="%s/media/' % (mediabase, )) if action == 'deploy' else post.xpath('body')[0].text,
            })
posts.sort(key = lambda post: post['published'], reverse=True)


# http://stackoverflow.com/a/1751478
def chunks(l):
    return [l[i:i+5] for i in range(0, len(l), 5)]

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

    #
    # year
    #
    try:
        x = site['years'][post['published'].year]['posts']
    except(KeyError):
        site['years'][post['published'].year] = {
            'posts': [],
            'months': {}
        }
        x = site['years'][post['published'].year]['posts']
    x.append(post['id'])
    
    #
    # month
    #
    try:
        x = site['years'][post['published'].year]['months'][post['published'].month]
    except:
        site['years'][post['published'].year]['months'][post['published'].month] = []
        x = site['years'][post['published'].year]['months'][post['published'].month]
    x.append(post['id'])
    
for tag, tagposts in site['tags'].items():
    site['tags'][tag] = chunks(tagposts)

for category, categoryposts in site['categories'].items():
    site['categories'][category] = chunks(categoryposts)

for year in site['years']:
    site['years'][year]['posts'] = chunks(site['years'][year]['posts'])
    for month in site['years'][year]['months']:
        site['years'][year]['months'][month] = chunks(site['years'][year]['months'][month])

site['posts'] = chunks([post['id'] for post in posts])

for post in posts:
    post['formal_published'] = post['published'].strftime(datetimefmt_formal)
    post['pretty_published'] = post['published'].strftime(datetimefmt_pretty)
    post['title'] = post['title'].replace('"', '')


loader = pystache.Loader()
base_tmpl = loader.load_template('base', 'source', 'utf-8')
post_tmpl = loader.load_template('post', 'source', 'utf-8')
list_tmpl = loader.load_template('list', 'source', 'utf-8')

monthnames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

recent = pystache.render(list_tmpl, { 'items': [{ 'link': post['link'], 'title': post['title']  } for post in posts[:5]] }).encode('utf-8')

archives = []
years = []
for year in site['years']:
    years.append(year)
years.reverse()
for year in years:    
    months = []
    for month in site['years'][year]['months']:
        months.append(month)
    months.reverse()        
    for month in months:
        count = 0
        for parts in site['years'][year]['months'][month]:
            count += len(parts)
        archives.append({
                'link': '/%04d/%02d/' % (year, month),
                'title': '%s %04d' % (monthnames[month], year),
                'count': '%s' % count
                })

archives = sorted(archives, key=lambda a: a['link'])
archives.reverse()
archives = pystache.render(list_tmpl, { 'items': archives } ).encode('utf-8')

categories = pystache.render(list_tmpl, { 'items': [{ 'link': '/category/%s/' % (category, ), 'title': category } for category in site['categories']] }).encode('utf-8')

baseattrs = {
    #'assetbase': assetbase if action == 'deploy' else None,
    'recent': recent,
    'archives': archives,
    'categories': categories
}


shutil.rmtree('./target', ignore_errors=True)
os.mkdir('./target')


# media, asset
shutil.rmtree('./target/media', ignore_errors=True)
shutil.copytree('./source/media', './target/media')
shutil.rmtree('./target/asset', ignore_errors=True)
shutil.copytree('./source/asset', './target/asset')


# root
os.mkdir('./target/page')
n = len(site['posts'])
for index, page in enumerate(site['posts']):
    os.mkdir('./target/page/%d' % (index+1, ))
    attrs = deepcopy(baseattrs)
    attrs['posts'] = [pystache.render(post_tmpl, getpost(post)) for post in page]
    attrs['next'] = '/page/%d/' % (index+2, ) if index < n-1 else None
    attrs['prev'] = '/page/%d/' % (index, ) if index > 1 else '/' if index > 0 else None
    open('./target/page/%d/index.html' % (index+1, ) if index > 0 else './target/index.html', 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))


# years, months
for year in site['years']:
    os.mkdir('./target/%04d' % (year, ))
    os.mkdir('./target/%04d/page' % (year, ))
    n = len(site['years'][year]['posts'])
    for index, page in enumerate(site['years'][year]['posts']):
        os.mkdir('./target/%04d/page/%d' % (year, index+1, ))
        attrs = deepcopy(baseattrs)
        attrs['title'] = '%04d' % (year, )
        attrs['description'] = 'Posts for year %04d' % (year, )
        attrs['posts'] = [pystache.render(post_tmpl, getpost(post)) for post in page]
        attrs['next'] = '/%04d/page/%d/' % (year, index+2) if index < n-1 else None
        attrs['prev'] = '/%04d/page/%d/' % (year, index) if index > 1 else '/%04d/' % (year, ) if index > 0 else None
        open('./target/%04d/page/%d/index.html' % (year, index+1) if index > 0 else './target/%04d/index.html' % (year, ), 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))
    
    for month in site['years'][year]['months']:
        os.mkdir('./target/%04d/%02d' % (year, month))
        os.mkdir('./target/%04d/%02d/page' % (year, month))
        n = len(site['years'][year]['months'][month])
        for index, page in enumerate(site['years'][year]['months'][month]):
            os.mkdir('./target/%04d/%02d/page/%d' % (year, month, index+1, ))
            attrs = deepcopy(baseattrs)
            attrs['title'] = '%s %04d' % (monthnames[month], year, )
            attrs['description'] = 'Posts for %s %04d' % (monthnames[month], year)
            attrs['posts'] = [pystache.render(post_tmpl, getpost(post)) for post in page]
            attrs['next'] = '/%04d/%02d/page/%d/' % (year, month, index+2) if index < n-1 else None
            attrs['prev'] = '/%04d/%02d/page/%d/' % (year, month, index) if index > 1 else '/%04d/%02d/' % (year, month) if index > 0 else None
            open('./target/%04d/%02d/page/%d/index.html' % (year, month, index+1) if index > 0 else './target/%04d/%02d/index.html' % (year, month), 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))


# individual posts
for post in posts:
    os.mkdir('./target/%04d/%02d/%s' % (post['published'].year, post['published'].month, post['slug']))
    attrs = deepcopy(baseattrs)
    attrs['title'] = '%s' % (post['title'], )
    attrs['description'] = '%s' % (post['title'], )
    attrs['posts'] = []
    attrs['posts'].append(pystache.render(post_tmpl, post))
    open('./target/%04d/%02d/%s/index.html' % (post['published'].year, post['published'].month, post['slug']), 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))


# categories
os.mkdir('./target/category')
for category in site['categories']:
    os.mkdir('./target/category/%s' % (category, ))
    os.mkdir('./target/category/%s/page' % (category, ))
    n = len(site['categories'][category])
    for index, page in enumerate(site['categories'][category]):        
        os.mkdir('./target/category/%s/page/%d' % (category, index+1, ))
        attrs = deepcopy(baseattrs)
        attrs['title'] = '%s' % (category, )
        attrs['description'] = 'Posts in category %s' % (category, )
        attrs['posts'] = [pystache.render(post_tmpl, getpost(post)) for post in page]
        attrs['next'] = '/category/%s/page/%d/' % (category, index+2) if index < n-1 else None
        attrs['prev'] = '/category/%s/page/%d/' % (category, index) if index > 1 else '/category/%s/' % (category, ) if index > 0 else None
        open('./target/category/%s/page/%d/index.html' % (category, index+1) if index > 0 else './target/category/%s/index.html' % (category, ), 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))

# tags
os.mkdir('./target/tag')
for tag in site['tags']:
    os.mkdir('./target/tag/%s' % (tag, ))
    os.mkdir('./target/tag/%s/page' % (tag, ))
    n = len(site['tags'][tag])
    for index, page in enumerate(site['tags'][tag]):        
        os.mkdir('./target/tag/%s/page/%d' % (tag, index+1, ))
        attrs = deepcopy(baseattrs)
        attrs['title'] = '%s' % (tag, )
        attrs['description'] = 'Posts tagged with %s' % (tag, )
        attrs['posts'] = [pystache.render(post_tmpl, getpost(post)) for post in page]
        attrs['next'] = '/tag/%s/page/%d/' % (tag, index+2) if index < n-1 else None
        attrs['prev'] = '/tag/%s/page/%d/' % (tag, index) if index > 1 else '/tag/%s/' % (tag, ) if index > 0 else None
        open('./target/tag/%s/page/%d/index.html' % (tag, index+1) if index > 0 else './target/tag/%s/index.html' % (tag, ), 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))


# feed
os.mkdir('./target/feed')
feed_tmpl = loader.load_template('feed', 'source', 'utf-8')

attrs = {
    'base': base,
    'lastBuildDate': time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime()),
    'items': [{
            'title': post['title'],
            'link': post['link'],
            'pubDate': post['published'].strftime('%a, %d %b %Y %H:%M:%S +0000'),
            'category': post['category'],
            'tags': post['tags'],
            'description': ' '.join(''.join([e for e in BeautifulSoup(post['body']).recursiveChildGenerator() if isinstance(e,unicode)]).split(' ')[:23]),
            'content': post['body'],
            #'content': post['body'].replace('href="/media/', 'href="%s/media/' % (base, )).replace('src="/media/', 'src="%s/media/' % (base, )),
            } for post in posts]
}
open('./target/feed/index.html', 'w').write(pystache.render(feed_tmpl, attrs).encode('utf-8'))


# sitemap.xml
sitemap = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for post in posts:
    sitemap += '<url><loc>' + base + post['link'] + '</loc></url>\n'
sitemap += '</urlset>'
open('./target/sitemap.xml', 'w').write(sitemap)


# 404
error_tmpl = loader.load_template('error', 'source', 'utf-8')
attrs = deepcopy(baseattrs)
attrs['posts'] = [pystache.render(error_tmpl, None)]
open('./target/404.html', 'w').write(pystache.render(base_tmpl, attrs).encode('utf-8'))


# robots.txt
open('./target/robots.txt', 'w').write(open('./source/robots.txt').read())


# favicon.ico
open('./target/favicon.ico', 'w').write(open('./source/favicon.ico').read())


# et cetera
os.mkdir('./target/cv')
open('./target/cv/index.html', 'w').write(open('./source/cv/index.html').read())


if action == 'preview':
    import SimpleHTTPServer
    import SocketServer
    
    class PreviewServer(SocketServer.TCPServer):
        allow_reuse_address = True
    
    PORT = 8000
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    os.chdir('./target')
    httpd = PreviewServer(('', PORT), Handler)
    print "previewing at port", PORT
    httpd.serve_forever()

    
elif action == 'deploy':
    connection = boto.s3.connect_to_region('eu-west-1')
    bucket = Bucket(connection, bucketname)
    for filename in dirwalk('./target/'):
        target = filename.replace('./target', '')
        k = Key(bucket)
        k.key = target
        
        print 'uploading', target
        
        if  target.split('.')[-1] in ['jpg', 'png', 'gif', 'ico', 'css', 'js', 'txt']:
            k.set_contents_from_filename(filename, headers={'Cache-Control': 'max-age=31536000'})
        
        elif target == '/feed/index.html':
            k.set_contents_from_filename(filename, headers={'Cache-Control': 'max-age=86400', 'Content-Type': 'application/xml'})

        else:
            k.set_contents_from_filename(filename, headers={'Cache-Control': 'max-age=86400'})

elif action == 'invalidate':
    try:
        extension = '.' + sys.argv[2]
    except:
        usage()
    
    indexes = []
    for filename in dirwalk('./target/'):
        target = filename.replace('./target', '')
        if extension in target:
            indexes.append(target)
    
    print 'creating cache invalidation request for %d files ending in "%s"' % (len(indexes), extension)
    connection = CloudFrontConnection()
    connection.create_invalidation_request(cf_distribution, indexes)
