"""Quick benchmark test for inspect_page against the reference URL."""
import json
import sys
sys.path.insert(0, ".")

from mcp_tools.inspect_page import inspect_page

URL = "https://test.grovuu.com/treatments/"

print(f"Testing inspect_page against: {URL}")
print("=" * 60)

try:
    result = inspect_page(URL)
    
    # Print key evidence for benchmark comparison
    meta = result["metadata"]
    idx = result["indexability"]
    headings = result["headings"]
    images = result["images"]
    sd = result["structuredData"]
    
    print(f"HTTP Status:        {result['http']['status']}")
    print(f"Final URL:          {result['finalUrl']}")
    print(f"Fetch time:         {result['fetchMs']}ms")
    print()
    print(f"Title:              {meta['title']}")
    print(f"Title chars:        {meta['titleCharacters']}")
    print(f"Meta description:   {meta['metaDescription'] or '(missing)'}")
    print(f"Desc chars:         {meta['metaDescriptionCharacters']}")
    print()
    print(f"Canonical:          {idx['canonical']}")
    print(f"Self-referencing:   {idx['selfReferencingCanonical']}")
    print(f"Noindex:            {idx['noindex']}")
    print(f"Robots meta:        {idx['robotsMeta']}")
    print()
    print(f"H1 tags:            {headings['h1']}")
    print(f"Total headings:     {len(headings['all'])}")
    print()
    print(f"Word count:         {result['content']['serverHtmlWordCount']}")
    print(f"HTML bytes:         {result['content']['htmlBytes']}")
    print()
    print(f"Internal links:     {result['links']['internalCount']}")
    print(f"External links:     {result['links']['externalCount']}")
    print()
    print(f"Images:             {images['count']}")
    print(f"  Missing alt:      {images['missingAltAttribute']}")
    print(f"  Missing dims:     {images['missingDimensions']}")
    print(f"  Lazy loaded:      {images['lazyLoaded']}")
    print()
    print(f"JSON-LD types:      {sd['jsonLdTypes'] or '(none)'}")
    print(f"Invalid JSON-LD:    {sd['invalidJsonLd'] or '(none)'}")
    print()
    print(f"Language:           {meta['lang']}")
    print(f"Viewport:           {meta['viewport']}")
    print()
    print(f"Open Graph title:   {meta['openGraph']['title']}")
    print(f"Open Graph desc:    {meta['openGraph']['description']}")
    print(f"Open Graph image:   {meta['openGraph']['image']}")
    
    print()
    print("=" * 60)
    print("BENCHMARK COMPARISON (vs Claude audit):")
    print(f"  Title 'Treatments – Liver':  {'✅ MATCH' if 'Treatments' in meta['title'] and 'Liver' in meta['title'] else '❌ DIFF: ' + meta['title']}")
    print(f"  Meta desc missing:           {'✅ MATCH' if meta['metaDescriptionCharacters'] == 0 else '❌ DIFF: has description'}")
    print(f"  Self-ref canonical:          {'✅ MATCH' if idx['selfReferencingCanonical'] else '❌ DIFF'}")
    print(f"  Has H1:                      {'✅ MATCH' if len(headings['h1']) >= 1 else '❌ DIFF'}")
    print(f"  JSON-LD absent:              {'✅ MATCH' if not sd['jsonLdTypes'] else '❌ DIFF: found ' + str(sd['jsonLdTypes'])}")
    print(f"  Images missing dims:         {'✅ MATCH' if images['missingDimensions'] > 0 else '❌ DIFF'}")
    print()
    print("Evidence status:", result["evidenceStatus"])
    print("Limitations:", result["limitations"])
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
