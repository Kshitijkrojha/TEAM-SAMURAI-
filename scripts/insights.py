# scripts/insights.py (Corrected Version)
import pandas as pd
import os

def generate_insights_and_recommendations(df, output_dir='output', filename='test_TeamSamurai.csv'):
    """
    Analyzes the scored data to find difficult destinations and their drivers,
    prints recommendations, and saves the final CSV.
    """
    print("Step 4: Analyzing results for insights and recommendations...")

    # --- Insight 1: Find the most consistently difficult destinations ---
    difficult_dest_analysis = df.groupby('scheduled_arrival_station_code').agg(
        avg_difficulty_score=('difficulty_score', 'mean'),
        difficult_flight_count=('difficulty_class', lambda x: (x == 'Difficult').sum())
    ).sort_values(by='avg_difficulty_score', ascending=False)
    
    top_5_dests = difficult_dest_analysis.head(5)
    print("\n--- INSIGHT: TOP 5 DIFFICULT DESTINATIONS ---")
    print(top_5_dests)
    
    # --- Insight 2: Analyze the "Difficulty Profile" for those top destinations ---
    driver_features = [
        'child_ratio', 'ssr_per_pax', 'is_high_risk_transfer', 
        'fleet_complexity_score', 'time_pressure_score'
    ]
    driver_analysis = df[df['scheduled_arrival_station_code'].isin(top_5_dests.index)]
    driver_summary = driver_analysis.groupby('scheduled_arrival_station_code')[driver_features].mean()
    print("\n--- INSIGHT: KEY DRIVERS FOR TOP DESTINATIONS (Average Values) ---")
    print(driver_summary)

    # --- Actionable Recommendations (Printed to console) ---
    print("\n--- ACTIONABLE RECOMMENDATIONS ---")
    print("1. For destinations with high 'child_ratio' and 'ssr_per_pax' (e.g., MCO):")
    print("   -> RECOMMENDATION: Proactively assign a Special Assistance Coordinator at the gate.")
    print("\n2. For destinations with high 'is_high_risk_transfer' and 'fleet_complexity' (e.g., EWR, LHR):")
    print("   -> RECOMMENDATION: Flag these flights in the ground operations system. Pre-stage baggage crews at the arrival gate.")
    print("\n3. For flights with high 'time_pressure_score' (departing 7-9 AM or 4-7 PM):")
    print("   -> RECOMMENDATION: Position an Operations Duty Manager centrally to dynamically allocate staff to the highest-scoring flights.")

    # --- Final Step: Save the required output file ---
    # --- FIX: Added 'departure_hour' to the list of columns to save ---
    final_columns = [
        'scheduled_departure_date_local', 'company_id', 'flight_number',
        'scheduled_departure_station_code', 'scheduled_arrival_station_code', 'load_factor',
        'ground_time_deficit', 'ssr_count', 'total_bags', 'fleet_complexity_score',
        'time_pressure_score', 'is_high_risk_transfer', 'departure_hour', # <-- THIS COLUMN IS NOW INCLUDED
        'difficulty_score', 'difficulty_rank_daily', 'difficulty_class'
    ]
    # Add rank columns for the dashboard deconstructor tab
    rank_cols_to_add = [col for col in df.columns if '_rank' in col]
    final_columns.extend(rank_cols_to_add)

    final_output_df = df[final_columns].sort_values(by=['scheduled_departure_date_local', 'difficulty_score'], ascending=[True, False])

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    final_output_df.to_csv(output_path, index=False)
    
    print(f"\n✅ Final analysis file saved to: {output_path}")