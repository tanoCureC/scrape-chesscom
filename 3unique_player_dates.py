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
from datetime import datetime, timedelta
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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
player_last_online_list = []
player_join_date_list = []

# Get text of the xpath
def get_element_text(element, xpath):
    try:
        elem = WebDriverWait(element, 20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return elem.text
    except TimeoutException:
        print(f"Timed out waiting for element with xpath {xpath} to load")
        return None

# Export to csv file
def export_to_csv():
    df = pd.DataFrame(
        {
            "Player name": player_name_list,
            "Last Online": player_last_online_list,
            "Joined": player_join_date_list,
        }
    )
    df.to_csv("unique_player_dates.csv", index=False)
    #print(df)

# Import the CSV file of unique player names
unique_players = pd.read_csv('unique_player_names.csv')
unique_player_names = unique_players['Player name']

# Get Join date and Last online date from profile page of each player
name_count = 1
for name in unique_player_names:
    # in order to export to csv each time, need to match the length of name list with the lengths of last online date list and join date list
    player_name_list.append(name)
    
    # get driver object of profile page
    profile_url = "https://www.chess.com/members/" + name
    driver.get(profile_url)

    # get last online date
    last_online_date = get_element_text(driver, last_online_xpath)
    player_last_online_list.append(last_online_date)
    print(f"\n{name_count}")
    print(name)
    print(last_online_date)

    # get join date
    join_date = get_element_text(driver, join_date_xpath)
    player_join_date_list.append(join_date)
    print(join_date)

    name_count += 1
    export_to_csv()
    sleep(5)

driver.quit()
print('end')