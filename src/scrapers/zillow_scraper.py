#!/usr/bin/env python3
"""
Zillow Research Data Scraper
Downloads publicly available CSV datasets from Zillow Research.

Data Sources:
- ZHVI (Zillow Home Value Index) - Median home values
- ZORI (Zillow Observed Rent Index) - Rental prices
- Inventory metrics
- Listings data

Usage:
    python zillow_scraper.py [--all | --zhvi | --zori | --inventory]
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import pandas as pd

# Zillow Research Data endpoints
ZILLOW_ENDPOINTS = {
    # Home Values (ZHVI)
    "zhvi_zip": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zhvi/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "description": "Home values by ZIP code (all tiers)",
        "geo_level": "zip"
    },
    "zhvi_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zhvi/Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "description": "Home values by Metro area",
        "geo_level": "metro"
    },
    "zhvi_state": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "description": "Home values by State",
        "geo_level": "state"
    },
    "zhvi_county": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
        "description": "Home values by County",
        "geo_level": "county"
    },
    
    # Rent Index (ZORI)
    "zori_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zori/Metro_zori_uc_sfrcondomfr_sm_sa_month.csv",
        "description": "Rent index by Metro area",
        "geo_level": "metro"
    },
    "zori_zip": {
        "url": "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_sa_month.csv",
        "description": "Rent index by ZIP code",
        "geo_level": "zip"
    },
    
    # Inventory & Listings
    "inventory_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/invt_fs/Metro_invt_fs_uc_sfrcondo_sm_month.csv",
        "description": "For-sale inventory by Metro",
        "geo_level": "metro"
    },
    "new_listings_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/new_listings/Metro_new_listings_uc_sfrcondo_sm_month.csv",
        "description": "New listings by Metro",
        "geo_level": "metro"
    },
    "days_on_market_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/mean_doz/Metro_mean_doz_uc_sfrcondo_sm_month.csv",
        "description": "Days on Zillow by Metro",
        "geo_level": "metro"
    },
    "price_cuts_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/pct_listings_price_cut/Metro_pct_listings_price_cut_uc_sfrcondo_sm_month.csv",
        "description": "Price cut percentage by Metro",
        "geo_level": "metro"
    },
    
    # Sale Prices
    "sale_price_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/median_sale_price/Metro_median_sale_price_uc_sfrcondo_sm_sa_month.csv",
        "description": "Median sale price by Metro",
        "geo_level": "metro"
    },
    "sale_to_list_metro": {
        "url": "https://files.zillowstatic.com/research/public_csvs/sale_to_list/Metro_sale_to_list_uc_sfrcondo_sm_month.csv",
        "description": "Sale-to-list ratio by Metro",
        "geo_level": "metro"
    }
}


class ZillowScraper:
    """
    Scraper for Zillow Research public data.
    All data is freely available for public use with attribution.
    """
    
    def __init__(self, output_dir: str = "data/zillow"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(
            timeout=180.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; ReventureClone/1.0; +https://github.com/breverdbidder/reventure-clone)"
            }
        )
        self.downloaded: Dict[str, str] = {}
    
    def download(self, dataset_name: str) -> Optional[str]:
        """
        Download a single Zillow dataset.
        
        Args:
            dataset_name: Key from ZILLOW_ENDPOINTS
            
        Returns:
            Path to downloaded file, or None on error
        """
        if dataset_name not in ZILLOW_ENDPOINTS:
            print(f"❌ Unknown dataset: {dataset_name}")
            return None
        
        endpoint = ZILLOW_ENDPOINTS[dataset_name]
        url = endpoint["url"]
        description = endpoint["description"]
        
        print(f"📥 Downloading: {description}")
        print(f"   URL: {url}")
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            # Save to file
            filepath = self.output_dir / f"{dataset_name}.csv"
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            # Verify it's valid CSV
            df = pd.read_csv(filepath, nrows=5)
            row_count = len(pd.read_csv(filepath))
            
            print(f"   ✅ Saved: {filepath}")
            print(f"   📊 Rows: {row_count:,} | Columns: {len(df.columns)}")
            
            self.downloaded[dataset_name] = str(filepath)
            return str(filepath)
            
        except httpx.HTTPStatusError as e:
            print(f"   ❌ HTTP Error {e.response.status_code}: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def download_all(self, category: Optional[str] = None) -> Dict[str, str]:
        """
        Download all datasets, optionally filtered by category.
        
        Args:
            category: Optional filter - 'zhvi', 'zori', 'inventory', or None for all
            
        Returns:
            Dict of dataset_name -> filepath
        """
        datasets = list(ZILLOW_ENDPOINTS.keys())
        
        if category:
            datasets = [d for d in datasets if category in d.lower()]
        
        print(f"📦 Downloading {len(datasets)} Zillow datasets...")
        print("=" * 60)
        
        results = {}
        for dataset in datasets:
            filepath = self.download(dataset)
            if filepath:
                results[dataset] = filepath
            print()
        
        print("=" * 60)
        print(f"✅ Downloaded {len(results)}/{len(datasets)} datasets")
        
        return results
    
    def to_long_format(self, filepath: str, dataset_name: str) -> pd.DataFrame:
        """
        Convert wide Zillow format to long format for database storage.
        
        Zillow CSVs have columns: RegionID, RegionName, State, ..., 2020-01, 2020-02, ...
        We convert to: geo_id, geo_name, state, metric_date, value
        """
        df = pd.read_csv(filepath)
        
        # Identify date columns (YYYY-MM format)
        date_cols = [c for c in df.columns if len(c) == 7 and c[4] == '-']
        id_cols = [c for c in df.columns if c not in date_cols]
        
        # Melt to long format
        df_long = df.melt(
            id_vars=id_cols,
            value_vars=date_cols,
            var_name='metric_date',
            value_name='value'
        )
        
        # Parse dates
        df_long['metric_date'] = pd.to_datetime(df_long['metric_date'] + '-01')
        
        # Standardize column names
        col_mapping = {
            'RegionID': 'geo_id',
            'RegionName': 'geo_name',
            'StateName': 'state',
            'State': 'state_code',
            'Metro': 'metro',
            'CountyName': 'county',
            'City': 'city',
            'SizeRank': 'size_rank',
            'RegionType': 'region_type'
        }
        
        df_long = df_long.rename(columns={
            k: v for k, v in col_mapping.items() if k in df_long.columns
        })
        
        # Add metadata
        df_long['data_source'] = 'zillow'
        df_long['dataset'] = dataset_name
        df_long['scraped_at'] = datetime.now().isoformat()
        
        return df_long
    
    def get_latest_values(self, filepath: str) -> pd.DataFrame:
        """
        Get only the most recent month's values.
        Useful for current market snapshots.
        """
        df = pd.read_csv(filepath)
        
        # Find most recent date column
        date_cols = sorted([c for c in df.columns if len(c) == 7 and c[4] == '-'])
        if not date_cols:
            return df
        
        latest_col = date_cols[-1]
        id_cols = [c for c in df.columns if c not in date_cols]
        
        # Keep only ID columns + latest value
        result = df[id_cols + [latest_col]].copy()
        result = result.rename(columns={latest_col: 'value'})
        result['metric_date'] = latest_col
        
        return result
    
    def calculate_yoy_change(self, filepath: str) -> pd.DataFrame:
        """
        Calculate year-over-year percentage change.
        """
        df = pd.read_csv(filepath)
        
        date_cols = sorted([c for c in df.columns if len(c) == 7 and c[4] == '-'])
        if len(date_cols) < 13:  # Need at least 13 months for YoY
            print("⚠️ Not enough data for YoY calculation")
            return pd.DataFrame()
        
        latest = date_cols[-1]
        year_ago = date_cols[-13]
        
        id_cols = [c for c in df.columns if c not in date_cols]
        
        result = df[id_cols].copy()
        result['current_value'] = df[latest]
        result['year_ago_value'] = df[year_ago]
        result['yoy_change'] = ((df[latest] - df[year_ago]) / df[year_ago] * 100).round(2)
        result['metric_date'] = latest
        
        return result
    
    def upload_to_supabase(
        self, 
        df: pd.DataFrame, 
        table_name: str,
        supabase_url: str,
        supabase_key: str
    ) -> bool:
        """
        Upload processed data to Supabase.
        """
        try:
            from supabase import create_client
            
            client = create_client(supabase_url, supabase_key)
            
            # Convert to records
            records = df.to_dict('records')
            
            # Batch insert (Supabase limit is 1000 per request)
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                client.table(table_name).upsert(batch).execute()
                print(f"   📤 Uploaded batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")
            
            print(f"✅ Uploaded {len(records)} records to {table_name}")
            return True
            
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def close(self):
        """Close HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zillow Research Data Scraper")
    parser.add_argument("--all", action="store_true", help="Download all datasets")
    parser.add_argument("--zhvi", action="store_true", help="Download home value data")
    parser.add_argument("--zori", action="store_true", help="Download rent data")
    parser.add_argument("--inventory", action="store_true", help="Download inventory data")
    parser.add_argument("--output", default="data/zillow", help="Output directory")
    parser.add_argument("--supabase", action="store_true", help="Upload to Supabase")
    parser.add_argument("--list", action="store_true", help="List available datasets")
    
    args = parser.parse_args()
    
    if args.list:
        print("📊 Available Zillow Datasets:")
        print("-" * 60)
        for name, info in ZILLOW_ENDPOINTS.items():
            print(f"  {name}")
            print(f"    {info['description']}")
            print(f"    Level: {info['geo_level']}")
            print()
        return
    
    with ZillowScraper(output_dir=args.output) as scraper:
        if args.zhvi:
            scraper.download_all(category="zhvi")
        elif args.zori:
            scraper.download_all(category="zori")
        elif args.inventory:
            scraper.download_all(category="inventory")
        else:
            # Default: download most important datasets
            key_datasets = [
                "zhvi_zip", "zhvi_metro", "zhvi_state",
                "zori_metro", "inventory_metro", "days_on_market_metro",
                "price_cuts_metro", "sale_price_metro"
            ]
            for dataset in key_datasets:
                scraper.download(dataset)
                print()
        
        # Optional: Upload to Supabase
        if args.supabase:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                print("❌ SUPABASE_URL and SUPABASE_KEY environment variables required")
                return
            
            for name, filepath in scraper.downloaded.items():
                print(f"\n📤 Processing {name} for upload...")
                df = scraper.to_long_format(filepath, name)
                
                # Only upload recent data (last 12 months)
                df = df[df['metric_date'] >= (datetime.now() - pd.Timedelta(days=365))]
                
                scraper.upload_to_supabase(
                    df, 
                    f"zillow_{ZILLOW_ENDPOINTS[name]['geo_level']}", 
                    supabase_url, 
                    supabase_key
                )


if __name__ == "__main__":
    main()
