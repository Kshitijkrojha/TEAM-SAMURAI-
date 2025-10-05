# scripts/scoring.py (UPDATED VERSION)
import pandas as pd
import os

def calculate_daily_score(df):
    """
    Solves the main challenge: calculates a daily difficulty score for each flight
    and includes the individual component ranks for detailed analysis.
    """
    print("Step 3: Calculating daily flight difficulty score...")
    
    difficulty_features = {
        'load_factor': True, 'ssr_per_pax': True, 'child_ratio': True, 'basic_economy_ratio': True,
        'bags_per_pax': True, 'is_international': True, 'ground_time_deficit': False,
        'fleet_complexity_score': True, 'time_pressure_score': True, 'is_high_risk_transfer': True
    }
    score_ranks = []
    for feature, higher_is_worse in difficulty_features.items():
        rank_col = f'{feature}_rank'
        df[rank_col] = df.groupby('scheduled_departure_date_local')[feature].rank(pct=True)
        if not higher_is_worse: df[rank_col] = 1 - df[rank_col]
        score_ranks.append(rank_col)

    df['difficulty_score'] = df[score_ranks].mean(axis=1) * 100
    df['difficulty_rank_daily'] = df.groupby('scheduled_departure_date_local')['difficulty_score'].rank(method='dense', ascending=False)
    df['difficulty_class'] = df.groupby('scheduled_departure_date_local')['difficulty_score'].transform(
        lambda x: pd.qcut(x, q=[0, 0.33, 0.66, 1.0], labels=['Easy', 'Medium', 'Difficult'], duplicates='drop')
    )

    print("Daily scoring and classification complete.")
    # The dataframe returned now includes all the important '_rank' columns
    return df