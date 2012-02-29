#!/usr/bin/env python


import sys, os, datetime, time, json, uuid, pystache, SimpleHTTPServer, SocketServer
from lxml import etree


def usage():
    print 'usage: %s [preview|deploy]'
    exit()

try:
    action = sys.argv[1]
except:
    usage()
    

datetimefmt_in = '%Y-%m-%d %H:%M:%S'
datetimefmt_out = '%B %e, %Y'

bucket = 'www.j-gw.com'
base = '/'


posts = []  # individual posts, sorted form newest to oldest; items below refer to post's 'id's
site = {
    'posts': [],       # same list as above, cut into chunks of ten
    'categories': {},  # key is a category, contains a list of post ids (chunked)
    'tags': {},        # key is a tag, contains a list of post ids (cunked)
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
            'link': '%s%04d/%02d/%s/' % (base, published.year, published.month, post.xpath('slug')[0].text),
            'published': published,
            'category': post.xpath('category')[0].text,
            'tags': [tag.text for tag in post.xpath('tags')[0]],
            'slug': post.xpath('slug')[0].text,
            'title': post.xpath('title')[0].text,
            'body': post.xpath('body')[0].text,
            })
#posts.sort(key = lambda post: post['published'], reverse=True)


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
    post['published'] = post['published'].strftime(datetimefmt_out)
    post['title'] = post['title'].replace('"', '')


loader = pystache.Loader()
base_tmpl = loader.load_template('base', 'source', 'utf-8')
post_tmpl = loader.load_template('post', 'source', 'utf-8')
list_tmpl = loader.load_template('list', 'source', 'utf-8')

recent = pystache.render(list_tmpl, { 'items': [{ 'link': post['link'], 'title': post['title']  } for post in posts[:5]] }).encode('utf-8')
print recent 

archives = []
for year in site['years']:
    for month in site['years'][year]['months']:        
        count = 0
        for parts in site['years'][year]['months'][month]:
            count += len(parts)
        archives.append({
                'link': '/%s/%s/' % (year, month),
                'title': '%s %s' % (month, year),
                'count': '%s' % count
                })
archives = pystache.render(list_tmpl, { 'items': archives } ).encode('utf-8')

categories = pystache.render(list_tmpl, { 'items': [{ 'link': '/category/%s/' % (category, ), 'title': category } for category in site['categories']] }).encode('utf-8')

if action == 'preview':
    
    class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
        def do_GET(self):
            
            parts = self.path.split('/')[1:]
            
            # root
            if len(parts) < 2:
                self.send_response(200)
                self.send_header('Content-type','text/html;charset=utf8')
                self.end_headers()
                attrs = {
                    'base': base,
                    'recent': recent,
                    'archives': archives,
                    'categories': categories,
                    'posts': [pystache.render(post_tmpl, post) for post in posts[:10]]
                    }                
                self.wfile.write(pystache.render(base_tmpl, attrs).encode('utf-8'))
                return

            # media
            elif parts[0] == 'media':
                self.send_response(200)
                filename = parts[-1]
                extension = filename.split('.')[1]
                if extension == 'jpg':
                    self.send_header('Content-type','image/jpg')
                elif extension == 'png':
                    self.send_header('Content-type','image/png')
                self.end_headers()
                self.wfile.write(open('./source/' + '/'.join(parts)).read())
            
            # asset
            elif parts[0] == 'asset':
                self.send_response(200)
                filename = parts[-1]
                extension = filename.split('.')[1]
                if extension == 'css':
                    self.send_header('Content-type','text/css')
                elif extension == 'js':
                    self.send_header('Content-type','application/javascript')
                self.end_headers()
                self.wfile.write(open('./source/' + '/'.join(parts)).read())
            

    server = SocketServer.TCPServer(("", 8080), Handler)
    server.serve_forever()
    
#
# start rendering site, first the front page
#
# attrs = {
#     'base': base,
#     'posts': [pystache.render(post_tmpl, post) for post in posts[:5]]
#     }

# print pystache.render(base_tmpl, attrs)
