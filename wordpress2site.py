#!/usr/bin/env python


import sys, os, datetime, json
from lxml import etree
from lxml.html.soupparser import fromstring

source = etree.parse('./source/asyncfi.wordpress.2012-02-19.xml').getroot()


site = {
    'posts': []
    }
for item in source.xpath('channel/item'):
    
    tags = []
    for tag in item.xpath('category[@domain="post_tag"]'):
        tags.append(tag.get('nicename'))
    
    body = item.xpath('content:encoded', namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'})[0].text
    
    body = body.replace('https://async.fi/wp-content/uploads/', '/media/')
    body = body.replace('http://async.fi/wp-content/uploads/', '/media/')
    
    site['posts'].append({
            'published': item.xpath('wp:post_date_gmt', namespaces={'wp': 'http://wordpress.org/export/1.1/'})[0].text,
            'slug': item.xpath('wp:post_name', namespaces={'wp': 'http://wordpress.org/export/1.1/'})[0].text,
            'title': item.xpath('title')[0].text,
            'tags': tags,
            'category': item.xpath('category[@domain="category"]')[0].get('nicename'),
            'body': body
        })


siteposts = etree.Element('posts')

for post in site['posts']:
    sitepost = etree.SubElement(siteposts, 'post')
    etree.SubElement(sitepost, 'published').text = post['published']
    etree.SubElement(sitepost, 'slug').text = post['slug']
    etree.SubElement(sitepost, 'title').text = post['title']
    etree.SubElement(sitepost, 'category').text = post['category']
    posttags = etree.SubElement(sitepost, 'tags')
    for tag in post['tags']:
        etree.SubElement(posttags, 'tag').text = tag

    etree.SubElement(sitepost, 'body').text = etree.CDATA(post['body'])

print(etree.tostring(siteposts, pretty_print=True))
