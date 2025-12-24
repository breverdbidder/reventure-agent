#!/usr/bin/env python3
"""
US Census Bureau API Scraper
Fetches demographic and housing data from the American Community Survey.

Data includes:
- Population and demographics
- Housing characteristics
- Income levels
- Home values
- Vacancy rates

API Documentation: https://www.census.gov/data/developers/data-sets.html
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import httpx
import pandas as pd

# Census API configuration
CENSUS_BASE_URL = "https://api.census.gov/data"

# ACS 5-Year Estimates Variables
# Full list: https://api.census.gov/data/2022/acs/acs5/variables.html
ACS_VARIABLES = {
    # Population
    "B01003_001E": "total_population",
    "B01002_001E": "median_age",
    
    # Housing Units
    "B25001_001E": "total_housing_units",
    "B25002_002E": "occupied_housing_units",
    "B25002_003E": "vacant_housing_units",
    "B25003_002E": "owner_occupied_units",
    "B25003_003E": "renter_occupied_units",
    
    # Home Values
    "B25077_001E": "median_home_value",
    "B25075_001E": "home_value_total",  # Base for distribution
    
    # Rent
    "B25064_001E": "median_gross_rent",
    "B25071_001E": "median_rent_as_pct_income",
    
    # Income
    "B19013_001E": "median_household_income",
    "B19301_001E": "per_capita_income",
    
    # Housing Costs
    "B25088_002E": "median_mortgage_payment",
    "B25094_001E": "selected_monthly_owner_costs",
    
    # Housing Characteristics
    "B25034_001E": "total_year_built",  # For median year calculation
    "B25035_001E": "median_year_built",
    "B25018_001E": "median_rooms",
}

# Geographic levels
GEO_LEVELS = {
    "state": "state:*",
    "county": "county:*",
    "zip": "zip code tabulation area:*",
    "place": "place:*",  # Cities
    "tract": "tract:*",  # Census tracts
}


class CensusScraper:
    """
    Scraper for US Census Bureau API.
    Requires a free API key from: https://api.census.gov/data/key_signup.html
    """
    
    def __init__(self, api_key: str, output_dir: str = "data/census"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(
            timeout=120.0,
            headers={"User-Agent": "ReventureClone/1.0"}
        )
    
    def get_acs_data(
        self,
        year: int = 2022,
        geo_level: str = "zip",
        state: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Fetch ACS 5-Year Estimates data.
        
        Args:
            year: Survey year (2022 is latest as of 2024)
            geo_level: Geographic level (state, county, zip, place, tract)
            state: Optional state FIPS code filter
            variables: List of variable codes, or None for all
            
        Returns:
            DataFrame with requested data
        """
        if variables is None:
            variables = list(ACS_VARIABLES.keys())
        
        # Build API URL
        url = f"{CENSUS_BASE_URL}/{year}/acs/acs5"
        
        # Variables to request
        var_string = ",".join(variables)
        
        # Geographic filter
        geo = GEO_LEVELS.get(geo_level, GEO_LEVELS["state"])
        
        params = {
            "get": var_string,
            "for": geo,
            "key": self.api_key
        }
        
        # Add state filter if specified
        if state and geo_level not in ["state"]:
            params["in"] = f"state:{state}"
        
        print(f"📊 Fetching Census ACS {year} data...")
        print(f"   Geographic level: {geo_level}")
        print(f"   Variables: {len(variables)}")
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                print("   ⚠️ No data returned")
                return pd.DataFrame()
            
            # First row is headers
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            
            # Rename columns using friendly names
            rename_map = {k: v for k, v in ACS_VARIABLES.items() if k in df.columns}
            df = df.rename(columns=rename_map)
            
            # Convert numeric columns
            for col in df.columns:
                if col not in ['state', 'county', 'zip code tabulation area', 'place', 'tract', 'NAME']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Standardize geography column names
            geo_renames = {
                'zip code tabulation area': 'zip_code',
                'NAME': 'geo_name'
            }
            df = df.rename(columns={k: v for k, v in geo_renames.items() if k in df.columns})
            
            # Add metadata
            df['year'] = year
            df['geo_level'] = geo_level
            df['scraped_at'] = datetime.now().isoformat()
            
            print(f"   ✅ Retrieved {len(df):,} records")
            
            return df
            
        except httpx.HTTPStatusError as e:
            print(f"   ❌ HTTP Error {e.response.status_code}")
            if e.response.status_code == 400:
                print(f"   Response: {e.response.text[:500]}")
            return pd.DataFrame()
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return pd.DataFrame()
    
    def get_population_estimates(
        self,
        year: int = 2023,
        geo_level: str = "state"
    ) -> pd.DataFrame:
        """
        Fetch Population Estimates Program (PEP) data.
        More current than ACS for population.
        """
        url = f"{CENSUS_BASE_URL}/{year}/pep/population"
        
        variables = ["POP", "NPOPCHG", "NATURALCHG", "NETMIG"]
        
        params = {
            "get": ",".join(variables),
            "for": GEO_LEVELS.get(geo_level, "state:*"),
            "key": self.api_key
        }
        
        print(f"📊 Fetching Census PEP {year} data...")
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            
            rename_map = {
                "POP": "population",
                "NPOPCHG": "population_change",
                "NATURALCHG": "natural_change",
                "NETMIG": "net_migration"
            }
            df = df.rename(columns=rename_map)
            
            for col in ['population', 'population_change', 'natural_change', 'net_migration']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['year'] = year
            
            print(f"   ✅ Retrieved {len(df):,} records")
            return df
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return pd.DataFrame()
    
    def get_building_permits(
        self,
        year: int = 2023,
        geo_level: str = "state"
    ) -> pd.DataFrame:
        """
        Fetch Building Permits Survey data.
        Indicates new construction activity.
        """
        # Building permits endpoint is different
        url = f"{CENSUS_BASE_URL}/timeseries/bps"
        
        params = {
            "get": "PERMIT,PERMIT_UNITS",
            "for": GEO_LEVELS.get(geo_level, "state:*"),
            "time": str(year),
            "key": self.api_key
        }
        
        print(f"📊 Fetching Building Permits {year} data...")
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            df['year'] = year
            
            print(f"   ✅ Retrieved {len(df):,} records")
            return df
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return pd.DataFrame()
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived housing metrics from raw Census data.
        """
        # Vacancy rate
        if 'vacant_housing_units' in df.columns and 'total_housing_units' in df.columns:
            df['vacancy_rate'] = (
                df['vacant_housing_units'] / df['total_housing_units'] * 100
            ).round(2)
        
        # Owner-occupied percentage
        if 'owner_occupied_units' in df.columns and 'occupied_housing_units' in df.columns:
            df['owner_occupied_pct'] = (
                df['owner_occupied_units'] / df['occupied_housing_units'] * 100
            ).round(2)
        
        # Price-to-income ratio
        if 'median_home_value' in df.columns and 'median_household_income' in df.columns:
            df['price_to_income'] = (
                df['median_home_value'] / df['median_household_income']
            ).round(2)
        
        # Price-to-rent ratio
        if 'median_home_value' in df.columns and 'median_gross_rent' in df.columns:
            # Annual rent
            df['price_to_rent'] = (
                df['median_home_value'] / (df['median_gross_rent'] * 12)
            ).round(1)
        
        # Affordability index (income needed to afford median home)
        if 'median_home_value' in df.columns:
            # Assume 28% of income to housing, 20% down, 7% rate, 30 year
            monthly_payment = df['median_home_value'] * 0.8 * (0.07/12) / (1 - (1 + 0.07/12)**-360)
            df['income_needed'] = (monthly_payment * 12 / 0.28).round(0)
        
        return df
    
    def download_all_geographies(
        self,
        year: int = 2022,
        geo_levels: Optional[List[str]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple geographic levels.
        """
        if geo_levels is None:
            geo_levels = ["state", "county", "zip"]
        
        results = {}
        
        for level in geo_levels:
            print(f"\n{'='*60}")
            print(f"Processing {level} level data...")
            
            df = self.get_acs_data(year=year, geo_level=level)
            
            if not df.empty:
                # Calculate derived metrics
                df = self.calculate_derived_metrics(df)
                
                # Save to file
                filepath = self.output_dir / f"census_acs_{level}_{year}.csv"
                df.to_csv(filepath, index=False)
                print(f"   💾 Saved to {filepath}")
                
                results[level] = df
        
        return results
    
    def get_state_fips_codes(self) -> Dict[str, str]:
        """
        Get mapping of state abbreviations to FIPS codes.
        """
        return {
            "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
            "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
            "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
            "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
            "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
            "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
            "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
            "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
            "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
            "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
            "DC": "11", "PR": "72"
        }
    
    def upload_to_supabase(
        self,
        df: pd.DataFrame,
        table_name: str,
        supabase_url: str,
        supabase_key: str
    ) -> bool:
        """Upload data to Supabase."""
        try:
            from supabase import create_client
            
            client = create_client(supabase_url, supabase_key)
            
            # Clean DataFrame for JSON serialization
            df = df.replace({pd.NA: None, float('inf'): None, float('-inf'): None})
            df = df.where(pd.notnull(df), None)
            
            records = df.to_dict('records')
            
            # Batch insert
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                client.table(table_name).upsert(batch).execute()
                print(f"   📤 Uploaded batch {i//batch_size + 1}")
            
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
    
    parser = argparse.ArgumentParser(description="US Census Bureau API Scraper")
    parser.add_argument("--year", type=int, default=2022, help="Survey year")
    parser.add_argument("--geo", choices=["state", "county", "zip", "place", "tract"],
                       default="zip", help="Geographic level")
    parser.add_argument("--state", help="State FIPS code filter")
    parser.add_argument("--all", action="store_true", help="Download all geo levels")
    parser.add_argument("--output", default="data/census", help="Output directory")
    parser.add_argument("--supabase", action="store_true", help="Upload to Supabase")
    
    args = parser.parse_args()
    
    api_key = os.getenv("CENSUS_API_KEY")
    if not api_key:
        print("❌ CENSUS_API_KEY environment variable required")
        print("   Get a free key at: https://api.census.gov/data/key_signup.html")
        return
    
    with CensusScraper(api_key=api_key, output_dir=args.output) as scraper:
        if args.all:
            results = scraper.download_all_geographies(year=args.year)
            print(f"\n✅ Downloaded {len(results)} geographic levels")
        else:
            df = scraper.get_acs_data(
                year=args.year,
                geo_level=args.geo,
                state=args.state
            )
            
            if not df.empty:
                # Calculate derived metrics
                df = scraper.calculate_derived_metrics(df)
                
                # Save
                filepath = scraper.output_dir / f"census_acs_{args.geo}_{args.year}.csv"
                df.to_csv(filepath, index=False)
                print(f"💾 Saved to {filepath}")
                
                # Preview
                print("\n📋 Sample data:")
                print(df.head())
                
                # Optional upload
                if args.supabase:
                    supabase_url = os.getenv("SUPABASE_URL")
                    supabase_key = os.getenv("SUPABASE_KEY")
                    
                    if supabase_url and supabase_key:
                        scraper.upload_to_supabase(
                            df, f"census_{args.geo}", supabase_url, supabase_key
                        )


if __name__ == "__main__":
    main()
