# scripts/data_loader.py
import pandas as pd
import os

def load_and_prepare_all_data(data_path='data'):
    """
    Loads all raw CSV files, handles data-specific cleaning and renaming,
    and merges them into a single flight-level DataFrame.
    """
    print("Step 1: Loading and preparing data...")
    try:
        flight_df = pd.read_csv(os.path.join(data_path, 'Flight Level Data.csv'))
        pnr_flight_df = pd.read_csv(os.path.join(data_path, 'PNR+Flight+Level+Data.csv'))
        pnr_remarks_df = pd.read_csv(os.path.join(data_path, 'PNR Remark Level Data.csv'))
        bag_df = pd.read_csv(os.path.join(data_path, 'Bag+Level+Data.csv'))
    except FileNotFoundError as e:
        print(f"ERROR: Could not find data file - {e}. Make sure the 'data' folder is correct.")
        return None

    flight_key = [
        'scheduled_departure_date_local', 'company_id', 'flight_number',
        'scheduled_departure_station_code', 'scheduled_arrival_station_code'
    ]

    # --- PNR Aggregation (Tailored for your files) ---
    if 'basic_economy_ind' in pnr_flight_df.columns:
        pnr_flight_df.rename(columns={'basic_economy_ind': 'basic_economy_pax'}, inplace=True)
    pnr_agg = pnr_flight_df.groupby(flight_key).agg(
        total_pax=('total_pax', 'sum'), lap_child_count=('lap_child_count', 'sum'),
        is_child_count=('is_child', lambda x: (x == 'Y').sum()),
        is_stroller_user_count=('is_stroller_user', lambda x: (x == 'Y').sum()),
        basic_economy_pax=('basic_economy_pax', 'sum')
    ).reset_index()

    # --- SSR Aggregation ---
    pnr_key_map = pnr_flight_df[['record_locator'] + flight_key].drop_duplicates()
    remarks_with_flight_key = pd.merge(
        pnr_remarks_df.drop(columns=['flight_number'], errors='ignore'),
        pnr_key_map, on='record_locator', how='left'
    )
    ssr_agg = remarks_with_flight_key.groupby(flight_key).size().reset_index(name='ssr_count')

    # --- Bag Aggregation (Tailored for your files) ---
    bag_agg = bag_df.pivot_table(
        index=flight_key, columns='bag_type', values='bag_tag_unique_number',
        aggfunc='count', fill_value=0
    ).reset_index()
    bag_agg.columns.name = None
    if 'Origin' in bag_agg.columns: bag_agg.rename(columns={'Origin': 'Checked'}, inplace=True)
    if 'Transfer' not in bag_agg.columns: bag_agg['Transfer'] = 0

    # --- Final Merge ---
    master_df = pd.merge(flight_df, pnr_agg, on=flight_key, how='left')
    master_df = pd.merge(master_df, ssr_agg, on=flight_key, how='left')
    master_df = pd.merge(master_df, bag_agg, on=flight_key, how='left')
    
    count_cols = ['total_pax', 'lap_child_count', 'is_child_count', 'basic_economy_pax',
                  'is_stroller_user_count', 'ssr_count', 'Checked', 'Transfer']
    for col in count_cols:
        if col in master_df.columns: master_df[col] = master_df[col].fillna(0)

    print("Data loading and merging complete.")
    return master_df