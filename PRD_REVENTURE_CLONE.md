# PRD: Reventure Clone Agent
## Housing Market Data Platform Reverse Engineering

**Version:** 1.0.0  
**Date:** December 24, 2025  
**Author:** AI Architect (Claude Opus 4.5)  
**Project Owner:** Ariel Shapira, Everest Capital USA

---

## Executive Summary

This PRD outlines the architecture and implementation plan for cloning reventure.app/map - a housing market data visualization platform. The goal is to create a functionally equivalent open-source alternative leveraging publicly available data sources while avoiding any proprietary API dependencies.

---

## 1. Target Analysis: reventure.app

### 1.1 Tech Stack (Reverse Engineered)

| Component | Technology | Evidence |
|-----------|------------|----------|
| Framework | Next.js (App Router) | CSR rendering, `__NEXT_DATA__` script tag, `.next` build artifacts |
| Maps | Mapbox GL JS via react-map-gl | Map controls visible, Mapbox attribution |
| Visualization | Deck.gl (suspected) | Choropleth layers, heat map rendering |
| Styling | Tailwind CSS | Class patterns in rendered DOM |
| State Management | React Context / Zustand | Single-page app behavior |
| Backend | Likely Node.js/Next.js API routes | API patterns suggest serverless |
| Database | Likely PostgreSQL / Supabase | Structured relational data patterns |

### 1.2 Data Sources (Confirmed)

| Source | Data Types | Update Frequency |
|--------|-----------|------------------|
| **Zillow** | Home values, Zestimates, price history | Mid-month |
| **Realtor.com** | Inventory, days on market, price cuts | Early month |
| **US Census Bureau** | Demographics, population, income, housing characteristics | Annual (2024 data by EOY 2025) |
| **BLS** | Employment, wages | Monthly |
| **FHFA** | House Price Index | Quarterly |

### 1.3 Key Metrics Tracked

1. **Home Values** - Median home prices by ZIP/Metro/State
2. **Inventory Levels** - Active listings count
3. **Price Cuts %** - Percentage of listings with price reductions
4. **Days on Market** - Average DOM for listings
5. **Price Forecast Score** - Proprietary ML prediction (1-100)
6. **Population Trends** - Net migration, growth rates
7. **Overvaluation Score** - Price-to-income, price-to-rent ratios
8. **Crash Potential** - Composite risk indicator
9. **Building Permits** - New construction activity
10. **Foreclosure Risk** - Mortgage delinquency rates

### 1.4 Geographic Coverage

- **50 States** - State-level aggregates
- **~500 Metro Areas** - CBSA/MSA regions
- **30,000+ ZIP Codes** - Granular local data

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     REVENTURE CLONE AGENT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │   Scraper   │   │   Data      │   │   ML        │            │
│  │   Agent     │──▶│   Pipeline  │──▶│   Scoring   │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
│         │                │                  │                    │
│         ▼                ▼                  ▼                    │
│  ┌───────────────────────────────────────────────┐              │
│  │              Supabase (PostgreSQL)             │              │
│  │  housing_data | metrics | forecasts | geo     │              │
│  └───────────────────────────────────────────────┘              │
│                          │                                       │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────┐              │
│  │           Next.js Frontend (Cloudflare)        │              │
│  │  Map | Dashboard | Reports | API Routes       │              │
│  └───────────────────────────────────────────────┘              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Pipeline Stages

```
Stage 1: DISCOVERY
    └──▶ Identify data sources, API endpoints, scrape targets

Stage 2: SCRAPING
    └──▶ Zillow Research Data (CSV), Realtor.com API, Census API

Stage 3: TRANSFORMATION
    └──▶ Normalize, clean, standardize geographic identifiers

Stage 4: ENRICHMENT
    └──▶ Join datasets by FIPS/ZIP, calculate derived metrics

Stage 5: ML SCORING
    └──▶ Price forecast model, crash potential, overvaluation

Stage 6: STORAGE
    └──▶ Supabase tables with proper indexing

Stage 7: API LAYER
    └──▶ Next.js API routes with caching (ISR)

Stage 8: VISUALIZATION
    └──▶ Mapbox + Deck.gl choropleth rendering
```

---

## 3. Data Integration Strategy

### 3.1 Zillow Research Data (FREE)

**Source:** https://www.zillow.com/research/data/

**Available Datasets:**
- ZHVI (Zillow Home Value Index) - By ZIP, Metro, State
- ZORI (Zillow Observed Rent Index)
- Inventory and Sales metrics
- New Construction and Listings

**Download Method:**
```python
# Zillow provides direct CSV downloads
ZHVI_URL = "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
```

### 3.2 Realtor.com Data (FREE via RAPID API)

**Endpoints:**
- `/properties/v3/list` - Active listings
- `/properties/v3/detail` - Property details
- `/locations/v2/auto-complete` - Location search

**Alternative:** Apify actors for scraping

### 3.3 US Census Bureau API (FREE)

**Base URL:** `https://api.census.gov/data/`

**Key Datasets:**
- ACS 5-Year Estimates: Demographics, income, housing
- PEP (Population Estimates Program): Migration, growth
- Building Permits Survey

**Example Query:**
```bash
curl "https://api.census.gov/data/2022/acs/acs5?get=B25077_001E,B19013_001E&for=zip%20code%20tabulation%20area:*&key=YOUR_KEY"
# B25077_001E = Median home value
# B19013_001E = Median household income
```

### 3.4 FHFA House Price Index (FREE)

**Source:** https://www.fhfa.gov/DataTools/Downloads

**Data:** Quarterly HPI by MSA, State, ZIP3

---

## 4. Scraper Agent Architecture

### 4.1 Multi-Tier Scraping Strategy

```
TIER 1: FREE (Default)
├── Direct CSV downloads (Zillow Research)
├── Census API
├── FHFA downloads
└── Beautiful Soup for static pages

TIER 2: FREE + Playwright
├── Client-side rendered pages
├── JavaScript-heavy dashboards
└── Mapbox tile layers

TIER 3: PAID Fallback ($16-35/mo)
├── Firecrawl - Anti-bot bypass
├── Browserless - BrowserQL
└── Apify Actors - Real estate scrapers
```

### 4.2 Scraper Modules

| Module | Target | Method |
|--------|--------|--------|
| `zillow_scraper.py` | Zillow Research CSVs | Direct download, pandas |
| `census_scraper.py` | Census API | REST API with key |
| `realtor_scraper.py` | Realtor.com | RapidAPI / Apify |
| `fhfa_scraper.py` | FHFA Excel files | Direct download, openpyxl |
| `reventure_scraper.py` | Reverse engineer reference | Playwright headless |

---

## 5. Database Schema (Supabase)

### 5.1 Core Tables

```sql
-- Geographic reference table
CREATE TABLE geographies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geo_type TEXT NOT NULL, -- 'zip', 'metro', 'state', 'county'
    geo_id TEXT NOT NULL UNIQUE, -- FIPS code or ZIP
    name TEXT NOT NULL,
    state_code TEXT,
    lat DECIMAL(9,6),
    lng DECIMAL(9,6),
    geojson JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Housing metrics (monthly snapshots)
CREATE TABLE housing_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geo_id TEXT REFERENCES geographies(geo_id),
    metric_date DATE NOT NULL,
    
    -- Price metrics
    median_home_value DECIMAL(12,2),
    median_list_price DECIMAL(12,2),
    median_sale_price DECIMAL(12,2),
    yoy_price_change DECIMAL(5,2),
    
    -- Inventory metrics
    active_listings INTEGER,
    new_listings INTEGER,
    pending_sales INTEGER,
    sold_count INTEGER,
    
    -- Market health
    days_on_market INTEGER,
    price_cut_pct DECIMAL(5,2),
    list_to_sale_ratio DECIMAL(5,3),
    
    -- Affordability
    median_income DECIMAL(10,2),
    price_to_income_ratio DECIMAL(5,2),
    median_rent DECIMAL(8,2),
    price_to_rent_ratio DECIMAL(5,2),
    
    -- Source tracking
    data_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(geo_id, metric_date)
);

-- ML Forecast scores
CREATE TABLE forecast_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geo_id TEXT REFERENCES geographies(geo_id),
    score_date DATE NOT NULL,
    
    price_forecast_score INTEGER, -- 1-100
    crash_potential_score INTEGER, -- 1-100
    overvaluation_score INTEGER, -- 1-100
    
    -- Component scores
    inventory_score INTEGER,
    dom_score INTEGER,
    price_cut_score INTEGER,
    appreciation_score INTEGER,
    
    -- Predictions
    predicted_1yr_change DECIMAL(5,2),
    predicted_3yr_change DECIMAL(5,2),
    
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(geo_id, score_date)
);

-- Population/Demographics
CREATE TABLE demographics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    geo_id TEXT REFERENCES geographies(geo_id),
    year INTEGER NOT NULL,
    
    population INTEGER,
    population_change INTEGER,
    net_migration INTEGER,
    median_age DECIMAL(4,1),
    
    -- Housing stock
    total_housing_units INTEGER,
    occupied_units INTEGER,
    vacancy_rate DECIMAL(5,2),
    owner_occupied_pct DECIMAL(5,2),
    
    -- Economic
    unemployment_rate DECIMAL(5,2),
    labor_force INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(geo_id, year)
);
```

### 5.2 Indexes

```sql
CREATE INDEX idx_housing_geo_date ON housing_metrics(geo_id, metric_date DESC);
CREATE INDEX idx_forecast_geo_date ON forecast_scores(geo_id, score_date DESC);
CREATE INDEX idx_geo_type ON geographies(geo_type);
CREATE INDEX idx_geo_state ON geographies(state_code);
```

---

## 6. ML Scoring Model

### 6.1 Price Forecast Score (1-100)

**Components (Reventure's methodology):**

| Component | Weight | Interpretation |
|-----------|--------|----------------|
| Inventory Level | 20% | Higher inventory = lower score |
| Days on Market | 20% | Higher DOM = lower score |
| Price Cut % | 20% | More cuts = lower score |
| Recent Appreciation | 25% | Lower growth = lower score |
| Mortgage Rates Impact | 15% | Higher rates = lower score |

**Score Interpretation:**
- **70-100:** Strong appreciation expected
- **50-69:** Stable/modest growth
- **30-49:** Flat to slight decline
- **0-29:** Significant decline risk

### 6.2 Implementation

```python
def calculate_price_forecast_score(metrics: dict) -> int:
    """
    Calculate Reventure-style price forecast score.
    """
    # Normalize each component to 0-100
    inventory_score = normalize_inventory(metrics['active_listings'], metrics['historical_avg'])
    dom_score = normalize_dom(metrics['days_on_market'])
    price_cut_score = normalize_price_cuts(metrics['price_cut_pct'])
    appreciation_score = normalize_appreciation(metrics['yoy_price_change'])
    rate_impact_score = normalize_rate_impact(metrics['mortgage_rate'])
    
    # Weighted average
    score = (
        inventory_score * 0.20 +
        dom_score * 0.20 +
        price_cut_score * 0.20 +
        appreciation_score * 0.25 +
        rate_impact_score * 0.15
    )
    
    return int(round(score))
```

---

## 7. Frontend Architecture

### 7.1 Tech Stack

```
Next.js 14 (App Router)
├── react-map-gl (Mapbox wrapper)
├── @deck.gl/react (Data viz layers)
├── @tanstack/react-query (Data fetching)
├── zustand (State management)
├── tailwindcss (Styling)
└── shadcn/ui (Component library)
```

### 7.2 Key Components

```
src/
├── app/
│   ├── page.tsx           # Landing page
│   ├── map/
│   │   └── page.tsx       # Main map dashboard
│   ├── reports/
│   │   └── [geo]/page.tsx # Detailed reports
│   └── api/
│       ├── metrics/route.ts
│       ├── forecast/route.ts
│       └── search/route.ts
├── components/
│   ├── map/
│   │   ├── MapContainer.tsx
│   │   ├── ChoroplethLayer.tsx
│   │   ├── MetricSelector.tsx
│   │   └── GeoSearch.tsx
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── TrendChart.tsx
│   │   └── ScoreGauge.tsx
│   └── ui/
│       └── [shadcn components]
├── lib/
│   ├── mapbox/
│   │   └── config.ts
│   └── api/
│       └── client.ts
└── stores/
    └── mapStore.ts
```

### 7.3 Map Implementation

```tsx
// components/map/MapContainer.tsx
'use client';

import Map, { NavigationControl, GeolocateControl } from 'react-map-gl';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';

export function MapContainer({ data, selectedMetric }) {
  const layer = new GeoJsonLayer({
    id: 'choropleth',
    data,
    filled: true,
    getFillColor: d => getColorForValue(d.properties[selectedMetric]),
    getLineColor: [255, 255, 255, 100],
    lineWidthMinPixels: 1,
    pickable: true,
    onHover: handleHover,
    onClick: handleClick
  });

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller={true}
      layers={[layer]}
    >
      <Map
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        mapStyle="mapbox://styles/mapbox/light-v11"
      >
        <NavigationControl position="top-right" />
        <GeolocateControl position="top-right" />
      </Map>
    </DeckGL>
  );
}
```

---

## 8. API Design

### 8.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics` | GET | Get housing metrics by geo |
| `/api/forecast` | GET | Get forecast scores |
| `/api/search` | GET | Search locations |
| `/api/compare` | GET | Compare multiple geos |
| `/api/historical` | GET | Historical time series |

### 8.2 Example Response

```json
GET /api/metrics?geo_id=32937&date=2025-12

{
  "geo_id": "32937",
  "name": "Satellite Beach, FL",
  "geo_type": "zip",
  "metric_date": "2025-12-01",
  "metrics": {
    "median_home_value": 425000,
    "yoy_price_change": 2.3,
    "active_listings": 145,
    "days_on_market": 48,
    "price_cut_pct": 22.5,
    "median_income": 78500,
    "price_to_income_ratio": 5.4
  },
  "forecast": {
    "price_forecast_score": 52,
    "crash_potential_score": 35,
    "predicted_1yr_change": 1.2
  }
}
```

---

## 9. Deployment Architecture

### 9.1 Infrastructure

```
GitHub (breverdbidder/reventure-clone)
    │
    ├──▶ GitHub Actions
    │       ├── scraper_workflow.yml (Daily 6 AM)
    │       ├── ml_scoring.yml (Weekly)
    │       └── deploy.yml (On push)
    │
    ├──▶ Supabase
    │       ├── PostgreSQL (data storage)
    │       ├── PostgREST (auto API)
    │       └── Storage (GeoJSON files)
    │
    └──▶ Cloudflare Pages
            ├── Next.js frontend
            ├── Edge functions (API routes)
            └── CDN (static assets)
```

### 9.2 Environment Variables

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Mapbox
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ...

# Data APIs
CENSUS_API_KEY=xxx
RAPIDAPI_KEY=xxx

# Scraping (optional)
FIRECRAWL_API_KEY=xxx
BROWSERLESS_API_KEY=xxx
```

---

## 10. Development Roadmap

### Phase 1: Data Foundation (Week 1)
- [ ] Set up Supabase schema
- [ ] Implement Zillow CSV scraper
- [ ] Implement Census API integration
- [ ] Load geographic boundaries (GeoJSON)

### Phase 2: Core Features (Week 2)
- [ ] Build Next.js frontend scaffold
- [ ] Implement Mapbox + Deck.gl map
- [ ] Create choropleth visualization
- [ ] Add metric selector UI

### Phase 3: ML & Analytics (Week 3)
- [ ] Implement forecast score algorithm
- [ ] Historical trend analysis
- [ ] Compare feature
- [ ] Export/reporting

### Phase 4: Polish & Deploy (Week 4)
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] Documentation
- [ ] Production deployment

---

## 11. Cost Analysis

### Monthly Operating Costs

| Service | Plan | Cost |
|---------|------|------|
| Supabase | Pro | $25 |
| Cloudflare Pages | Free | $0 |
| Mapbox | Free tier (50k loads) | $0 |
| Census API | Free | $0 |
| Zillow Research | Free | $0 |
| **Total** | | **$25/mo** |

### Optional Enhancements

| Service | Use Case | Cost |
|---------|----------|------|
| Firecrawl | Anti-bot scraping | $16/mo |
| Browserless | Playwright hosting | $35/mo |
| Mapbox | Beyond free tier | $0.60/1k |

---

## 12. API Mega Library Integration

### Recommended Tools from API_MEGA_LIBRARY.md

| Tool | Purpose | Priority |
|------|---------|----------|
| **AI Web Scraper - Crawl4AI** | LLM-optimized scraping | HIGH |
| **Global Real Estate Aggregator** | Multi-source property data | HIGH |
| **Playwright MCP Server** | Browser automation | HIGH |
| **Census API** | Demographics | HIGH |
| **Zillow Research Data** | Home values | HIGH |
| **Firecrawl** | Anti-bot bypass | MEDIUM |
| **Browserless** | Hosted Playwright | MEDIUM |

### MCP Servers for Enhanced Automation

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/mcp-server-playwright"]
    },
    "supabase": {
      "command": "npx", 
      "args": ["@anthropic/mcp-server-supabase"]
    }
  }
}
```

---

## 13. Success Metrics

| KPI | Target |
|-----|--------|
| Data freshness | < 30 days lag |
| Geographic coverage | 30,000+ ZIPs |
| API response time | < 200ms |
| Map load time | < 3s |
| Uptime | 99.9% |
| Cost | < $50/mo |

---

## 14. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Zillow blocks scraping | Use official Research Data CSVs (allowed) |
| Rate limiting | Implement exponential backoff, caching |
| Data accuracy | Cross-validate with multiple sources |
| Mapbox costs | Start with free tier, monitor usage |
| Scope creep | Prioritize MVP features, iterate |

---

## Appendix A: GeoJSON Sources

- **US States:** Natural Earth / Census TIGER
- **Counties:** Census TIGER/Line
- **ZIP Code Tabulation Areas:** Census ZCTA
- **Metro Areas:** Census CBSA boundaries

## Appendix B: Color Scale Reference

Reventure uses a **red-to-green** diverging scale:
- **Red (high risk):** `#FF4444`
- **Orange:** `#FF8C00`  
- **Yellow (neutral):** `#FFD700`
- **Light Green:** `#90EE90`
- **Green (low risk):** `#22C55E`

---

*Document generated by AI Architect for BidDeed.AI / Everest Capital USA*
