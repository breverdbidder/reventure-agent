# Website Cloning Agent - SKILL.md

## Overview

The **Website Cloning Agent** is an advanced agentic AI system that reverse engineers web applications and creates functionally equivalent open-source alternatives using public data sources. This skill is specifically designed for housing market data platforms like Reventure.app but can be adapted for other data-driven web applications.

## Capabilities

### 1. Tech Stack Discovery
- Detects frontend framework (Next.js, React, Vue, Angular)
- Identifies mapping libraries (Mapbox, Google Maps, Leaflet)
- Recognizes CSS frameworks (Tailwind, Bootstrap, Material UI)
- Extracts API endpoint patterns
- Captures analytics/tracking tools

### 2. Content Scraping
- Playwright-based headless browser scraping for CSR sites
- Network request interception to discover API calls
- __NEXT_DATA__ extraction for Next.js applications
- Full-page screenshot capture
- Asset collection (JS, CSS, images)

### 3. Data Source Mapping
- Identifies public data alternatives to proprietary APIs
- Maps Zillow Research Data endpoints
- Documents US Census Bureau API variables
- Catalogs FHFA, FRED, and other government sources

### 4. Code Generation
- Generates complete Next.js project structure
- Creates Mapbox + Deck.gl map components
- Builds Supabase database schema
- Produces GitHub Actions pipelines

## Usage

### CLI Commands

```bash
# Full pipeline
python src/agents/reventure_clone_agent.py --full

# Discovery only
python src/agents/reventure_clone_agent.py --discover

# Generate code
python src/agents/reventure_clone_agent.py --generate --output my-clone

# Run scrapers
python src/scrapers/zillow_scraper.py --all
python src/scrapers/census_scraper.py --geo zip --year 2022
```

### Python API

```python
from src.agents.reventure_clone_agent import ReventureCloneAgent

async with ReventureCloneAgent() as agent:
    # Discover tech stack
    tech = await agent.discover_tech_stack("https://example.com")
    
    # Scrape with Playwright
    data = await agent.scrape_with_playwright("https://example.com/app")
    
    # Map data sources
    sources = agent.map_data_sources()
    
    # Generate project
    agent.generate_project_structure("output-dir")
```

## Data Sources

| Source | Cost | Update Frequency | Key Data |
|--------|------|------------------|----------|
| Zillow Research | FREE | Monthly | Home values, rent, inventory |
| US Census API | FREE | Annual | Demographics, income, housing |
| FHFA HPI | FREE | Quarterly | Price indices |
| FRED | FREE | Varies | Mortgage rates, economic |
| Realtor.com | FREE/API | Monthly | Listings, DOM |

## Architecture

```
reventure-agent/
├── src/
│   ├── agents/
│   │   └── reventure_clone_agent.py  # Main orchestrator
│   ├── scrapers/
│   │   ├── zillow_scraper.py         # Zillow Research data
│   │   ├── census_scraper.py         # Census API
│   │   └── realtor_scraper.py        # Realtor.com (optional)
│   ├── integrations/
│   │   └── supabase_client.py        # Database client
│   ├── components/
│   │   └── MapContainer.tsx          # React map component
│   └── utils/
│       └── scoring.py                # ML scoring functions
├── .github/
│   └── workflows/
│       └── pipeline.yml              # Data pipeline
└── PRD_REVENTURE_CLONE.md            # Product requirements
```

## ML Scoring Model

The Price Forecast Score (0-100) uses these components:

| Component | Weight | Source |
|-----------|--------|--------|
| Inventory Level | 20% | Zillow/Realtor |
| Days on Market | 20% | Zillow/Realtor |
| Price Cut % | 20% | Zillow |
| Recent Appreciation | 25% | Zillow ZHVI |
| Rate Impact | 15% | FRED |

## Deployment

### Requirements
- Node.js 18+
- Python 3.11+
- Playwright (for scraping)
- Supabase account
- Mapbox account
- Cloudflare Pages (hosting)

### Environment Variables

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Mapbox
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ...

# Census
CENSUS_API_KEY=xxx

# GitHub (for workflows)
GITHUB_TOKEN=ghp_xxx

# Cloudflare
CLOUDFLARE_API_TOKEN=xxx
CLOUDFLARE_ACCOUNT_ID=xxx
```

## API from API_MEGA_LIBRARY Integration

Recommended tools from the API Mega Library:

| Tool | Use Case | Priority |
|------|----------|----------|
| Crawl4AI (Apify) | LLM-optimized scraping | HIGH |
| Playwright MCP Server | Browser automation | HIGH |
| Global Real Estate Aggregator | Multi-source data | MEDIUM |
| Firecrawl | Anti-bot bypass | MEDIUM |
| Browserless | Hosted Playwright | LOW |

## Best Practices

1. **Rate Limiting**: Respect API limits, use exponential backoff
2. **Caching**: Cache responses to reduce API calls
3. **Incremental Updates**: Only fetch changed data
4. **Attribution**: Always credit data sources
5. **Privacy**: Don't scrape personal information

## Limitations

- Requires public data alternatives (can't replicate proprietary algorithms exactly)
- Playwright scraping may be blocked by some sites
- Census data has 1-2 year lag
- Mapbox free tier limited to 50k loads/month

## Related Skills

- `/mnt/skills/examples/website-to-vite-scraper/SKILL.md` - Basic website cloning
- `/mnt/skills/public/frontend-design/SKILL.md` - UI design
- `/mnt/skills/examples/mcp-builder/SKILL.md` - MCP server creation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-24 | Initial release |

---

*Part of BidDeed.AI / Everest Capital USA*
