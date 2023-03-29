import pandas as pd

## Create the list of unique player names
# Import the CSV files into pandas dataframes
blitz_leaderboard = pd.read_csv('blitz_leaderboard.csv')
bullet_leaderboard = pd.read_csv('bullet_leaderboard.csv')
rapid_leaderboard = pd.read_csv('rapid_leaderboard.csv')
daily960_leaderboard = pd.read_csv('960daily_leaderboard.csv')
live960_leaderboard = pd.read_csv('960live_leaderboard.csv')
daily_leaderboard = pd.read_csv('daily_leaderboard.csv')

# Extract the 'Player name' columns from the dataframes
blitz_names = blitz_leaderboard['Player name']
bullet_names = bullet_leaderboard['Player name']
rapid_names = rapid_leaderboard['Player name']
daily960_names = daily960_leaderboard['Player name']
live960_names = live960_leaderboard['Player name']
daily_names = daily_leaderboard['Player name']

# Combine the three lists of player names using pandas.concat
combined_names = pd.concat([blitz_names, bullet_names, rapid_names, daily960_names, live960_names, daily_names])

# Create a list of unique player names
unique_player_names = combined_names.drop_duplicates().tolist()

# Count the number of unique players
unique_player_count = len(unique_player_names)

# Print the list of unique player names and their count
#print("Unique player names:", unique_player_names)
print("Number of unique players:", unique_player_count)

# Convert the list of unique player names to a pandas DataFrame
unique_player_names_df = pd.DataFrame(unique_player_names, columns=['Player name'])

# Write the DataFrame to a CSV file
unique_player_names_df.to_csv('unique_player_names.csv', index=False)