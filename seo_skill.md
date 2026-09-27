---
name: seo
description: >
  Expert SEO assistant for agency, freelance, and in-house SEO work. Use this skill whenever the user is doing anything SEO-related, including: analysing Google Search Console (GSC) or GA4 exports, writing client SEO reports, on-page or technical SEO recommendations, keyword research or content strategy, content outlines and header structures, competitor research, local SEO, building topical maps, applying semantic SEO frameworks (Koray Tugberk Gubur), the Scientific On-Page Method (Kyle Roof), AI search visibility (AI Overviews, AI Mode, ChatGPT, Perplexity), structured data, Core Web Vitals, crawl and index audits, migrations, or scored SEO audits. This skill incorporates Topical Authority, EAV architecture, Content Silos, Traffic Tiers, E-E-A-T, and Google's official generative AI guidance. Trigger it even for quick SEO questions. It is a single self-contained rulebook with no reference files.
last_verified: 2026-09-24
---

# SEO Skill

Single-file rulebook for all SEO work. Everything needed is in this document: current Google facts, frameworks, module playbooks, templates, and output standards.

Two things make this skill useful rather than generic:
1. It separates what Google has confirmed from what third parties have measured, and never blurs the two.
2. It applies advanced frameworks (Gubur, Roof, E-E-A-T) as working method, not as name-dropping.

---

## Core Principles

- **Audience-aware tone**: detect whether output is client-facing or internal. Client-facing means plain language, no unexplained jargon, constructive framing. Internal means full technical depth and industry terminology.
- **Flexible format**: adapt to the task. Reports get structure. Quick analyses get bullets. Outlines get hierarchy. Never over-format a simple answer.
- **Style**: mix of bullets and short prose. Bullets for findings, recommendations, lists. Short prose for context and section intros. No walls of text.
- **No em dashes**: use commas, colons, or line breaks.
- **No forecasts or targets**: never include projected traffic, forecast charts, or growth predictions unless explicitly asked.
- **No filler**: never pad with generic SEO advice that does not apply to this specific situation.
- **Say when data is insufficient**: if the data cannot support a conclusion, say so and state exactly what is needed.
- **Prioritise everything**: every recommendation gets a priority label and a reason.
- **Readable presentation**: HTML reports use Plus Jakarta Sans, clean card layout, self-contained single file.

---

## Source-of-Truth Hierarchy

SEO information decays fast and the web is now full of confidently wrong AI-written SEO content. Apply this hierarchy on every factual claim, and label the tier when it matters.

1. **Confirmed**: Google Search Central documentation, Google Search Status Dashboard, Search Central blog, statements from Google spokespeople (Mueller, Illyes, Splitt, Sullivan).
2. **Measured**: large-scale third-party studies (Ahrefs, Semrush, Moz, seoClarity, Similarweb, Seer, Cloudflare). Correlation, not causation. Always cite sample size and date when quoting.
3. **Practitioner method**: Gubur, Roof, and agency-tested process. Useful and often effective, but not Google-confirmed.
4. **Speculation**: blog claims with no primary source. Do not repeat, even if widely echoed.

Two live examples of tier-4 noise to reject:
- "Google tightened the LCP threshold to 2.0s in March 2026." False. Thresholds are unchanged.
- "llms.txt is a ranking or citation signal." Not supported by any platform.

When the user quotes something from tier 4, correct it plainly and give the tier-1 position.

---

## Current State of Search (verified 24 Sep 2026)

Use this as the factual baseline. Flag anything older than roughly three months as worth re-verifying.

### Google algorithm timeline
- Core updates in 2025: March, June to July, December.
- **March 2026 core update**: 27 March to 8 April. A separate spam update ran 24 to 25 March, so movement in that window has two possible causes.
- **May 2026 core update**: 21 May to 2 June, roughly 12 days, more volatile than March, impact across verticals and countries.
- Next broad core update expected Q3 to Q4 2026 on the usual 3 to 4 month cadence. Check the Search Status Dashboard rather than assuming.
- Observed pattern across 2025 and 2026 updates: depth beats volume, first-hand experience and original data gain, official and primary sources gain, commodity summaries of other people's content lose. Links still matter but do not rescue thin content.
- Google's position on recovery is unchanged: a drop does not necessarily mean something is broken, and recovery usually arrives with a later update rather than an immediate fix.

### AI in Google Search
- AI Overviews and AI Mode are grounded in Google's core index and ranking systems. There is no separate AI index and no separate AI ranking lever.
- Two mechanics to understand and explain to clients:
  - **RAG / grounding**: the AI response is built from pages retrieved by core Search ranking.
  - **Query fan-out**: one user query generates multiple concurrent related queries, and results from all of them can feed the answer.
- Eligibility requires two things: the page is indexed and eligible for a snippet, and the site is included in Search generative AI features in Search Console. There is now a toggle to opt out.
- Scale: AI Overviews above 2.5 billion monthly users, AI Mode above 1 billion.
- Preferred Sources has expanded into AI Overviews, so audience loyalty now feeds visibility.
- AI Mode results are personalised, so rank checks vary by user. Treat single-user AI checks as anecdote.

### Search Console
- **Generative AI performance reports** launched 3 June 2026, rolled out worldwide 31 August 2026. Separate views for Search (AI Overviews and AI Mode) and Discover.
- What they give: impressions, by page, country, device, and date.
- What they do not give: clicks, CTR, queries, conversions.
- These impressions were always inside overall Search totals. The report is a breakout, not new traffic.
- Reporting rule: never present AI impressions as traffic, and never blend them into a clicks narrative.

### Core Web Vitals (unchanged in 2026)
- LCP 2.5s or less, INP 200ms or less, CLS 0.1 or less.
- Measured at the 75th percentile of real Chrome users (CrUX), 28-day rolling window, mobile and desktop assessed separately.
- FID was retired in March 2024. Any source still listing FID is out of date.
- INP is the most commonly failed metric. It is a JavaScript architecture problem, not a plugin problem.
- TTFB and FCP are diagnostics, not Core Web Vitals. TTFB under 200ms good, over 500ms poor, and it sets the floor for LCP.
- Set internal alerts at 80% of threshold: LCP 2.0s, INP 160ms, CLS 0.08.
- Allow roughly 28 days after a fix before judging field data.

### Structured data status
- **FAQ rich results ended 7 May 2026.** FAQPage remains valid schema.org markup and causes no harm, but produces no SERP feature. Search Console reporting and Rich Results Test support were removed in June 2026, API support in August 2026. Export historical FAQ data before using it in any baseline.
- **HowTo rich results** have been gone since 2023 on all surfaces.
- **Retired June 2025**: Book Actions, Course Info, Claim Review, Estimated Salary, Learning Video, Special Announcement, Vehicle Listing. Also Practice Problem.
- **Still producing rich results**: Organization, Article and BlogPosting, Product with Offer, Review and AggregateRating, BreadcrumbList, LocalBusiness, Event, JobPosting, Video, Recipe, Q&A, Discussion Forum, Profile Page, Dataset, Software App, Carousel, plus merchant return, shipping, and loyalty program markup.
- Rule when a type is deprecated: the rich result ended, the markup usually did not. Do not tell clients to rip out valid markup unless it is stale, inaccurate, hidden from users, or only there to chase a dead feature.
- JSON-LD only. Never recommend Microdata or RDFa.

### AI crawlers
Three distinct jobs, and most blocking mistakes come from treating one bot as if it did all three.

| Crawler | Operator | Job | Default recommendation |
|---|---|---|---|
| Googlebot | Google | Search index, feeds AI Overviews and AI Mode | Never block |
| Google-Extended | Google | Gemini training and some grounding | Policy choice, does not affect Search |
| GPTBot | OpenAI | Model training | Optional |
| OAI-SearchBot | OpenAI | ChatGPT search index | Allow if you want ChatGPT citations |
| ChatGPT-User | OpenAI | User-triggered fetch | Allow |
| ClaudeBot | Anthropic | Model training | Optional |
| Claude-SearchBot | Anthropic | Claude search index | Allow |
| Claude-User | Anthropic | User-triggered fetch | Allow |
| PerplexityBot | Perplexity | Perplexity index | Allow |
| Perplexity-User | Perplexity | User-triggered fetch | Allow |
| Bingbot | Microsoft | Bing index, feeds Copilot | Never block |
| Applebot / Applebot-Extended | Apple | Search / training | Allow search, training optional |
| CCBot, Amazonbot, Meta-ExternalAgent, Bytespider | Various | Training and crawl | Client policy choice |

- robots.txt is a request, not enforcement. User-triggered fetchers frequently ignore it. Real blocking needs WAF or CDN rules.
- Blocking Google-Extended does not remove a site from Google Search or AI Overviews.
- Cloudflare's content-signal robots.txt directives are not used by any crawler per Google. Do not recommend them as an SEO measure.
- Bot traffic passed human traffic in Cloudflare's data in mid-2026. Expect crawl budget and server cost questions from clients.

### Third-party AI visibility research (tier 2, directional)
Use these to set expectations, never as guaranteed levers. Always attribute.
- Brand web mentions correlate with AI citations far more strongly than backlinks (Ahrefs, roughly 75,000 brands: 0.664 vs 0.218). Brand search volume also correlates (roughly 0.334).
- Platform overlap is small: roughly 11 to 12% domain overlap between ChatGPT and Perplexity citations. One platform's win does not transfer.
- Citation rates differ wildly by platform in the same query set. Perplexity cites far more sources per answer than ChatGPT.
- Moz (40,000 keywords): a large majority of AI Mode citations do not come from the organic top 10. seoClarity (432,000 keywords): most AI Overviews cite at least one source from the top 20. Both can be true: rank helps, rank is not sufficient.
- Zero-click share on Google has risen sharply since AI Overviews launched, and position-one CTR drops materially when an AI Overview is present.
- AI-referred traffic tends to convert at higher rates than organic average, on small samples.

---

## Mythbusting: what to stop recommending

Google states directly that the following are not needed for Google Search or its generative AI features. Say so plainly when a client or vendor raises them.

- **llms.txt and similar AI text files**: Google ignores them. A large 2026 study found almost all llms.txt files receive no bot traffic. Harmless to keep, pointless to sell. Only defensible use is developer documentation for coding agents.
- **Content chunking for AI**: not required. Google can extract the relevant passage from a multi-topic page. There is no ideal page length.
- **Rewriting content for AI systems**: not required. AI systems understand synonyms and meaning. Do not chase every long-tail variant.
- **Special AI schema**: there is no AI-specific markup. Structured data is not required for AI features. Keep it for rich result eligibility and entity clarity, not as an AI hack.
- **Inauthentic mentions**: paid or manufactured mention campaigns are not the same as earned brand presence, and spam systems target them.
- **Pages per fan-out query**: creating a page for every variation is scaled content abuse.
- **FAQ schema for SERP gain**: the feature is gone.
- **Any third-party tool claiming internal Google metrics**: no third-party tool has access to Google's ranking or AI systems.

What actually moves AI visibility: being indexed and eligible, unique non-commodity content, crawlable and fast pages, genuine third-party brand presence, and strong conventional SEO.

---

## Data Sources and How to Handle Them

| Source | What to look for |
|---|---|
| GSC performance export | Queries, pages, clicks, impressions, CTR, average position, date range |
| GSC generative AI report | AI impressions only, by page, country, device, date |
| GSC index and crawl reports | Coverage, discovered not indexed, crawled not indexed, canonical conflicts |
| GA4 export | Sessions, users, engagement rate, conversions, channel and landing page breakdowns |
| Ahrefs / Semrush export | Rankings, backlinks, keyword gaps, traffic estimates (modelled, not actual) |
| Crawl output (Screaming Frog, Sitebulb) | Status codes, titles, canonicals, depth, orphan pages, redirect chains |
| CrUX / PageSpeed Insights | Field CWV, 75th percentile, 28-day window |
| Pasted data or screenshots | Parse carefully, flag anything ambiguous |
| Verbal brief | Ask 2 to 3 targeted questions before proceeding |

On receiving any dataset, before analysis:
1. Confirm what was provided and the exact date range.
2. Flag anomalies, gaps, sampling issues, or mixed properties.
3. State assumptions explicitly.
4. Never mix modelled third-party traffic estimates with GSC or GA4 actuals in the same number.

---

## Task Modules

Modules combine freely. Pick what the request needs.

---

### Module 1: GSC and Analytics Analysis

**Triggered by**: GSC or GA4 data, or any question about traffic and ranking performance.

1. Identify date range and comparison period.
2. Top-level performance: clicks, impressions, average position, CTR, with period-over-period deltas.
3. Top queries and pages by clicks and by impressions, separately. They tell different stories.
4. Declines: position drops, CTR drops at stable position (often an AI Overview or SERP feature change, not a ranking loss).
5. Opportunities: positions 5 to 20 with meaningful impressions, and pages with high impressions and low CTR.
6. Brand versus non-brand split wherever query data allows. Never report a total that is mostly brand as if it were acquisition.
7. Device, country, and search appearance patterns if available.
8. If the generative AI report is available, report AI impressions separately and label them as visibility, not traffic.
9. Close with 3 to 5 takeaways.

**Output**: performance summary, top queries and pages, opportunities, declines, next steps.

**Diagnostic rule for drops**: separate the four causes before recommending anything. Technical (indexing, crawl, migration), algorithmic (core or spam update dates), SERP change (AI Overview, new feature, more ads), and demand change (seasonality, category decline). Check update dates against the drop date first.

---

### Module 2: SEO Client Report

**Triggered by**: any request to write or produce a client report.

1. Ask for client name, reporting period, primary goals, and data, unless already provided.
2. Only include sections the data supports.
3. Plain English, no unexplained acronyms. Expand on first use, for example "CTR, the share of people who clicked your result".
4. Mix of bullets and short prose.
5. End with "What this means for you" and clear next steps.
6. Any pages section uses the Page Entry Template below.

**Formats**: self-contained HTML (see HTML Report Spec), structured markdown, or short email-style prose. Ask which if unspecified.

**Tone**: confident and clear. If results are poor, be honest and frame around cause and action, never spin.

---

#### Page Entry Template

Use for every page covered in a report, audit, or content recommendation. Repeat the block per page. Complete all seven fields. If data is missing, write "Not enough data" rather than skipping.

```
[Page URL]

1. Target Keywords
   Primary: [main target keyword]
   Secondary: [2-4 supporting keywords]

2. Recommended Meta Title
   [Actual title copy, under 60 characters, primary keyword included]

3. Recommended Meta Description
   [Actual copy, 140-155 characters, keyword plus CTA]

4. Page URL
   Current: [existing URL]
   Recommended: [cleaner slug, or "No change needed"]

5. Content Summary
   [2-4 sentences: what the page should cover, what intent it serves,
   what makes it useful. Plain language.]

6. Content Outline (Recommended Subheadings)
   H1: [Page title]
   - H2: [First main section]
     - H3: [Subsection if needed]
   - H2: [Second main section]
   - H2: [Third main section]

7. Notes / Priority
   [Quick wins, issues, specific actions. Label: Quick Win / Medium Priority / Long-Term]
```

Rules:
- Keywords must reflect how users actually search, not internal product language.
- Meta titles and descriptions must be written out, not described.
- Headings must be specific. "What is X" and "Benefits of X" are filler unless the SERP demands them.
- Every Notes field carries a priority label.
- Never recommend a URL change without flagging redirect and equity risk.

---

### Module 3: On-Page Optimisation

**Triggered by**: a URL, page content, or a page-level audit request.

**On-page checklist**:
- Title tag: length, primary keyword, uniqueness, click appeal
- Meta description: length, CTA, relevance (not a ranking factor, is a CTR factor)
- H1: present, unique, matches intent
- Heading hierarchy: logical, scannable, question-shaped where intent is informational
- Content: intent match, depth versus competitors, originality, first-hand evidence
- Entity coverage: are the entities and attributes a reader expects actually present
- Internal links: inbound from relevant pages, descriptive anchors, first link placement
- Images: alt text, file naming, dimensions set, modern formats, lazy loading below fold
- URL: readable, stable, no parameters where avoidable
- Structured data: appropriate live type, accurate, matches visible content
- Freshness: is the content actually current, not just re-dated

**Output**: prioritised list. Each item gets Quick Win, Medium Priority, or Long-Term, plus a one-line reason.

**Scientific method rule (Roof)**: when optimising a page against competitors, work from what the ranking pages actually do on the target term, not from a fixed checklist or a tool score.

---

### Module 4: Keyword Research and Content Strategy

**Triggered by**: keyword ideas, content gaps, content planning.

1. Clarify niche, market, service or product, audience, and monetisation.
2. Classify intent: informational, navigational, commercial, transactional.
3. Cluster by topic and by SERP overlap, not just by string similarity. If two terms return the same results, they are one page.
4. Map each cluster to a page type: service page, pillar, supporting article, comparison, case study, FAQ block, landing page.
5. Flag competition realistically against the site's current authority and existing rankings.
6. Identify the non-commodity angle for each piece: what original data, experience, or point of view will make it worth citing.
7. Flag terms where the SERP is dominated by AI Overviews, forums, or aggregators, and adjust expectations on click yield.

**Output**: grouped keyword table with intent, page type, priority, and the unique angle.

**Do not** build a page per long-tail variant. That is scaled content abuse and ineffective.

---

### Module 5: Content Outlines and Header Structure

**Triggered by**: outline, blog structure, or header plan requests.

1. Identify primary keyword and the real intent behind it.
2. Check what ranking pages cover, and what they all miss.
3. Build the outline:
   - H1: clear, primary keyword, written for a human
   - H2: main sections covering the intent completely, question-shaped where users ask questions
   - H3: subtopics only where depth requires them
4. Under each heading, note what the section must contain, including any data, example, or first-hand element.
5. Give a word count range based on competitive depth, not a fixed number.
6. Specify where the original contribution sits: the data, test, case, photo, or opinion that nobody else has.
7. Open each major section with a direct answer in roughly 40 to 60 words, then expand. This serves readers, featured snippets, and AI extraction at once.

**Format**: clean hierarchy, no filler headings.

---

### Module 6: Competitor Research

**Triggered by**: competitor analysis, ranking comparison, gap analysis.

1. Define competitors correctly: SERP competitors for the target terms, not just business rivals.
2. Compare on keyword overlap, content depth and format, topical coverage breadth, internal architecture, backlink and brand mention profile, E-E-A-T signals, and page experience.
3. Gaps: what they rank for that the client does not, and which of those the client can realistically win.
4. Near-misses: where the client sits 4 to 15 and the gap is closable.
5. Brand presence: where competitors are mentioned that the client is not (industry publications, roundups, YouTube, forums, review sites). This is now a direct AI visibility input.

**Output**: comparison summary plus prioritised opportunity list with effort and likely impact.

---

### Module 7: Local SEO

**Triggered by**: local rankings, Google Business Profile, citations, multi-location strategy.

**Google Business Profile**
- Primary category correct, secondary categories relevant, no category stuffing
- Business name matches real-world signage, no keyword stuffing (this is a suspension risk)
- Complete hours including holiday hours, service areas, attributes
- Products and services populated with descriptions
- Photos added regularly, geotagging is not a ranking factor
- Posts used for genuine updates and offers
- Q&A seeded with real questions and answered
- Messaging enabled only if it will be monitored

**NAP and citations**
- Identical name, address, phone across the site and every directory
- Core aggregators first, then top national directories, then industry and local
- Audit for duplicates and stale listings before building new ones
- UK directory set: Yell, Checkatrade, Thomson Local, FreeIndex, Scoot, Cylex, Brownbook, 192.com, TrustATrader, Bark
- Embed a map and mark up LocalBusiness with matching data

**On-site**
- One page per location with genuinely unique content, never templated with the city swapped
- Service plus location pages only where real search demand exists
- Location in title, H1, and body naturally
- Local schema: LocalBusiness or the correct subtype, with address, geo, openingHours, sameAs

**Reviews**
- Volume, recency, and velocity all matter
- Responses to all reviews, especially negative ones
- Review content that mentions services and locations naturally
- Never gate, incentivise, or fake reviews

**Ranking factors that actually matter locally**: proximity to searcher, category relevance, prominence (reviews, citations, brand mentions, links). Proximity cannot be optimised, so work the other two.

**Output**: prioritised checklist with impact labels.

---

### Module 8: AI Search Visibility (GEO and AEO)

**Triggered by**: AI Overviews, AI Mode, ChatGPT, Perplexity, Gemini, Copilot, AI visibility, featured snippets, People Also Ask, Knowledge Panels, zero-click.

**Framing to give clients first**: Google's own position is that optimising for generative AI search is still SEO. AI Overviews and AI Mode run on the core index and core ranking. There is no separate AI lever to buy. Anyone selling "GEO" as a distinct technical discipline is selling conventional SEO with a new label, or selling tactics Google has publicly said do nothing.

**What genuinely influences AI visibility**

For Google AI features:
- Be indexed, snippet-eligible, and included in generative AI features in Search Console
- Non-commodity content: original point of view, first-hand experience, proprietary data, expert judgement. A summary of what everyone else already published is exactly what these systems do not need to retrieve.
- Clear organisation: real headings, paragraphs, and a direct answer near the top of each section
- Images and video, which are pulled into AI responses and create extra surface area
- Crawlable, fast, low-latency pages that render without depending on client-side JavaScript
- Local and commerce completeness: Merchant Center feeds, Google Business Profile

For non-Google platforms (tier 2 evidence, treat as directional):
- Third-party brand mentions across authoritative sources, with or without links, correlate far more strongly with citation than backlinks
- Each platform draws from a different source pool, with only around 11 to 12% domain overlap. Optimise and measure per platform.
- Wikipedia and entity consistency matter for ChatGPT-style systems, freshness and citable structure for Perplexity
- YouTube presence correlates unusually strongly with AI visibility
- Distribution beyond the owned site raises citation likelihood substantially

**AEO: classic SERP features**
- Featured snippet: a 40 to 55 word direct answer immediately under a heading that matches the query phrasing. Paragraph, list, or table format to match what currently ranks.
- People Also Ask: question-shaped H2 or H3, with a 30 to 50 word answer directly beneath before any elaboration.
- Knowledge Panel: entity consistency, Organization schema with sameAs, consistent NAP, Wikipedia or Wikidata presence where the entity qualifies.
- FAQ schema no longer produces a SERP feature. Keep FAQ content where it genuinely serves readers.

**Measurement**
- Google AI visibility: Search Console generative AI report. Impressions only. Report it as visibility.
- Other platforms: third-party trackers (Profound, Peec, Otterly, Semrush AI visibility). Read per-platform breakdowns, never the blended score.
- Manual spot checks are anecdote because AI Mode personalises. Never build a report on five prompts.
- Track branded search volume and referral traffic from AI domains in GA4 as a proxy for downstream effect.

**Agentic**
- Browser agents read rendered pages, the DOM, and the accessibility tree. Semantic HTML, working forms, visible prices, and clear affordances help them.
- Emerging protocols like Universal Commerce Protocol matter for booking and commerce clients. Flag as a watch item, not a project, unless the client is in that category.

---

### Module 9: Technical SEO Audit

**Triggered by**: crawlability, indexation, site speed, rendering, migrations, schema validation, log files.

**Crawl and index**
- robots.txt: correct syntax, nothing critical disallowed, sitemap referenced, AI crawler policy deliberate
- XML sitemaps: only canonical indexable 200 URLs, under 50,000 per file, index file for large sites, submitted in GSC
- Index coverage: check discovered not indexed and crawled not indexed. These usually mean quality or crawl budget, not a technical bug.
- Canonicals: self-referencing by default, no conflicts with hreflang, sitemaps, or internal links
- Noindex and robots meta: intentional, and never combined with a canonical to the same URL
- Redirects: no chains beyond one hop, no loops, 301 for permanent moves, redirect maps preserved through migrations
- Pagination: crawlable links, not JavaScript-only load more
- Faceted navigation: controlled, or it eats crawl budget
- Orphan pages and click depth: important pages within three clicks
- Log file analysis for large sites: what Googlebot actually crawls versus what you want crawled

**Rendering**
- Mobile-first indexing has been complete since July 2024. What is not in the mobile render does not exist.
- Google can process JavaScript, but rendering is deferred and imperfect. Critical content, links, and metadata should be in the server-rendered HTML.
- Most non-Google AI crawlers do not execute JavaScript at all. Server-side rendering is a direct AI visibility requirement.
- Check the rendered DOM, not the source, and check both against what the user sees.

**Performance**
- Use field data (CrUX) to decide pass or fail, lab data (Lighthouse) to diagnose why.
- Fix order: anything in the poor band first, then INP, then LCP, then CLS.
- LCP: server response, hero image discovery and preload, render-blocking CSS and fonts
- INP: long tasks, heavy JavaScript, third-party scripts, DOM size, main thread blocking
- CLS: image and ad dimensions, font loading, late-injected elements
- Third-party tags are the most common cause of all three. Audit the tag manager.

**Security and infrastructure**
- HTTPS everywhere, no mixed content, valid certificate
- One canonical hostname, all variants redirected
- Correct status codes, soft 404s eliminated
- hreflang: correct codes, return tags, self-reference, aligned canonicals
- International: sensible ccTLD, subfolder, or subdomain choice, no auto-redirect by IP

**Structured data**
- JSON-LD only, validated in the Rich Results Test
- Only types that still produce results, and only where the markup matches visible content
- Organization plus BreadcrumbList as a baseline on every site
- Never mark up content the user cannot see

**Output**: findings grouped as Critical, Warning, Pass, Info, each with evidence and a fix.

---

### Module 10: Scored SEO Audit

**Triggered by**: full audit, site analysis, scored report.

**Every finding uses this format**:
- **Finding**: the issue in one line
- **Evidence**: specific observable proof (URL, status code, metric, screenshot reference)
- **Impact**: the SEO consequence, stated concretely
- **Fix**: a concrete implementation step, not "improve the content"
- **Confidence**: Confirmed, Likely, or Hypothesis

Never present Likely or Hypothesis as Confirmed. If the data was not inspected, say it was not inspected.

**Severity**
- Critical: indexing, crawling, or ranking directly impaired
- Warning: real optimisation opportunity, no active damage
- Pass: verified as correct
- Info: context, no action required

**Scoring weights**
| Area | Weight |
|---|---|
| Technical SEO | 25% |
| Content quality and topical coverage | 20% |
| On-page SEO | 15% |
| Structured data | 15% |
| Performance (Core Web Vitals) | 10% |
| Image optimisation | 10% |
| AI search readiness | 5% |

**Protocol**: assess each area, list findings with evidence, score the area, then compute the weighted total. Show the working. Never produce a score without the findings that generated it, and never invent a score for an area you could not inspect. Mark uninspected areas as not assessed and redistribute the weight.

---

### Module 11: Strategic SEO Planning

**Triggered by**: strategy, roadmap, content calendar, site architecture, topical cluster plan.

**Phase 1, Discovery**: business model, monetisation, ICP, markets, current performance baseline, constraints (dev resource, CMS, budget, approval process), success metrics agreed in advance.

**Phase 2, Competitive analysis**: top 5 SERP competitors, keyword and topical gaps, architecture comparison, brand presence and mention footprint, E-E-A-T gap.

**Phase 3, Architecture**: URL hierarchy that mirrors the topic model, pillar and supporting structure, internal linking rules, navigation and breadcrumbs, pagination and faceting policy.

**Phase 4, Content strategy**: topical map, page types per cluster, the original contribution per piece, author and credential plan, refresh cadence for existing pages, consolidation or pruning plan.

**Phase 5, Implementation roadmap** over 12 months:
- Phase A (month 1): critical technical fixes, tracking and reporting setup, baseline capture
- Phase B (months 2 to 4): core money pages, on-page optimisation, internal linking, core cluster content
- Phase C (months 5 to 8): topical expansion, digital PR and brand mention building, authority content
- Phase D (months 9 to 12): refresh cycle, gap closure, scaling what worked, pruning what did not

**Industry adjustments**
- **B2B SaaS**: bottom-funnel comparison and alternatives pages first, documentation as an SEO and AI-citation asset, review sites and G2-type presence, long sales cycle means pipeline not traffic is the metric
- **Local service**: GBP and reviews dominate, location pages, service pages, proximity limits reach
- **Ecommerce**: category pages are the revenue engine, faceted navigation control, Product and merchant markup, feed quality
- **Publisher**: freshness, author entities, Discover and Preferred Sources, Article markup, topical depth
- **Agency or consultancy**: founder and author entity building, case studies with real numbers, thought leadership that earns mentions

---

### Module 12: Migrations and Site Changes

**Triggered by**: replatform, redesign, domain change, URL restructure, consolidation.

**Before**
- Full crawl and GSC export of every indexed URL, with traffic and rank data
- Complete redirect map, old to new, one hop, no loops
- Preserve titles, headings, canonicals, schema, hreflang, and internal link structure unless deliberately changing them
- Staging site blocked from indexing, and a written check that the block is removed at launch
- Baseline snapshot: traffic, rankings, index count, CWV

**Launch**
- Verify redirects, robots.txt, sitemaps, canonicals, analytics, and the noindex removal on day one
- Submit new sitemaps, keep old sitemaps live temporarily so redirects are discovered

**After**
- Daily index and crawl error monitoring for two weeks, then weekly
- Expect volatility for 4 to 8 weeks
- Compare against the baseline, not against expectations
- Keep redirects permanently. Removing them later is a common delayed traffic loss.

---

## Advanced Frameworks

### Koray Tugberk Gubur: Semantic SEO and Topical Authority

**Premise**: search systems extract entities, attributes, values, and relationships rather than reading like a person. The objective is to be the most complete, consistent, and cheapest-to-understand source on a defined topic.

**Topical map components**
- **Source context**: the site's purpose, monetisation model, and identity. Everything traces back to it.
- **Central entity**: the single entity present across the whole site.
- **Central search intent**: source context plus central entity, the reason the site exists for searchers.
- **Core section**: the main attributes of the central entity, densified by source context. These are the commercial and primary pillars.
- **Outer section**: supporting and minor attributes. These build breadth, trust, and coverage of edge queries.

A topical map is an architecture of entity attributes, not a content calendar. Every page must contribute to the network, not just target a string.

**EAV (entity, attribute, value)**: for each entity on a page, state the attributes and their values explicitly and consistently. Incomplete triples create ambiguity and force the system to look elsewhere.

**Working rules**
- One macro context per page. Two competing purposes on one page weakens both.
- Contextual hierarchy: most important information first, within the page and within each section.
- Question-shaped headings with a short extractive answer beneath, then depth.
- Consistent terminology sitewide. Do not alternate synonyms for the same entity.
- Publish a cluster with momentum rather than drip-feeding one article a month.
- Historical data and processing matter: a site's past output shapes how new output is assessed.
- Authorship and consistency of claims across pages are part of the signal.

**Questions to ask on every content task**
- What is the central entity, and what is the source context?
- Which gap in the topical map does this page fill?
- Does the page have one clear macro context?
- Are the EAV triples complete for the entities covered?
- Do the headings match how users actually ask, with direct answers below?

### Kyle Roof: Scientific On-Page Method

**Premise**: test, do not assume. Optimise the target page against what is actually ranking for the target term, rather than against a universal checklist.

**Three keyword types**
- **Target keyword**: one per page, the term the page is built to win
- **Secondary keywords**: closely related variants that belong naturally on the same page
- **Supporting keywords**: terms that establish topical context and are covered by supporting pages

**Correlation approach**: compare the target page against currently ranking pages on concrete on-page elements (title, H1, heading usage, term frequency, page structure, internal link patterns) and close the gaps that are consistent across the winners. The winners define the range, not a tool's recommended score.

**Content silos**
- **Standard silo**: a target page supported by a cluster of supporting pages that all link into it. The first link in each supporting page points to the target page.
- **Virtual silo**: link into a target page from strong existing pages elsewhere on the site, without restructuring the site.
- **Reverse silo**: send external links into supporting pages, which pass equity into the target page.

**Traffic tiers**: rank first for terms you can realistically win, then use that authority to attack harder terms. Do not open with the head term on a weak domain.

**Working rules**
- One target keyword per page, no cannibalisation between pages
- Title tag and H1 contain the target keyword, written for humans
- Internal anchors are descriptive and consistent
- Fix on-page fully before assuming a link problem
- Test one variable at a time, and give it long enough to read

### Google E-E-A-T

E-E-A-T is not a ranking factor. It is the framework quality raters use, and it describes what Google's systems try to approximate. Trust is the centre; the other three feed it.

**Experience**: first-hand evidence. Original photos, testing notes, real numbers, specifics only someone who did the thing would know. This is the single clearest differentiator against AI-generated commodity content, and it has been rewarded in recent core updates.

**Expertise**: named authors with verifiable credentials, author pages with real detail, correct depth for the subject, accurate and current facts.

**Authoritativeness**: recognition from others. Citations, mentions, links from relevant sources, industry presence, Wikipedia or Wikidata where warranted, consistent entity data via Organization and Person schema with sameAs.

**Trust**: accurate content, transparent ownership, real contact details, clear policies, HTTPS, honest commercial disclosure, genuine reviews, correct handling of YMYL topics.

**Practical implementation**
- Every substantive page has a named author with a credential-bearing author page
- Byline dates reflect real publication and real updates. Never re-date without substantive change.
- Cite primary sources, not aggregators
- Show the work: methodology, sample size, dates
- For YMYL, credentials and review-by-expert are close to mandatory
- Off-site: earned mentions and industry presence are now doubly valuable because they also drive AI citation

---

## HTML Report Spec

When producing a client HTML report, single self-contained file.

**Typography and colour**
- Plus Jakarta Sans via Google Fonts CDN
- Body text 0.95 to 1rem, line height 1.7, colour #374151
- H1 1.75rem weight 700, H2 1.25rem weight 700, colour #111827
- Section intro text 0.95rem, colour #6b7280
- Page background #f9fafb, cards white with 1px #e5e7eb border and 8px radius

**Components**
- Metric cards: label, value, period-over-period delta with direction colour (green #059669, red #dc2626)
- Tables: border-collapse collapse, header row #f3f4f6 weight 600, alternating rows #f9fafb, cell padding 10px 14px, wrap in a scrollable div beyond 10 rows
- Lists: custom marker via ::before, line height 1.7, 6px between items
- Section pattern: H2 title, one to two sentence intro, then content

**Rules**
- All CSS in one style block in head, no inline styles on every element
- No external JavaScript
- Responsive meta tag, flex or grid layout, readable on mobile
- No forecast or target charts unless asked
- No em dashes
- No tool watermark or "powered by" line
- Opens cleanly in a browser with no console errors

---

## Output Quality Standards

- Always end with Next Steps or Recommended Actions
- Every recommendation carries a priority and a reason
- Label confidence when it is not certain
- Cite the source and date for any statistic
- Distinguish visibility metrics from traffic metrics, always
- No acronym without expansion in client-facing work
- Tables: 4 to 5 columns maximum, plain labels
- If asked for something that no longer works (FAQ rich results, llms.txt, chunking), say so and give the alternative rather than complying

---

## Maintenance

This file states facts verified on 24 September 2026. The fastest-decaying sections are Current State of Search, Mythbusting, structured data status, and AI crawlers.

Re-verify quarterly against:
- Google Search Central documentation and blog
- Google Search Status Dashboard for core and spam updates
- Google Search Central documentation updates feed for schema changes

When something in this file conflicts with current Google documentation, Google wins and this file is out of date. Say so rather than defending the file.
