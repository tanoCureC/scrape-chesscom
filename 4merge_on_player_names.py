import pandas as pd

# Import the CSV files into pandas dataframes
blitz_leaderboard = pd.read_csv('blitz_leaderboard.csv')
bullet_leaderboard = pd.read_csv('bullet_leaderboard.csv')
rapid_leaderboard = pd.read_csv('rapid_leaderboard.csv')
daily960_leaderboard = pd.read_csv('960daily_leaderboard.csv')
live960_leaderboard = pd.read_csv('960live_leaderboard.csv')
daily_leaderboard = pd.read_csv('daily_leaderboard.csv')

unique_player_dates = pd.read_csv('unique_player_dates.csv')

# Merge the two dataframes on the 'Player name' column
blitz_leaderboard_dates = pd.merge(blitz_leaderboard, unique_player_dates, on='Player name')
bullet_leaderboard_dates = pd.merge(bullet_leaderboard, unique_player_dates, on='Player name')
rapid_leaderboard_dates = pd.merge(rapid_leaderboard, unique_player_dates, on='Player name')
daily960_leaderboard_dates = pd.merge(daily960_leaderboard, unique_player_dates, on='Player name')
live960_leaderboard_dates = pd.merge(live960_leaderboard, unique_player_dates, on='Player name')
daily_leaderboard_dates = pd.merge(daily_leaderboard, unique_player_dates, on='Player name')

# Save the merged dataframe as a new CSV file
blitz_leaderboard_dates.to_csv('blitz_leaderboard_dates.csv', index=False)
bullet_leaderboard_dates.to_csv('bullet_leaderboard_dates.csv', index=False)
rapid_leaderboard_dates.to_csv('rapid_leaderboard_dates.csv', index=False)
daily960_leaderboard_dates.to_csv('960daily_leaderboard_dates.csv', index=False)
live960_leaderboard_dates.to_csv('960live_leaderboard_dates.csv', index=False)
daily_leaderboard_dates.to_csv('daily_leaderboard_dates.csv', index=False)

print("The merged CSV files have been created.")
