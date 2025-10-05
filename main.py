# main.py
# Main script to run the entire flight difficulty analysis pipeline.

# Import the functions from our custom scripts
from scripts import data_loader, feature_engineering, scoring, insights

def run_pipeline():
    """
    Executes the full data pipeline from loading to final insights.
    """
    print("--- Starting United Airlines Flight Difficulty Analysis Pipeline ---")

    # Module 1: Load and merge data from the 'data' folder
    master_df = data_loader.load_and_prepare_all_data(data_path='data')
    
    if master_df is not None:
        # Module 2: Engineer features to quantify difficulty
        featured_df = feature_engineering.create_features(master_df, airports_path='data/Airports Data.csv')

        # Module 3: Calculate the daily difficulty score (Solves the main challenge)
        scored_df = scoring.calculate_daily_score(featured_df)

        # Module 4: Analyze results for insights, print recommendations, and save the final output
        # The filename is set here as per the submission guidelines
        insights.generate_insights_and_recommendations(scored_df, output_dir='output', filename='test_TeamSamurai.csv')
    
    print("\n--- Pipeline finished successfully! ---")

# This block ensures the script runs only when this file is executed directly
if __name__ == "__main__":
    run_pipeline()