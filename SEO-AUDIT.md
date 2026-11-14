# Berlin directory SEO work

Prepared 14 November 2026. Repository: ubaid164/berlin-directory. Website: https://www.mickyberlingroupsl.ink/.

## Implemented

- Eighteen original articles in six clusters, with the existing community-choice guide retained and corrected: nineteen articles total.
- Homepage owns the broad Berlin Telegram group links query. Topic-specific pages answer distinct practical questions.
- Homepage and blog hub link to every new article. Each new article links to the homepage, hub, correction page and two guides within its cluster.
- Unique title, description, social metadata and canonical URL for every indexable page.
- BlogPosting and breadcrumb JSON-LD on new articles; CollectionPage and ItemList on the blog; visible homepage FAQ answers match its FAQPage data.
- Live host was observed to redirect from the apex to www. Canonicals, schema URLs, robots and both sitemaps now consistently use www.
- Existing /groups.html 301 redirect retained. /faq.html redirects to the homepage FAQ. The obsolete numbered invitation article redirects to the homepage. Neither obsolete source is in the sitemap.
- Decorative background extracted byte-for-byte into a shared, content-hashed WebP. The original typography uses locally served WOFF2 fonts with their SIL Open Font Licenses, swap rendering and Latin font preloads.
- Long-lived immutable cache headers apply to versioned assets. No Google Fonts stylesheet import remains.
- English is the document language. EN/DE controls only change navigation labels. No fictional translated URLs, hreflang alternates, local business address or business-profile eligibility are claimed.
- Existing Google verification file and well-known files preserved. No removed Telegram invitations restored.
- A noindex custom 404 page is provided; the server should return an actual 404 for missing routes, rather than a homepage rewrite.

## Important editorial limitation

The site currently has no group invitations. The homepage and old copy previously promised links that were absent; these statements have been corrected. More articles cannot substitute for the live directory inventory a link-seeking visitor expects. Do not fabricate group names, activity levels, checking dates or destinations to fill this gap.

The prepared articles concern legitimate community participation. Promotional cross-links for drug-sales or dealer-group searches were not added. No ranking is guaranteed. Keyword candidates reflect editorial intent, not measured search volume or difficulty.

## Sources reviewed

- Telegram FAQ: https://telegram.org/faq
- Official apps: https://telegram.org/apps
- Invitation mechanics: https://core.telegram.org/api/invites
- Channels FAQ: https://telegram.org/faq_channels
- Berlin Service Portal: https://service.berlin.de/
- Berlin districts: https://www.berlin.de/en/districts/
- Berlin events: https://www.berlin.de/en/events/
- Berlin volunteer agencies: https://www.berlin.de/sen/kultgz/engagement/freiwilligenagenturen-1642030.php
- BVG disruption information: https://www.bvg.de/en/connections/traffic-news
- BVG route planning: https://www.bvg.de/en/connections/connection-search
- Housing information: https://www.stw.berlin/en/housing/
- Official job search: https://www.make-it-in-germany.com/en/working-in-germany/job-listings
- Language tandems: https://www.sprachenzentrum.fu-berlin.de/en/slz/tandem/index.html
- IHK Berlin: https://www.ihk.de/berlin/english
- Google's people-first guidance: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google's multilingual guidance: https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites

Practical examples are illustrative and independently written for this website; the articles do not claim personal experience. No transient prices, member counts, local rankings, eligibility decisions or event dates are asserted.

## Checks that require live deployment or account data

Passing local validation is not a statement that all SEO issues are cleared.

- Confirm the deployed article pages, canonical host, 301 rules, asset cache headers and unknown-route 404 response after pushing.
- Search Console access is required to verify Google's selected canonical, indexing status, manual actions and query/country/device performance. Use Germany for the country dimension; Berlin is the city focus.
- Submit the www sitemap and inspect representative pages. Sitemap inclusion does not guarantee indexing.
- Run mobile PageSpeed Insights after deployment; measure real LCP, INP and CLS where field data is available. No improved timings have been invented.
- Review actual query demand before expanding. A full German edition would need complete German content and reciprocal language annotations, rather than just changing navigation labels.
- Review the privacy and terms text against actual operational practices with appropriate professional advice where necessary. Metadata work is not legal certification.

## Maintenance

Edit content/articles.json, then run `python scripts/build-content.py` and `python scripts/validate-site.py`. Rebuilding uses the saved original body of the existing choice guide so repeated builds do not append duplicate updates. All pages are published immediately; there is no scheduler or deploy-hook secret.
