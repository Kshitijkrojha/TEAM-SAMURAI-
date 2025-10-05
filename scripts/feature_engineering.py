# scripts/feature_engineering.py
import pandas as pd
import os

def create_features(df, airports_path='data/Airports Data.csv'):
    """
    Engineers all basic and advanced features for the difficulty score analysis.
    """
    print("Step 2: Creating basic and advanced features...")
    airports_df = pd.read_csv(airports_path)
    
    # --- Basic Features ---
    df['ground_time_deficit'] = df['scheduled_ground_time_minutes'] - df['minimum_turn_minutes']
    df['load_factor'] = df['total_pax'] / df['total_seats'].replace(0, pd.NA)
    df['ssr_per_pax'] = df['ssr_count'] / df['total_pax'].replace(0, pd.NA)
    df['child_ratio'] = (df['lap_child_count'] + df['is_child_count']) / df['total_pax'].replace(0, pd.NA)
    df['basic_economy_ratio'] = df['basic_economy_pax'] / df['total_pax'].replace(0, pd.NA)
    df['total_bags'] = df['Checked'] + df['Transfer']
    df['bags_per_pax'] = df['total_bags'] / df['total_pax'].replace(0, pd.NA)
    
    airports_df.rename(columns={'airport_iata_code': 'scheduled_arrival_station_code'}, inplace=True)
    df = pd.merge(df, airports_df[['scheduled_arrival_station_code', 'iso_country_code']], on='scheduled_arrival_station_code', how='left')
    df['is_international'] = (df['iso_country_code'] != 'US').astype(int)

    # --- Advanced Features ---
    def assign_fleet_complexity(fleet_type):
        if any(s in str(fleet_type) for s in ['B777', 'B787', 'B767']): return 3
        if any(s in str(fleet_type) for s in ['B737', 'A320', 'A319']): return 2
        if any(s in str(fleet_type) for s in ['ERJ', 'CRJ']): return 1
        return 1
    df['fleet_complexity_score'] = df['fleet_type'].apply(assign_fleet_complexity)

    df['departure_hour'] = pd.to_datetime(df['scheduled_departure_datetime_local']).dt.hour
    def assign_time_pressure(hour):
        if 7 <= hour <= 9 or 16 <= hour <= 19: return 3
        if 5 <= hour <= 6 or 10 <= hour <= 15 or 20 <= hour <= 21: return 2
        return 1
    df['time_pressure_score'] = df['departure_hour'].apply(assign_time_pressure)

    df['transfer_bag_ratio'] = df['Transfer'] / df['total_bags'].replace(0, pd.NA)
    high_transfer = df.groupby('scheduled_departure_date_local')['transfer_bag_ratio'].transform(lambda x: x.quantile(0.75))
    low_ground_time = df.groupby('scheduled_departure_date_local')['ground_time_deficit'].transform(lambda x: x.quantile(0.25))
    df['is_high_risk_transfer'] = ((df['transfer_bag_ratio'] >= high_transfer) & (df['ground_time_deficit'] <= low_ground_time)).astype(int)

    df.fillna(0, inplace=True)
    print("Feature engineering complete.")
    return df