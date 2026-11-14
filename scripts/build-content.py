"""Render the reviewed article library. All outputs stay in this repository."""
from pathlib import Path
import html
import json
import hashlib
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = 'https://www.mickyberlingroupsl.ink'
DAY = '2026-11-14'
POSTS = json.loads((ROOT / 'content/articles.json').read_text(encoding='utf-8-sig'))
assert len(POSTS) == 18 and len({p['slug'] for p in POSTS}) == 18
TEMPLATE = (ROOT / 'blog.html').read_text(encoding='utf-8')
esc = lambda text: html.escape(text, quote=True)
SAFETY_NOTICE = 'Drug use can cause serious harm. This website does not promote drug sales and is not affiliated with Telegram, WhatsApp or external community operators. External content is controlled by its respective operators; we cannot guarantee its accuracy or safety.'
POPUP_CSS = (ROOT / 'content/safety-popup.css').read_text(encoding='utf-8')
POPUP_JS = (ROOT / 'content/safety-notice.js').read_bytes()
POPUP_ASSET = 'safety-notice-' + hashlib.sha256(POPUP_JS).hexdigest()[:12] + '.js'
(ROOT / 'assets' / POPUP_ASSET).write_bytes(POPUP_JS)
POPUP_HTML = '''<dialog id="safety-popup" class="safety-popup" aria-labelledby="safety-popup-title" aria-describedby="safety-popup-description">
<svg class="safety-art" viewBox="0 0 170 110" aria-hidden="true"><ellipse cx="85" cy="98" rx="63" ry="7" fill="#d7e6cb"/><circle cx="85" cy="52" r="44" fill="#d8e9c9"/><path d="M22 87V65h12v22m7 0V53h12v34m72 0V61h10v26m7 0V71h9v16" fill="none" stroke="#739275" stroke-width="3"/><path d="M54 31L85 18l31 13v23c0 21-15 33-31 40-16-7-31-19-31-40z" fill="#205331"/><path d="M72 53l9 9 20-22" fill="none" stroke="#d8f7b1" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M27 28v12m-6-6h12m108-15v10m-5-5h10" stroke="#a593bf" stroke-width="3" stroke-linecap="round"/><circle cx="139" cy="46" r="4" fill="#a593bf"/></svg>
<p class="safety-eyebrow">A moment for safety</p><h2 id="safety-popup-title">Before you continue</h2>
<div id="safety-popup-description"><p class="safety-warning">Drug use can cause serious harm.</p><p>This is an independent information website. We are not affiliated with Telegram or WhatsApp, and we do not verify or endorse third-party communities, offers or transactions.</p><p>Never share passwords, login codes or sensitive documents.</p></div>
<div class="safety-actions"><button type="button" data-safety-understand autofocus>I Understand</button><button type="button" data-safety-back>Go Back</button></div></dialog>'''


def meta(source, key, value, prop=False):
    pattern = r'<meta\s+(?:name|property)="' + re.escape(key) + r'"[^>]*>'
    tag = '<meta ' + ('property' if prop else 'name') + '="' + key + '" content="' + esc(value) + '">'
    if re.search(pattern, source):
        return re.sub(pattern, lambda match: tag, source, count=1)
    return source.replace('</head>', tag + '\n</head>', 1)


def page(slug, title, description, main, schemas, kind='website', index=True, template=None):
    source = template or TEMPLATE
    url = DOMAIN + '/' + slug
    source = re.sub(r'<title>.*?</title>', lambda match: '<title>' + esc(title) + '</title>', source, flags=re.S)
    source = re.sub(r'<link rel="canonical"[^>]*>', lambda match: '<link rel="canonical" href="' + url + '">', source)
    fields = [('description', description, False), ('robots', 'index,follow,max-image-preview:large' if index else 'noindex,follow', False), ('og:title', title, True), ('og:description', description, True), ('og:url', url, True), ('og:type', kind, True), ('og:site_name', 'Berlin Telegram Directory', True), ('twitter:title', title, False), ('twitter:description', description, False)]
    for key, value, prop in fields:
        source = meta(source, key, value, prop)
    source = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', source, flags=re.S)
    if schemas:
        data = json.dumps({'@context': 'https://schema.org', '@graph': schemas}, ensure_ascii=False).replace('<', '\\u003c')
        source = source.replace('</head>', '<script type="application/ld+json">' + data + '</script>\n</head>', 1)
    source = re.sub(r'<main[^>]*>.*?</main>', lambda match: main, source, count=1, flags=re.S)
    source = re.sub(r'<p id="site-safety-notice"[^>]*>.*?</p>', '', source, flags=re.S)
    source = source.replace('<footer>', '<footer><p id="site-safety-notice" style="max-width:900px;margin:0 auto 16px;padding:0 20px">' + esc(SAFETY_NOTICE) + '</p>', 1)
    source = re.sub(r'<style id="safety-popup-styles">.*?</style>\n?', '', source, flags=re.S)
    source = source.replace('</head>', '<style id="safety-popup-styles">' + POPUP_CSS + '</style>\n</head>', 1)
    source = re.sub(r'<dialog id="safety-popup".*?</dialog>', '', source, flags=re.S)
    source = re.sub(r'<script defer src="/assets/safety-notice-[a-f0-9]+\.js"></script>', '', source)
    source = re.sub(r'<button type="button" class="safety-reopen" data-open-safety-notice>Safety notice</button>', '', source)
    source = source.replace('</footer>', '<button type="button" class="safety-reopen" data-open-safety-notice>Safety notice</button></footer>', 1)
    source = source.replace('</body>', POPUP_HTML + '<script defer src="/assets/' + POPUP_ASSET + '"></script></body>', 1)
    return source.replace('href="favicon.svg"', 'href="/favicon.svg"')


def main(title, body, article=False):
    tag = 'article' if article else 'div'
    return '<main id="top"><section><div class="wrap"><div class="section-title"><h1>' + esc(title) + '</h1></div><' + tag + ' class="content" lang="en">' + body + '</' + tag + '></div></section></main>'


clusters = {}
for post in POSTS:
    assert re.fullmatch('[a-z0-9-]+', post['slug'])
    clusters.setdefault(post['cluster'], []).append(post)

legacy = 'how-to-choose-berlin-telegram-group.html'
for post in POSTS:
    slug = post['slug'] + '.html'
    siblings = [item for item in clusters[post['cluster']] if item != post]
    links = '<h2>Related reading</h2><ul>' + ''.join('<li><a href="/' + item['slug'] + '.html">' + esc(item['title']) + '</a></li>' for item in siblings) + '</ul>'
    body = '<p><a href="/">Home</a> / <a href="/blog.html">Blog</a> / ' + esc(post['cluster']) + '</p><p>By <a href="/about.html">Berlin Telegram Directory</a> · Published <time datetime="' + DAY + '">14 November 2026</time></p>' + post['body'] + '<p>For the current listing status and the rest of our Berlin guidance, return to the <a href="/">Berlin Telegram group links homepage</a>.</p>' + links + '<p>See an error? <a href="/contact.html">Send a correction</a>.</p>'
    schemas = [{'@type': 'BlogPosting', '@id': DOMAIN + '/' + slug + '#article', 'headline': post['title'], 'description': post['description'], 'mainEntityOfPage': DOMAIN + '/' + slug, 'datePublished': DAY, 'dateModified': DAY, 'inLanguage': 'en', 'author': {'@type': 'Organization', 'name': 'Berlin Telegram Directory', 'url': DOMAIN + '/about.html'}, 'publisher': {'@type': 'Organization', 'name': 'Berlin Telegram Directory', 'url': DOMAIN + '/about.html'}, 'articleSection': post['cluster']}, {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': DOMAIN + '/'}, {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': DOMAIN + '/blog.html'}, {'@type': 'ListItem', 'position': 3, 'name': post['title'], 'item': DOMAIN + '/' + slug}]}]
    (ROOT / slug).write_text(page(slug, post['title'], post['description'], main(post['title'], body, True), schemas, 'article'), encoding='utf-8')

# Keep the existing editorial guide, with the original publication date.
body = (ROOT / 'content/choice-guide-body.txt').read_text(encoding='utf-8')
parts = re.findall(r'<p>.*?</p>|<h[23]>.*?</h[23]>', body, re.S)
parts = [part for part in parts if not any(host in part for host in ['loganberlingroupslinks.com', 'berlingroupslinks.site', 'top-10-berlin-telegram-group-links.html'])]
body = '\n'.join(parts)
body = body.replace('Open our <a href="/#groups">Berlin Telegram Groups directory</a> and choose one invitation to inspect.', 'Read the <a href="/">homepage</a> for the current listing status and community guidance.')
body += '<p>This website currently lists no group invitations. The guidance above explains how to evaluate a community found through an organiser or another source.</p><p>Updated <time datetime="' + DAY + '">14 November 2026</time>.</p><h2>Continue reading</h2><p><a href="/joining-a-berlin-telegram-community.html">Opening an invitation carefully</a> · <a href="/check-offers-in-berlin-community-chats.html">Checking offers independently</a></p>'
title = 'How to Choose a Berlin Telegram Group You Will Actually Use'
description = 'Compare a community with your own purpose, read its rules and decide whether its conversations deserve a place in your routine.'
(ROOT / legacy).write_text(page(legacy, title, description, main(title, body, True), [{'@type': 'BlogPosting', 'headline': title, 'description': description, 'mainEntityOfPage': DOMAIN + '/' + legacy, 'datePublished': '2026-10-31', 'dateModified': DAY, 'inLanguage': 'en', 'author': {'@type': 'Organization', 'name': 'Berlin Telegram Directory', 'url': DOMAIN + '/about.html'}}], 'article'), encoding='utf-8')

# A six-cluster editorial hub, rather than another general group-link directory.
body = '<p>Practical articles for people using community chats in Berlin, Germany. These are guides to decisions and participation; they are not verified lists of live invitations. Read the <a href="/">Berlin Telegram group links homepage</a> for the current listing status.</p><p><a href="/' + legacy + '">Start with choosing a community that fits your purpose</a>.</p><ul>'
for number, label in enumerate(clusters, 1):
    body += '<li><a href="#cluster-' + str(number) + '">' + esc(label) + '</a></li>'
body += '</ul>'
for number, (label, items) in enumerate(clusters.items(), 1):
    body += '<h2 id="cluster-' + str(number) + '">' + esc(label) + '</h2>'
    for item in items:
        body += '<h3><a href="/' + item['slug'] + '.html">' + esc(item['title']) + '</a></h3><p>' + esc(item['description']) + ' <time datetime="' + DAY + '">14 November 2026</time>.</p>'
urls = [DOMAIN + '/' + legacy] + [DOMAIN + '/' + post['slug'] + '.html' for post in POSTS]
schemas = [{'@type': 'CollectionPage', 'name': 'Berlin Community Blog and Guides', 'url': DOMAIN + '/blog.html', 'description': 'Nineteen practical guides organised by the decisions Berlin community members need to make.', 'inLanguage': 'en', 'about': {'@type': 'Place', 'name': 'Berlin, Germany'}}, {'@type': 'ItemList', 'numberOfItems': len(urls), 'itemListElement': [{'@type': 'ListItem', 'position': number, 'url': url} for number, url in enumerate(urls, 1)]}]
(ROOT / 'blog.html').write_text(page('blog.html', 'Berlin Community Blog | Joining, Privacy and Local Life', 'Explore 19 Berlin community guides covering invitations, privacy, housing searches, work, study and local participation.', main('Berlin Community Blog and Guides', body), schemas), encoding='utf-8')

# Previously removed invitations remain removed. Visible answers match the FAQ schema.
faqs = [
    ('Where are the Berlin Telegram group links?', 'No group invitations are currently listed on this website. The guides explain how to evaluate links you find through recognised organisers and other sources.'),
    ('Is this an official Telegram or Berlin government website?', 'No. This is an independent editorial website. It does not represent Telegram, the City of Berlin or community administrators.'),
    ('Who are these guides for?', 'They are written in English for residents, students, newcomers and other people participating in communities in Berlin, Germany.'),
    ('Does a directory description verify a community?', 'No. Check the current destination, topic, language and rules yourself. Membership counts and group names do not establish that an offer is reliable.'),
    ('Why might an invitation stop working?', 'Administrators can revoke invitations or set expiry dates and usage limits. A request awaiting approval is different from an expired invitation.'),
    ('Can I ask for housing or job advice in any group?', 'Check its purpose and rules first. Independently verify the provider or employer before sharing documents, money or account information.'),
    ('Are the EN and DE controls separate translated pages?', 'No. They change selected navigation labels. The guides are in English; no separate German edition is currently published.'),
    ('How can I request a correction?', 'Use the contact page and include the page address, the detail you believe is wrong and a source for the correction. Do not send passwords or private documents.'),
]
hero = '<section class="hero"><div class="wrap"><div class="pill">Berlin community guides · Germany</div><h1>Berlin Telegram <span>Group Links</span></h1><p>Looking for Berlin Telegram group links? Use our guides to understand invitations, compare communities and ask useful local questions. No group invitations are currently listed on this website.</p><div class="hero-actions"><a class="btn" href="/blog.html">Explore the community guides</a><a class="btn alt" href="#faq">Common questions</a></div></div></section>'
contact_source = (ROOT / 'contact.html').read_text(encoding='utf-8')
whatsapp = re.search(r'href="(https://wa\.me/[0-9]+)"', contact_source)
assert whatsapp, 'The existing WhatsApp contact must be present before adding the button.'
whatsapp_button = '<a class="btn" href="' + whatsapp[1] + '" target="_blank" rel="noopener noreferrer" aria-label="Contact Berlin Telegram Directory on WhatsApp" data-en="Chat on WhatsApp" data-de="Auf WhatsApp schreiben">Chat on WhatsApp</a>'
hero = hero.replace('</div></div></section>', whatsapp_button + '</div></div></section>', 1)
status = '<section id="groups"><div class="wrap"><div class="section-title"><h2>Current listing status</h2><p>There are no Telegram group listings to join here at present.</p></div><div class="content" lang="en"><p>We have kept removed invitations out of the directory. An old article, a familiar community name or a topic suggestion should not be mistaken for a checked group link.</p><p>If an organiser shares an invitation elsewhere, check its current Telegram preview and read the community rules. Start with our <a href="/joining-a-berlin-telegram-community.html">invitation checklist</a> or <a href="/how-to-choose-berlin-telegram-group.html">guide to comparing communities</a>.</p></div></div></section>'
guides = '<section id="guides"><div class="wrap"><div class="section-title"><h2>Practical guides for Berlin community members</h2><p>Choose the question you need to answer, rather than joining more chats without a purpose.</p></div><div class="grid">'
for label, items in clusters.items():
    guides += '<div class="card"><h3>' + esc(label) + '</h3><ul>' + ''.join('<li><a href="/' + item['slug'] + '.html">' + esc(item['title']) + '</a></li>' for item in items) + '</ul></div>'
guides += '</div><p class="popular"><a href="/blog.html">Browse all 19 guides by topic</a>.</p></div></section>'
about = '<section id="about"><div class="wrap"><div class="section-title"><h2>What these Berlin guides cover</h2></div><div class="content" lang="en"><p>A community chat can help you ask a local question, organise study or discuss an activity. Those conversations have limits. For an official requirement, a service disruption or an organisation\'s admission rules, use the original provider\'s current information.</p><p>Our articles separate practical suggestions from documented platform features. Sources are linked where factual details matter. We do not claim that the website\'s name, article count or a community\'s membership guarantees useful advice.</p><p>Berlin is the city focus and Germany is the geographic audience. The English articles are intended to be useful to international residents as well as anyone comfortable reading English. A separate German-language site section is not currently published.</p><p>Learn <a href="/about.html">how the editorial website works</a> or <a href="/contact.html">request a correction</a>.</p></div></div></section>'
faq = '<section id="faq"><div class="wrap"><div class="section-title"><h2>Frequently asked questions</h2></div><div class="faq">' + ''.join('<details><summary>' + esc(question) + '</summary><p>' + esc(answer) + '</p></details>' for question, answer in faqs) + '</div></div></section>'
disclaimer = '<section><div class="wrap"><div class="notice"><h3>Disclaimer</h3><p>This website is independent of Telegram, the City of Berlin and community administrators. Articles provide general information, not verification of offers or personalised legal, financial or housing advice. Check important details with the relevant provider.</p></div></div></section>'
schemas = [{'@type': 'WebSite', '@id': DOMAIN + '/#website', 'name': 'Berlin Telegram Directory', 'url': DOMAIN + '/', 'inLanguage': 'en'}, {'@type': 'WebPage', 'name': 'Berlin Telegram Group Links', 'url': DOMAIN + '/', 'description': 'Berlin community guidance and the current directory listing status. No invitations currently listed.', 'inLanguage': 'en', 'about': {'@type': 'Place', 'name': 'Berlin, Germany'}}, {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': question, 'acceptedAnswer': {'@type': 'Answer', 'text': answer}} for question, answer in faqs]}]
(ROOT / 'index.html').write_text(page('', 'Berlin Telegram Group Links | Berlin Community Guides', 'Read practical Berlin Telegram community guides on joining, privacy, local questions and useful participation. No invitations currently listed.', '<main id="top">' + hero + status + guides + about + faq + disclaimer + '</main>', schemas), encoding='utf-8')

about_body = '<h2>Purpose and current status</h2><p>Berlin Telegram Directory publishes practical English-language articles about community participation in Berlin, Germany. No Telegram invitations are currently listed. The homepage explains this status rather than promising access to groups that are not present.</p><h2>Sources and editorial limits</h2><p>Articles link to official platform documentation, public organisations and original service pages where factual details matter. Practical examples are illustrative; they are not accounts of personal experience or claims that a community has been tested.</p><p>We do not invent checking dates, membership counts, rankings or an endorsement by an outside organisation. Advice about an informal conversation does not replace requirements published by a university, public authority, employer or housing provider.</p><h2>Corrections</h2><p>Use the <a href="/contact.html">contact page</a> to identify a page and the detail requiring correction. Include an authoritative source where possible. No response time or recurring invitation-checking schedule is promised.</p><h2>Independence</h2><p>This website is not affiliated with Telegram or the City of Berlin. Community administrators control their own spaces. Read the <a href="/disclaimer.html">disclaimer</a> and <a href="/privacy.html">privacy information</a> for further context.</p>'
(ROOT / 'about.html').write_text(page('about.html', 'About the Berlin Community Guides | Berlin Telegram Directory', 'Read the purpose, current listing status, source policy and correction process for this independent Berlin community website.', main('About the Berlin Community Guides', about_body), [{'@type': 'AboutPage', 'name': 'About the Berlin Community Guides', 'url': DOMAIN + '/about.html', 'inLanguage': 'en'}]), encoding='utf-8')

for slug, title, destination in [('faq.html', 'FAQ moved to the homepage', '/#faq'), ('top-10-berlin-telegram-group-links.html', 'Former invitation article moved', '/')]:
    source = page('', title, 'This older page now redirects to the homepage.', main(title, '<p><a href="' + destination + '">Continue to the current homepage information</a>.</p>'), [], index=False)
    source = source.replace('</head>', '<meta http-equiv="refresh" content="0;url=' + destination + '">\n</head>', 1)
    (ROOT / slug).write_text(source, encoding='utf-8')

utilities = [('contact.html', 'Contact and Corrections | Berlin Telegram Directory', 'Find the existing contact route for corrections, removal requests and questions about this Berlin community website.', 'ContactPage'), ('privacy.html', 'Privacy Policy | Berlin Telegram Directory', 'Read how this website describes privacy, external services and information shared when contacting the editor.', 'WebPage'), ('terms.html', 'Terms of Use | Berlin Telegram Directory', 'Read the terms for using this independent Berlin community information website.', 'WebPage'), ('disclaimer.html', 'Editorial Disclaimer | Berlin Telegram Directory', 'Understand the limits of general community information, external links and the independence of this website.', 'WebPage')]
for slug, title, description, kind in utilities:
    target = ROOT / slug
    source = target.read_text(encoding='utf-8')
    current_main = re.search(r'<main[^>]*>.*?</main>', source, re.S)[0]
    if slug == 'disclaimer.html':
        current_main = main('Disclaimer', '<h2>Safety notice</h2><p>Drug use can cause serious harm. This website does not promote drug sales or provide a service for arranging prohibited transactions.</p><h2>Independent website</h2><p>We are not affiliated with Telegram, WhatsApp, the City of Berlin or external community operators. Third-party communities are controlled by their respective administrators.</p><h2>Limits of the information</h2><p>The articles provide general information. We do not operate external communities or verify their members, messages, offers or transactions. We cannot guarantee the accuracy, availability or safety of third-party content.</p><h2>Report a concern</h2><p>Use our <a href="/contact.html">contact page</a> for a correction or removal request. For conduct within a third-party community, use its moderation or reporting process. Do not send passwords, login codes or identity documents.</p>')
    target.write_text(page(slug, title, description, current_main, [{'@type': kind, 'name': title, 'url': DOMAIN + '/' + slug, 'inLanguage': 'en'}], template=source), encoding='utf-8')

# Obsolete redirect sources never appear in the sitemap.
active = ['', 'about.html', 'blog.html', 'contact.html', 'disclaimer.html', 'privacy.html', 'terms.html', legacy] + [post['slug'] + '.html' for post in POSTS]
namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', namespace)
root = ET.Element('{' + namespace + '}urlset')
for slug in active:
    item = ET.SubElement(root, '{' + namespace + '}url')
    ET.SubElement(item, '{' + namespace + '}loc').text = DOMAIN + '/' + slug
    ET.SubElement(item, '{' + namespace + '}lastmod').text = DAY
ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
(ROOT / 'sitemap_index.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="' + namespace + '"><sitemap><loc>' + DOMAIN + '/sitemap.xml</loc><lastmod>' + DAY + '</lastmod></sitemap></sitemapindex>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /scripts/\n\nSitemap: ' + DOMAIN + '/sitemap.xml\n', encoding='utf-8')
(ROOT / '404.html').write_text(page('404.html', 'Page Not Found | Berlin Telegram Directory', 'This page could not be found. Return to the homepage or browse the published community guides.', main('Page not found', '<p>The address may have changed. Visit the <a href="/">homepage</a> or <a href="/blog.html">browse the community guides</a>.</p>'), [], index=False), encoding='utf-8')

lines = ['# Berlin topical map', '', 'Prepared 14 November 2026. Repository: ubaid164/berlin-directory. Site: ' + DOMAIN + '/.', '', '## Scope and intent ownership', '', 'Homepage owns Berlin Telegram group links. Target geography is Berlin, Germany; the actual content language is English. No search volumes, difficulty measurements or ranking promises are asserted. No separate German URLs exist, so no hreflang alternates are invented.', '', 'No invitations are currently listed. This is a substantive gap for users seeking live group links, not something article volume can conceal. Do not restore removed groups without the owner\'s instruction and real destination checks.', '', '## Published clusters', '', '| Cluster | Distinct query / intent | Article URL |', '| --- | --- | --- |']
for post in POSTS:
    lines.append('| ' + post['cluster'] + ' | ' + post['keyword'] + ' | /' + post['slug'] + '.html |')
lines += ['', 'Existing guide retained: /' + legacy + '. The old numbered directory article redirects to the homepage.', '', '## Link structure', '', 'Homepage -> all 18 new articles and the existing choice guide. Blog -> all 19 articles by cluster. Each new article -> homepage, hub, two sibling guides and correction page. Keep descriptive anchors and avoid a second generic top-links page.', '', '## Source policy', '', 'Use the official sources linked inside the articles. Editorial examples are hypothetical; do not present them as real case studies. Check any new price, schedule, eligibility or legal claim before publishing. Do not add dealer contacts or controlled-substance sales content.']
(ROOT / 'TOPICAL-MAP.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('Built 18 new articles, one revised guide, six-cluster hub and 26-URL sitemap.')
for post in POSTS:
    print(post['slug'], len(re.sub('<[^>]+>', ' ', post['body']).split()), 'words')
