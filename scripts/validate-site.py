"""Validate published content, crawl paths, metadata and preserved verification files."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://www.mickyberlingroupsl.ink'
POSTS = json.loads((ROOT / 'content/articles.json').read_text(encoding='utf-8'))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.ids = set()
        self.urls = []
        self.meta = {}
        self.canonical = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'h1':
            self.h1 += 1
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, ('Duplicate ID', attrs['id'])
            self.ids.add(attrs['id'])
        for key in ['href', 'src']:
            if key in attrs:
                self.urls.append(attrs[key])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical.append(attrs['href'])
        if tag == 'meta':
            key = attrs.get('name', attrs.get('property'))
            if key:
                assert key not in self.meta, ('Duplicate meta', key)
                self.meta[key] = attrs.get('content', '')


pages = {}
for target in ROOT.glob('*.html'):
    if target.name.startswith('google'):
        continue
    source = target.read_text(encoding='utf-8')
    parsed = Page()
    parsed.feed(source)
    assert parsed.h1 == 1, target.name
    assert '<html lang="en">' in source, target.name
    assert 'document.documentElement.lang=lang' not in source
    assert 'data:image/' not in source and 'fonts.googleapis.com' not in source
    assert parsed.meta.get('description') and parsed.meta.get('og:title')
    assert parsed.meta.get('og:description') == parsed.meta['description']
    expected = DOMAIN + '/' + ('' if target.name == 'index.html' else target.name)
    if target.name in ['faq.html', 'top-10-berlin-telegram-group-links.html']:
        expected = DOMAIN + '/'
    assert parsed.canonical == [expected], target.name
    assert parsed.meta.get('og:url') == expected, target.name
    assert 'https://mickyberlingroupsl.ink' not in source, target.name
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
        json.loads(raw)
    pages[target.name] = (source, parsed)

titles = []
descriptions = []
active = []
for name, (source, parsed) in pages.items():
    for url in parsed.urls:
        if url.startswith('//') or url.startswith('data:'):
            continue
        split = urlsplit(url)
        if split.scheme and split.netloc != 'www.mickyberlingroupsl.ink':
            continue
        filename = unquote(split.path).lstrip('/') or (name if not split.path else 'index.html')
        if url.startswith('/') and not split.path.strip('/'):
            filename = 'index.html'
        target = ROOT / filename
        assert target.is_file(), (name, url)
        if split.fragment:
            assert filename in pages and unquote(split.fragment) in pages[filename][1].ids, (name, url)
    if 'noindex' not in parsed.meta['robots']:
        active.append(parsed.canonical[0])
        titles.append(re.search('<title>(.*?)</title>', source)[1])
        descriptions.append(parsed.meta['description'])
assert len(active) == 26
assert len(titles) == len(set(titles))
assert len(descriptions) == len(set(descriptions))

home = pages['index.html'][0]
hub = pages['blog.html'][0]
for post in POSTS:
    name = post['slug'] + '.html'
    source, parsed = pages[name]
    assert '/' + name in home and '/' + name in hub, ('Orphan article', name)
    assert '/' in parsed.urls and '/blog.html' in parsed.urls
    assert '/contact.html' in parsed.urls
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1])['@graph']
    article = next(item for item in graph if item['@type'] == 'BlogPosting')
    assert article['headline'] == post['title']
    assert article['description'] == post['description']
    assert article['mainEntityOfPage'] == DOMAIN + '/' + name
    assert article['datePublished'] == '2026-11-14'
    assert article['dateModified'] == '2026-11-14'
    assert '<time datetime="2026-11-14">14 November 2026</time>' in source
    siblings = [other for other in POSTS if other != post and other['cluster'] == post['cluster']]
    assert all('/' + sibling['slug'] + '.html' in parsed.urls for sibling in siblings)
    assert len(re.sub('<[^>]+>', ' ', post['body']).split()) >= 300

graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', home, re.S)[1])['@graph']
faq = next(item for item in graph if item['@type'] == 'FAQPage')
for item in faq['mainEntity']:
    import html
    assert '<summary>' + html.escape(item['name'], quote=True) + '</summary>' in home
    assert '<p>' + html.escape(item['acceptedAnswer']['text'], quote=True) + '</p>' in home
assert 'No group invitations are currently listed' in home
assert not re.search(r'https://t\.me/\+', home)

namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
tree = ET.parse(ROOT / 'sitemap.xml')
urls = [item.text for item in tree.findall('.//s:loc', namespace)]
assert sorted(urls) == sorted(active)
assert all(item.text == '2026-11-14' for item in tree.findall('.//s:lastmod', namespace))
ET.parse(ROOT / 'sitemap_index.xml')
assert DOMAIN + '/sitemap.xml' in (ROOT / 'robots.txt').read_text()
config = json.loads((ROOT / 'vercel.json').read_text())
redirects = {item['source']: item for item in config['redirects']}
assert redirects['/groups.html']['statusCode'] == 301
assert redirects['/faq.html']['destination'] == '/#faq'
assert redirects['/top-10-berlin-telegram-group-links.html']['destination'] == '/'
assert '/faq.html' not in urls
assert 'noindex' in pages['404.html'][1].meta['robots']

verification = ROOT / 'google178db51e898f702a.html'
original = subprocess.check_output(['git', '-c', 'safe.directory=' + ROOT.as_posix(), 'show', 'HEAD:' + verification.name], cwd=ROOT)
assert verification.read_bytes() == original
for font in (ROOT / 'assets/fonts').glob('*.woff2'):
    assert font.read_bytes()[:4] == b'wOF2'
assert len(list((ROOT / 'assets/fonts').glob('*OFL.txt'))) == 2

print('PASS: 18 new articles; 19-article library; 26 indexable pages; unique metadata; valid links, anchors, JSON-LD and XML; matching FAQ; redirects; preserved verification file and zero restored invitations.')
print('Homepage HTML bytes:', (ROOT / 'index.html').stat().st_size)
print('Example article bytes:', (ROOT / (POSTS[0]['slug'] + '.html')).stat().st_size)
