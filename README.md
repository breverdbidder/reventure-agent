# 🏠 Reventure Clone Agent

An agentic AI system that reverse engineers housing market data platforms (like Reventure.app) and creates functionally equivalent open-source alternatives using **public data sources**.

## 🎯 What This Does

1. **Discovers** - Analyzes target site's tech stack, APIs, and data sources
2. **Scrapes** - Captures rendered content using Playwright headless browser
3. **Maps** - Identifies public data alternatives (Zillow, Census, FHFA)
4. **Replicates** - Generates complete Next.js + Mapbox + Supabase codebase
5. **Deploys** - Ships to Cloudflare Pages with automated data pipelines

## 🚀 Quick Start

```bash
# Clone this repo
git clone https://github.com/breverdbidder/reventure-clone
cd reventure-clone

# Install Python dependencies
pip install httpx pandas playwright beautifulsoup4 supabase

# Run the full pipeline
python src/agents/reventure_clone_agent.py --full

# Or run individual scrapers
python src/scrapers/zillow_scraper.py --all
python src/scrapers/census_scraper.py --geo zip
```

## 📊 Data Sources (All FREE)

| Source | Data | Update |
|--------|------|--------|
| [Zillow Research](https://www.zillow.com/research/data/) | Home values, rent, inventory | Monthly |
| [US Census API](https://api.census.gov/) | Demographics, income, housing | Annual |
| [FHFA HPI](https://www.fhfa.gov/DataTools/Downloads) | Price indices | Quarterly |
| [FRED](https://fred.stlouisfed.org/) | Mortgage rates, economic | Varies |

## 🗂️ Project Structure

```
reventure-agent/
├── src/
│   ├── agents/
│   │   └── reventure_clone_agent.py   # Main orchestrator
│   └── scrapers/
│       ├── zillow_scraper.py          # Zillow Research data
│       └── census_scraper.py          # Census API integration
├── .github/workflows/
│   └── pipeline.yml                   # Automated data pipeline
├── PRD_REVENTURE_CLONE.md             # Product requirements document
└── SKILL.md                           # Agent skill documentation
```

## 🔑 Required API Keys

| Key | Get It From | Required For |
|-----|-------------|--------------|
| `CENSUS_API_KEY` | [census.gov](https://api.census.gov/data/key_signup.html) | Census data |
| `MAPBOX_TOKEN` | [mapbox.com](https://account.mapbox.com/) | Map rendering |
| `SUPABASE_URL/KEY` | [supabase.com](https://supabase.com/) | Database |

## 📈 ML Scoring Model

The Price Forecast Score (0-100) replicates Reventure's methodology:

| Component | Weight |
|-----------|--------|
| Inventory Level | 20% |
| Days on Market | 20% |
| Price Cut % | 20% |
| Recent Appreciation | 25% |
| Mortgage Rate Impact | 15% |

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- Mapbox GL JS + Deck.gl
- Tailwind CSS + shadcn/ui
- TanStack Query + Zustand

**Backend:**
- Supabase (PostgreSQL)
- GitHub Actions (data pipeline)
- Cloudflare Pages (hosting)

## 💰 Cost Analysis

| Service | Cost |
|---------|------|
| Supabase Pro | $25/mo |
| Cloudflare Pages | FREE |
| Mapbox (50k loads) | FREE |
| Data APIs | FREE |
| **Total** | **$25/mo** |

## 📖 Documentation

- [PRD_REVENTURE_CLONE.md](PRD_REVENTURE_CLONE.md) - Full product requirements
- [SKILL.md](SKILL.md) - Agent capability documentation

## ⚠️ Disclaimer

This project uses **publicly available data** from Zillow Research, US Census Bureau, and other government sources. It does not scrape, copy, or redistribute any proprietary data from Reventure.app. The goal is to create an **equivalent** product using legitimate data sources.

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

*Part of [BidDeed.AI](https://github.com/breverdbidder) - Agentic AI for Real Estate*
