from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchElementException as NSEE,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from datetime import datetime, timedelta, timezone
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import pytz

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")  # linux only
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36")

service = Service(executable_path=ChromeDriverManager().install())  # linux only
driver = webdriver.Chrome(service=service, options=chrome_options)  # linux only
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) # Windows only

driver.set_window_position(0, 0)
driver.set_window_size(1440, 900)
ignored_exceptions = (NSEE, StaleElementReferenceException)

last_online_xpath = '//div[@class="profile-card-info-item-value"]/div'
join_date_xpath = '//*[@id="view-profile"]/div[1]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]/div'

unique_player_names = []
player_name_list = []
player_join_date_list = []
player_last_online_list = []
scraping_time_list = []
last_online_date_chesscom_list = []

scraping_timezone = pytz.timezone('Pacific/Auckland') # timezone of your scraping
chesscom_timezone = pytz.timezone('America/Los_Angeles') # timezone of chess.com server

# Get text of the xpath
def get_element_text(element, xpath):
    try:
        elem = WebDriverWait(element, 20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return elem.text
    except TimeoutException:
        print(f"Timed out waiting for element with xpath {xpath} to load")
        return None

# calculate and convert Last Online date/time in chess.com timezone
def calculate_last_online_datetime(last_online_date, scraping_time):
    # Convert scraping_time (string) to a datetime object with timezone information
    scraping_dt = scraping_timezone.localize(datetime.strptime(scraping_time, '%Y-%m-%d %H:%M:%S'))
    
    # Convert datetime object of scraping_time to datetime object of chess.com server time
    scraping_dt_chess_com_server = scraping_dt.astimezone(chesscom_timezone)

    # Set a default value for last_online_datetime in case the following if and elif conditions are not met.
    last_online_datetime = scraping_dt_chess_com_server
    
    if last_online_date == 'Just now' or last_online_date == 'Online Now':
        last_online_datetime = scraping_dt_chess_com_server
    elif ' ago' in last_online_date:
        num = int(re.search(r'\d+', last_online_date).group()) # first appearing consecutive numbers in the string
        if 'min' in last_online_date:
            last_online_datetime = scraping_dt_chess_com_server - timedelta(minutes=num)
        elif 'hour' in last_online_date or 'hr' in last_online_date:
            last_online_datetime = scraping_dt_chess_com_server - timedelta(hours=num)
        elif 'day' in last_online_date:
            last_online_datetime = scraping_dt_chess_com_server - timedelta(days=num)
    else:
        last_online_datetime = chesscom_timezone.localize(datetime.strptime(last_online_date, '%b %d, %Y'))

    return last_online_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Export to csv file
def export_to_csv():
    df = pd.DataFrame(
        {
            "Player name": player_name_list,
            "Joined": player_join_date_list,
            "Last Online": player_last_online_list,
            "Scraping time": scraping_time_list,
            "Last Online chess.com server time": last_online_date_chesscom_list,
        }
    )
    df.to_csv("unique_player_dates.csv", index=False)
    #print(df)

## MAIN PROCESS
# Import csv file of unique player names
unique_players = pd.read_csv('unique_player_names.csv')
unique_player_names = unique_players['Player name']

# Get Join date and Last online date from profile page of each player
name_count = 1
for name in unique_player_names:
    # get driver object of profile page
    profile_url = "https://www.chess.com/members/" + name
    driver.get(profile_url)

    # get last online date
    last_online_date = get_element_text(driver, last_online_xpath)
    if last_online_date == None:
        continue
    
    # get join date
    join_date = get_element_text(driver, join_date_xpath)
    if join_date == None:
        continue
    
    player_last_online_list.append(last_online_date)
    player_join_date_list.append(join_date)
    
    # get scraping time
    scraping_time = datetime.now(scraping_timezone).strftime('%Y-%m-%d %H:%M:%S') 
    scraping_time_list.append(scraping_time)
    
    # calculate last_online_date to chess.com server time
    last_online_date_chesscom = calculate_last_online_datetime(last_online_date, scraping_time)
    last_online_date_chesscom_list.append(last_online_date_chesscom)

    print(f"\n{name_count}")
    print(name)
    print(join_date)
    print(last_online_date)    
    print(scraping_time)
    print(last_online_date_chesscom)
    
    name_count += 1
    # in order to export to csv each time, need to match the length of name list with the lengths of last online date list and join date list
    player_name_list.append(name)
    # export to csv file every 100 players so that work can be resumed from the nearest point that the process crashes midway
    if name_count % 100 == 0:
        export_to_csv()
    sleep(5)

driver.quit()
export_to_csv()