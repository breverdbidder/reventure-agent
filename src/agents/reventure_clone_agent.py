#!/usr/bin/env python3
"""
Reventure Clone Agent - Website Cloning & Data Intelligence System
Part of BidDeed.AI / Everest Capital USA

This agent reverse engineers reventure.app and creates a functionally
equivalent housing market data platform using public data sources.
"""

import asyncio
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

# Configuration
CONFIG = {
    "target_url": "https://www.reventure.app",
    "map_url": "https://www.reventure.app/map",
    "output_dir": "reventure-clone",
    "github_repo": "breverdbidder/reventure-clone",
    "supabase_url": os.getenv("SUPABASE_URL", ""),
    "supabase_key": os.getenv("SUPABASE_KEY", ""),
}


class ReventureCloneAgent:
    """
    Agentic Website Cloning System for housing market data platforms.
    
    Pipeline:
    1. DISCOVER - Analyze target site structure, APIs, tech stack
    2. SCRAPE - Capture rendered content, assets, API calls
    3. ANALYZE - Reverse engineer data models and business logic
    4. REPLICATE - Build functionally equivalent system
    5. DEPLOY - Ship to Cloudflare Pages
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        self.discovered_apis: List[Dict] = []
        self.discovered_assets: List[str] = []
        self.tech_stack: Dict[str, str] = {}
        self.data_sources: List[Dict] = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, *args):
        await self.client.aclose()
    
    # ==================== STAGE 1: DISCOVERY ====================
    
    async def discover_tech_stack(self, url: str) -> Dict[str, Any]:
        """
        Analyze target site to identify technologies used.
        """
        print(f"🔍 Discovering tech stack for {url}...")
        
        try:
            response = await self.client.get(url)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            tech_stack = {
                "framework": self._detect_framework(html, soup),
                "mapping": self._detect_mapping_library(html),
                "styling": self._detect_styling(html),
                "analytics": self._detect_analytics(html),
                "api_patterns": self._extract_api_patterns(html),
            }
            
            self.tech_stack = tech_stack
            return tech_stack
            
        except Exception as e:
            print(f"❌ Discovery error: {e}")
            return {}
    
    def _detect_framework(self, html: str, soup: BeautifulSoup) -> str:
        """Detect frontend framework."""
        indicators = {
            "Next.js": ["__NEXT_DATA__", "_next/", "next/head"],
            "React": ["react-root", "__react", "data-reactroot"],
            "Vue.js": ["__vue__", "v-cloak", "vue-app"],
            "Angular": ["ng-version", "ng-app", "_ngcontent"],
        }
        
        for framework, patterns in indicators.items():
            for pattern in patterns:
                if pattern in html:
                    return framework
        
        return "Unknown"
    
    def _detect_mapping_library(self, html: str) -> str:
        """Detect mapping library used."""
        if "mapbox" in html.lower() or "mapboxgl" in html.lower():
            return "Mapbox GL JS"
        if "google.maps" in html or "maps.googleapis" in html:
            return "Google Maps"
        if "leaflet" in html.lower():
            return "Leaflet"
        return "Unknown"
    
    def _detect_styling(self, html: str) -> str:
        """Detect CSS framework."""
        if "tailwind" in html.lower():
            return "Tailwind CSS"
        if "bootstrap" in html.lower():
            return "Bootstrap"
        if "mui" in html.lower() or "material-ui" in html.lower():
            return "Material UI"
        return "Custom CSS"
    
    def _detect_analytics(self, html: str) -> List[str]:
        """Detect analytics/tracking."""
        analytics = []
        if "google-analytics" in html or "gtag" in html:
            analytics.append("Google Analytics")
        if "facebook.com/tr" in html:
            analytics.append("Facebook Pixel")
        if "segment.com" in html or "analytics.js" in html:
            analytics.append("Segment")
        return analytics
    
    def _extract_api_patterns(self, html: str) -> List[str]:
        """Extract potential API endpoint patterns."""
        patterns = []
        
        # Look for API URLs in scripts
        api_pattern = r'["\'](?:https?://)?[^"\']*(?:api|graphql|v\d)[^"\']*["\']'
        matches = re.findall(api_pattern, html, re.IGNORECASE)
        
        for match in matches:
            url = match.strip('"\'')
            if url and 'reventure' in url.lower():
                patterns.append(url)
        
        return list(set(patterns))
    
    # ==================== STAGE 2: SCRAPING ====================
    
    async def scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """
        Use Playwright to capture fully rendered CSR content.
        """
        print(f"🌐 Scraping {url} with Playwright...")
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Capture network requests
                api_calls = []
                js_files = []
                
                async def handle_request(request):
                    req_url = request.url
                    if 'api' in req_url.lower() or '/v1/' in req_url or '/v2/' in req_url:
                        api_calls.append({
                            'url': req_url,
                            'method': request.method,
                            'resource_type': request.resource_type
                        })
                    if '.js' in req_url and not 'chunk' in req_url:
                        js_files.append(req_url)
                
                page.on('request', handle_request)
                
                # Navigate and wait
                await page.goto(url, wait_until='networkidle', timeout=60000)
                await page.wait_for_timeout(3000)  # Extra wait for CSR
                
                # Get content
                html_content = await page.content()
                
                # Extract __NEXT_DATA__ if present
                next_data = None
                next_data_match = re.search(
                    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                    html_content,
                    re.DOTALL
                )
                if next_data_match:
                    try:
                        next_data = json.loads(next_data_match.group(1))
                    except:
                        pass
                
                # Take screenshot
                screenshot_path = f"/tmp/reventure_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                await browser.close()
                
                self.discovered_apis = api_calls
                
                return {
                    'html': html_content,
                    'api_calls': api_calls,
                    'js_files': js_files,
                    'next_data': next_data,
                    'screenshot': screenshot_path
                }
                
        except ImportError:
            print("⚠️ Playwright not installed, falling back to basic scraping")
            return await self._fallback_scrape(url)
        except Exception as e:
            print(f"❌ Playwright error: {e}")
            return await self._fallback_scrape(url)
    
    async def _fallback_scrape(self, url: str) -> Dict[str, Any]:
        """Basic HTTP scraping fallback."""
        response = await self.client.get(url)
        return {
            'html': response.text,
            'api_calls': [],
            'js_files': [],
            'next_data': None,
            'screenshot': None
        }
    
    # ==================== STAGE 3: DATA SOURCE MAPPING ====================
    
    def map_data_sources(self) -> List[Dict]:
        """
        Map the public data sources that can replicate Reventure's data.
        """
        sources = [
            {
                "name": "Zillow Research Data",
                "url": "https://www.zillow.com/research/data/",
                "data_types": ["home_values", "rent_index", "inventory", "listings"],
                "update_frequency": "monthly",
                "access": "free_download",
                "format": "CSV",
                "endpoints": {
                    "zhvi_zip": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
                    "zhvi_metro": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
                    "zhvi_state": "https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
                    "zori": "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_sa_month.csv",
                    "inventory": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
                }
            },
            {
                "name": "US Census Bureau API",
                "url": "https://api.census.gov/data/",
                "data_types": ["demographics", "population", "income", "housing_units"],
                "update_frequency": "annual",
                "access": "api_key_required",
                "format": "JSON",
                "endpoints": {
                    "acs5": "https://api.census.gov/data/{year}/acs/acs5",
                    "pep_population": "https://api.census.gov/data/{year}/pep/population",
                    "building_permits": "https://api.census.gov/data/timeseries/bps"
                },
                "key_variables": {
                    "B25077_001E": "Median home value",
                    "B19013_001E": "Median household income",
                    "B01003_001E": "Total population",
                    "B25002_002E": "Occupied housing units",
                    "B25002_003E": "Vacant housing units"
                }
            },
            {
                "name": "FHFA House Price Index",
                "url": "https://www.fhfa.gov/DataTools/Downloads",
                "data_types": ["house_price_index", "appreciation"],
                "update_frequency": "quarterly",
                "access": "free_download",
                "format": "Excel"
            },
            {
                "name": "Realtor.com Research",
                "url": "https://www.realtor.com/research/data/",
                "data_types": ["active_listings", "days_on_market", "price_cuts"],
                "update_frequency": "monthly",
                "access": "free_download",
                "format": "CSV"
            },
            {
                "name": "FRED Economic Data",
                "url": "https://fred.stlouisfed.org/",
                "data_types": ["mortgage_rates", "unemployment", "inflation"],
                "update_frequency": "varies",
                "access": "api_key_required",
                "format": "JSON/CSV"
            }
        ]
        
        self.data_sources = sources
        return sources
    
    # ==================== STAGE 4: CODE GENERATION ====================
    
    def generate_project_structure(self, output_dir: str) -> None:
        """
        Generate the full project structure for the clone.
        """
        print(f"📁 Generating project structure in {output_dir}...")
        
        dirs = [
            "src/app",
            "src/app/api/metrics",
            "src/app/api/forecast",
            "src/app/api/search",
            "src/app/map",
            "src/app/reports/[geo]",
            "src/components/map",
            "src/components/dashboard",
            "src/components/ui",
            "src/lib/mapbox",
            "src/lib/api",
            "src/lib/data",
            "src/stores",
            "src/types",
            "public/geojson",
            "scripts/scrapers",
            "scripts/pipeline",
            ".github/workflows",
        ]
        
        for d in dirs:
            Path(output_dir, d).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created {len(dirs)} directories")
    
    def generate_package_json(self) -> str:
        """Generate package.json for Next.js project."""
        return json.dumps({
            "name": "reventure-clone",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "scrape": "python scripts/scrapers/run_all.py",
                "pipeline": "python scripts/pipeline/main.py"
            },
            "dependencies": {
                "next": "14.2.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-map-gl": "^7.1.7",
                "@deck.gl/core": "^9.0.0",
                "@deck.gl/layers": "^9.0.0",
                "@deck.gl/react": "^9.0.0",
                "mapbox-gl": "^3.1.0",
                "@supabase/supabase-js": "^2.39.0",
                "@tanstack/react-query": "^5.17.0",
                "zustand": "^4.4.7",
                "d3-scale": "^4.0.2",
                "d3-scale-chromatic": "^3.0.0"
            },
            "devDependencies": {
                "@types/node": "^20.10.0",
                "@types/react": "^18.2.0",
                "typescript": "^5.3.0",
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.32",
                "autoprefixer": "^10.4.16",
                "eslint": "^8.55.0",
                "eslint-config-next": "14.2.0"
            }
        }, indent=2)
    
    def generate_map_component(self) -> str:
        """Generate the main map component."""
        return '''
'use client';

import React, { useState, useCallback } from 'react';
import Map, { NavigationControl, GeolocateControl, Popup } from 'react-map-gl';
import DeckGL from '@deck.gl/react';
import { GeoJsonLayer } from '@deck.gl/layers';
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import 'mapbox-gl/dist/mapbox-gl.css';

import { MetricSelector } from './MetricSelector';
import { GeoSearch } from './GeoSearch';
import { useMapStore } from '@/stores/mapStore';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 4,
  pitch: 0,
  bearing: 0
};

const METRICS = [
  { id: 'median_home_value', label: 'Home Values', format: 'currency' },
  { id: 'yoy_price_change', label: 'YoY Change', format: 'percent' },
  { id: 'price_forecast_score', label: 'Forecast Score', format: 'score' },
  { id: 'days_on_market', label: 'Days on Market', format: 'number' },
  { id: 'price_cut_pct', label: 'Price Cuts %', format: 'percent' },
  { id: 'active_listings', label: 'Inventory', format: 'number' },
];

export function MapContainer() {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [hoverInfo, setHoverInfo] = useState(null);
  const [selectedGeo, setSelectedGeo] = useState(null);
  
  const { selectedMetric, setSelectedMetric, geoData } = useMapStore();
  
  // Color scale based on metric
  const colorScale = scaleSequential(interpolateRdYlGn).domain([0, 100]);
  
  const getColor = useCallback((value: number) => {
    if (value === null || value === undefined) return [200, 200, 200, 180];
    
    // Normalize value to 0-100 based on metric
    let normalized = value;
    if (selectedMetric === 'median_home_value') {
      normalized = Math.min(100, (value / 1000000) * 100);
    } else if (selectedMetric === 'yoy_price_change') {
      normalized = 50 + (value * 5); // -10% to +10% mapped to 0-100
    }
    
    const rgb = colorScale(normalized);
    const match = rgb.match(/\\d+/g);
    return match ? [+match[0], +match[1], +match[2], 200] : [200, 200, 200, 180];
  }, [selectedMetric, colorScale]);
  
  const layers = [
    new GeoJsonLayer({
      id: 'choropleth-layer',
      data: geoData,
      filled: true,
      stroked: true,
      getFillColor: d => getColor(d.properties?.[selectedMetric] || 0),
      getLineColor: [255, 255, 255, 100],
      lineWidthMinPixels: 0.5,
      pickable: true,
      autoHighlight: true,
      highlightColor: [255, 255, 255, 100],
      onHover: info => setHoverInfo(info.object ? info : null),
      onClick: info => setSelectedGeo(info.object?.properties || null),
      updateTriggers: {
        getFillColor: [selectedMetric]
      }
    })
  ];
  
  return (
    <div className="relative w-full h-screen">
      {/* Controls */}
      <div className="absolute top-4 left-4 z-10 space-y-4">
        <GeoSearch />
        <MetricSelector 
          metrics={METRICS}
          selected={selectedMetric}
          onSelect={setSelectedMetric}
        />
      </div>
      
      {/* Map */}
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState }) => setViewState(viewState)}
        controller={true}
        layers={layers}
      >
        <Map
          mapboxAccessToken={MAPBOX_TOKEN}
          mapStyle="mapbox://styles/mapbox/light-v11"
          reuseMaps
        >
          <NavigationControl position="top-right" />
          <GeolocateControl position="top-right" />
        </Map>
      </DeckGL>
      
      {/* Hover tooltip */}
      {hoverInfo && hoverInfo.object && (
        <div 
          className="absolute bg-white rounded-lg shadow-lg p-3 pointer-events-none z-20"
          style={{ left: hoverInfo.x + 10, top: hoverInfo.y + 10 }}
        >
          <div className="font-semibold">{hoverInfo.object.properties.name}</div>
          <div className="text-sm text-gray-600">
            {formatValue(
              hoverInfo.object.properties[selectedMetric],
              METRICS.find(m => m.id === selectedMetric)?.format
            )}
          </div>
        </div>
      )}
      
      {/* Legend */}
      <div className="absolute bottom-8 right-4 bg-white rounded-lg shadow-lg p-4 z-10">
        <div className="text-sm font-medium mb-2">
          {METRICS.find(m => m.id === selectedMetric)?.label}
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs">Low</span>
          <div 
            className="w-32 h-3 rounded"
            style={{
              background: 'linear-gradient(to right, #d73027, #fee08b, #1a9850)'
            }}
          />
          <span className="text-xs">High</span>
        </div>
      </div>
    </div>
  );
}

function formatValue(value: number, format: string) {
  if (value === null || value === undefined) return 'N/A';
  
  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'USD',
        maximumFractionDigits: 0 
      }).format(value);
    case 'percent':
      return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
    case 'score':
      return `${value}/100`;
    default:
      return value.toLocaleString();
  }
}
'''
    
    def generate_github_workflow(self) -> str:
        """Generate GitHub Actions workflow for data pipeline."""
        return '''name: Housing Data Pipeline

on:
  schedule:
    # Run at 6 AM UTC on the 1st and 15th of each month
    - cron: '0 6 1,15 * *'
  workflow_dispatch:
    inputs:
      full_refresh:
        description: 'Full data refresh'
        required: false
        default: 'false'

jobs:
  scrape-data:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install httpx pandas openpyxl supabase python-dotenv
      
      - name: Run Zillow scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scripts/scrapers/zillow_scraper.py
      
      - name: Run Census scraper
        env:
          CENSUS_API_KEY: ${{ secrets.CENSUS_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scripts/scrapers/census_scraper.py
      
      - name: Calculate forecast scores
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python scripts/pipeline/calculate_scores.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: pipeline-logs
          path: logs/

  deploy-frontend:
    needs: scrape-data
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        env:
          NEXT_PUBLIC_MAPBOX_TOKEN: ${{ secrets.MAPBOX_TOKEN }}
          NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: npm run build
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: reventure-clone
          directory: out
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
'''
    
    # ==================== STAGE 5: RUN AGENT ====================
    
    async def run(self) -> Dict[str, Any]:
        """
        Execute the full cloning pipeline.
        """
        print("=" * 60)
        print("🚀 REVENTURE CLONE AGENT - Starting Pipeline")
        print("=" * 60)
        
        results = {
            "status": "started",
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Discovery
        print("\n📍 STAGE 1: DISCOVERY")
        tech_stack = await self.discover_tech_stack(CONFIG["target_url"])
        results["stages"]["discovery"] = {
            "tech_stack": tech_stack,
            "status": "completed"
        }
        print(f"   Framework: {tech_stack.get('framework', 'Unknown')}")
        print(f"   Mapping: {tech_stack.get('mapping', 'Unknown')}")
        
        # Stage 2: Scraping
        print("\n📍 STAGE 2: SCRAPING")
        scrape_results = await self.scrape_with_playwright(CONFIG["map_url"])
        results["stages"]["scraping"] = {
            "api_calls_found": len(scrape_results.get('api_calls', [])),
            "js_files_found": len(scrape_results.get('js_files', [])),
            "has_next_data": scrape_results.get('next_data') is not None,
            "status": "completed"
        }
        print(f"   APIs discovered: {len(scrape_results.get('api_calls', []))}")
        print(f"   JS bundles: {len(scrape_results.get('js_files', []))}")
        
        # Stage 3: Data Source Mapping
        print("\n📍 STAGE 3: DATA SOURCE MAPPING")
        data_sources = self.map_data_sources()
        results["stages"]["data_sources"] = {
            "sources_mapped": len(data_sources),
            "sources": [s["name"] for s in data_sources],
            "status": "completed"
        }
        print(f"   Sources identified: {len(data_sources)}")
        for source in data_sources:
            print(f"      - {source['name']}: {', '.join(source['data_types'][:3])}")
        
        # Stage 4: Code Generation
        print("\n📍 STAGE 4: CODE GENERATION")
        output_dir = CONFIG["output_dir"]
        self.generate_project_structure(output_dir)
        
        # Write files
        files_written = []
        
        with open(f"{output_dir}/package.json", "w") as f:
            f.write(self.generate_package_json())
            files_written.append("package.json")
        
        with open(f"{output_dir}/src/components/map/MapContainer.tsx", "w") as f:
            f.write(self.generate_map_component())
            files_written.append("src/components/map/MapContainer.tsx")
        
        with open(f"{output_dir}/.github/workflows/pipeline.yml", "w") as f:
            f.write(self.generate_github_workflow())
            files_written.append(".github/workflows/pipeline.yml")
        
        results["stages"]["code_generation"] = {
            "files_written": files_written,
            "output_dir": output_dir,
            "status": "completed"
        }
        print(f"   Files generated: {len(files_written)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETED")
        print("=" * 60)
        
        results["status"] = "completed"
        results["summary"] = {
            "tech_stack": tech_stack.get("framework", "Unknown"),
            "data_sources": len(data_sources),
            "files_generated": len(files_written),
            "output_dir": output_dir
        }
        
        return results


# ==================== DATA SCRAPERS ====================

class ZillowScraper:
    """Scraper for Zillow Research Data (CSV downloads)."""
    
    ENDPOINTS = {
        "zhvi_zip": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "zhvi_metro": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "zhvi_state": "https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "zori_metro": "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_sa_month.csv",
        "inventory": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
    }
    
    def __init__(self, output_dir: str = "data/zillow"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(timeout=120.0)
    
    def download_all(self) -> Dict[str, str]:
        """Download all Zillow datasets."""
        results = {}
        
        for name, url in self.ENDPOINTS.items():
            print(f"📥 Downloading {name}...")
            try:
                response = self.client.get(url)
                response.raise_for_status()
                
                filepath = self.output_dir / f"{name}.csv"
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                results[name] = str(filepath)
                print(f"   ✅ Saved to {filepath}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[name] = None
        
        return results
    
    def __del__(self):
        self.client.close()


class CensusScraper:
    """Scraper for US Census Bureau API."""
    
    BASE_URL = "https://api.census.gov/data"
    
    # Key ACS5 variables
    VARIABLES = {
        "B25077_001E": "median_home_value",
        "B19013_001E": "median_household_income",
        "B01003_001E": "total_population",
        "B25002_002E": "occupied_housing_units",
        "B25002_003E": "vacant_housing_units",
        "B25064_001E": "median_gross_rent",
        "B25003_002E": "owner_occupied_units",
        "B25003_003E": "renter_occupied_units",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=60.0)
    
    def get_zip_data(self, year: int = 2022) -> List[Dict]:
        """Get ACS data by ZIP code."""
        variables = ",".join(self.VARIABLES.keys())
        url = f"{self.BASE_URL}/{year}/acs/acs5"
        
        params = {
            "get": variables,
            "for": "zip code tabulation area:*",
            "key": self.api_key
        }
        
        print(f"📊 Fetching Census ACS5 data for {year}...")
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            headers = data[0]
            rows = data[1:]
            
            results = []
            for row in rows:
                record = dict(zip(headers, row))
                # Rename variables
                for census_var, friendly_name in self.VARIABLES.items():
                    if census_var in record:
                        value = record.pop(census_var)
                        record[friendly_name] = int(value) if value and value != '-' else None
                
                record["zip_code"] = record.pop("zip code tabulation area", None)
                record["year"] = year
                results.append(record)
            
            print(f"   ✅ Retrieved {len(results)} ZIP codes")
            return results
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def __del__(self):
        self.client.close()


# ==================== ML SCORING ====================

class ForecastScorer:
    """Calculate Reventure-style forecast scores."""
    
    @staticmethod
    def calculate_price_forecast_score(metrics: Dict) -> int:
        """
        Calculate price forecast score (0-100).
        
        Components:
        - Inventory level (20%): Higher = lower score
        - Days on market (20%): Higher = lower score  
        - Price cut % (20%): Higher = lower score
        - Recent appreciation (25%): Lower = lower score
        - Mortgage rate impact (15%): Higher = lower score
        """
        scores = []
        
        # Inventory score (inverted - lower inventory = higher score)
        if metrics.get('inventory_vs_avg'):
            inv_ratio = metrics['inventory_vs_avg']
            inv_score = max(0, min(100, 100 - (inv_ratio - 1) * 50))
            scores.append(('inventory', inv_score, 0.20))
        
        # DOM score (inverted)
        if metrics.get('days_on_market'):
            dom = metrics['days_on_market']
            dom_score = max(0, min(100, 100 - (dom - 30) * 1.5))
            scores.append(('dom', dom_score, 0.20))
        
        # Price cut score (inverted)
        if metrics.get('price_cut_pct') is not None:
            pc_pct = metrics['price_cut_pct']
            pc_score = max(0, min(100, 100 - pc_pct * 3))
            scores.append(('price_cuts', pc_score, 0.20))
        
        # Appreciation score
        if metrics.get('yoy_price_change') is not None:
            yoy = metrics['yoy_price_change']
            app_score = max(0, min(100, 50 + yoy * 5))
            scores.append(('appreciation', app_score, 0.25))
        
        # Rate impact score
        if metrics.get('mortgage_rate'):
            rate = metrics['mortgage_rate']
            rate_score = max(0, min(100, 100 - (rate - 5) * 15))
            scores.append(('rate_impact', rate_score, 0.15))
        
        if not scores:
            return 50  # Neutral score if no data
        
        # Weighted average
        total_weight = sum(s[2] for s in scores)
        weighted_sum = sum(s[1] * s[2] for s in scores)
        
        return int(round(weighted_sum / total_weight))
    
    @staticmethod
    def calculate_crash_potential(metrics: Dict) -> int:
        """
        Calculate crash potential score (0-100).
        Higher = more risk.
        """
        risk_factors = []
        
        # Price-to-income ratio risk
        if metrics.get('price_to_income'):
            pti = metrics['price_to_income']
            # 3x is healthy, 5x+ is risky
            pti_risk = max(0, min(100, (pti - 3) * 25))
            risk_factors.append(pti_risk)
        
        # Rapid appreciation risk
        if metrics.get('three_year_appreciation'):
            app_3y = metrics['three_year_appreciation']
            # 30%+ 3-year appreciation is risky
            app_risk = max(0, min(100, (app_3y - 15) * 2))
            risk_factors.append(app_risk)
        
        # Inventory surge risk
        if metrics.get('inventory_yoy_change'):
            inv_change = metrics['inventory_yoy_change']
            # 50%+ inventory increase is risky
            inv_risk = max(0, min(100, inv_change * 1.5))
            risk_factors.append(inv_risk)
        
        if not risk_factors:
            return 30  # Default moderate risk
        
        return int(round(sum(risk_factors) / len(risk_factors)))


# ==================== CLI ====================

async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Reventure Clone Agent")
    parser.add_argument("--discover", action="store_true", help="Run discovery only")
    parser.add_argument("--scrape", action="store_true", help="Run scraping")
    parser.add_argument("--generate", action="store_true", help="Generate code")
    parser.add_argument("--full", action="store_true", help="Run full pipeline")
    parser.add_argument("--output", default="reventure-clone", help="Output directory")
    
    args = parser.parse_args()
    
    CONFIG["output_dir"] = args.output
    
    async with ReventureCloneAgent() as agent:
        if args.full or not any([args.discover, args.scrape, args.generate]):
            results = await agent.run()
            print(json.dumps(results, indent=2))
        elif args.discover:
            tech = await agent.discover_tech_stack(CONFIG["target_url"])
            print(json.dumps(tech, indent=2))
        elif args.scrape:
            data = await agent.scrape_with_playwright(CONFIG["map_url"])
            print(f"HTML length: {len(data.get('html', ''))}")
            print(f"APIs found: {len(data.get('api_calls', []))}")
        elif args.generate:
            agent.generate_project_structure(args.output)
            print(f"Project generated in {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
