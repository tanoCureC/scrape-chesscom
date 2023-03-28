import subprocess
from time import sleep

scripts_to_run = [
    '1leaderboard.py', # scrape data on each leaderboard 
    '2unique_player_names.py', # Produce the list of unique player names
    '3unique_player_dates.py', # Scrape Last Online dates and Joined dates of each player
    '4merge_on_player_names.py' # Merge the data of Last Online and Joined dates with the data of each leaderboard
]

for script in scripts_to_run:
    print(f"\nRunning {script}...")
    subprocess.run(['python', script])
    sleep(1) # no special meaning
    print(f"\n{script} finished.")
    sleep(1) # no special meaning
    
print("\nAll scripts have been executed.")
