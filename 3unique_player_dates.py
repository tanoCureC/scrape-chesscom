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

# xPaths
last_online_xpath = '//div[@class="profile-card-info-item-value"]/div'
join_date_xpath = '//*[@id="view-profile"]/div[1]/div/div[1]/div[2]/div/div[2]/div[3]/div[2]/div'

# variables
unique_player_names = []
player_name_list = []
player_join_date_list = []
player_last_online_list = []
scraping_datetime = []
last_online_date_list_pdt = []

# Get text of the xpath
def get_element_text(element, xpath):
    try:
        elem = WebDriverWait(element, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return elem.text
    except TimeoutException:
        print(f"Timed out waiting for element with xpath {xpath} to load")
        return None

# Export to csv file
def export_to_csv():
    df = pd.DataFrame(
        {
            "Player name": player_name_list,
            "Joined": player_join_date_list,
            "Last Online": player_last_online_list,
            "Scraping DateTime NZST": scraping_datetime,
            "Last Online PDT": last_online_date_list_pdt,
        }
    )
    df.to_csv("unique_player_dates.csv", index=False)
    #print(df)

def calculate_last_online_datetime(last_online_date, scraping_time):
    # Convert scraping_time to a datetime object with timezone information (NZST GMT+13 hours)
    scraping_dt = datetime.strptime(scraping_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone(timedelta(hours=13)))
    
    # Convert scraping_time (NZST) to PDT (GMT-7 hours)
    scraping_dt_pdt = scraping_dt.astimezone(timezone(timedelta(hours=-7)))

    if last_online_date == 'Just now' or last_online_date == 'Online Now':
        last_online_datetime = scraping_dt_pdt
    elif ' ago' in last_online_date:
        num = int(re.search(r'\d+', last_online_date).group()) # first appearing consecutive numbers in the string
        if 'minute' in last_online_date:
            last_online_datetime = scraping_dt_pdt - timedelta(minutes=num)
        elif 'hour' in last_online_date:
            last_online_datetime = scraping_dt_pdt - timedelta(hours=num)
        elif 'day' in last_online_date:
            last_online_datetime = scraping_dt_pdt - timedelta(days=num)
    else:
        last_online_datetime = datetime.strptime(last_online_date, '%b %d, %Y').replace(tzinfo=timezone(timedelta(hours=-7)))

    return last_online_datetime

## MAIN PROCESS
# Import the CSV file of unique player names
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
    scraping_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    scraping_datetime.append(scraping_time)
    
    # calculate last_online_date to PDT
    last_online_date_pdt = calculate_last_online_datetime(last_online_date, scraping_time)
    last_online_date_list_pdt.append(last_online_date_pdt.strftime('%Y-%m-%d %H:%M:%S'))

    print(f"\n{name_count}")
    print(name)
    print(last_online_date)
    print(join_date)
    print(scraping_time)
    print(last_online_date_pdt)
    
    name_count += 1
    # in order to export to csv each time, need to match the length of name list with the lengths of last online date list and join date list
    player_name_list.append(name)
    # export to csv file each time so that work can be resumed from the point that the process crashes midway
    export_to_csv()
    sleep(5)

driver.quit()
print('end')