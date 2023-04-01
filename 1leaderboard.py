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

ignored_exceptions = (NSEE, StaleElementReferenceException)

banner_close_xpath = '//button[@class="ready-to-play-banner-close"]'
player_data_xpath = '//tr[@class="leaderboard-row-show-on-hover"]'
player_name_xpath = './td[@class="leaderboard-row-user-cell"]/a/div/a[@data-test-element="user-tagline-username"]'
rating_xpath = './td[@class="table-text-right leaderboard-row-score"]/a'
stats_xpath = './td[@class="leaderboard-row-rating table-text-right"]/a/span[@class="leaderboard-row-regular-stats leaderboard-row-stats"]'
next_page_button_xpath = '//button[@aria-label="Next Page"]'

leaderboards = [
    ("blitz", "https://www.chess.com/leaderboard/live?country=JP&page=1"),
    ("bullet", "https://www.chess.com/leaderboard/live/bullet?country=JP&page=1"),
    ("rapid", "https://www.chess.com/leaderboard/live/rapid?country=JP&page=1"),
    ("960live", "https://www.chess.com/leaderboard/live/blitz/chess960?country=JP&page=1"),
    ("960daily", "https://www.chess.com/leaderboard/daily/chess960?country=JP&page=1"),
    ("daily", "https://www.chess.com/leaderboard/daily?country=JP&page=1"),
]

player_name_list = []
player_rating_list = []
player_win_list = []
player_draw_list = []
player_loss_list = []

# Get text of the xpath
def get_element_text(element, xpath):
    try:
        elem = WebDriverWait(element, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return elem.text
    except TimeoutException:
        print(f"Timed out waiting for element with xpath {xpath} to load")
        return None

# Get player list on the current page
def get_player_data_from_page():
    retry = True
    max_retries = 5
    attempts = 0
    player_data = None
    while retry and attempts < max_retries:
        try:
            player_data = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_all_elements_located((By.XPATH, player_data_xpath)))
            retry = False
        except TimeoutException:
            print("Timed out waiting for player data to load")
            driver.refresh()
            attempts += 1

    if attempts == max_retries:
        print("Reached maximum retries. Exiting.")
        
    return player_data

# Get data of each player on the current page
def process_player_data(player_data, current_page, leaderboard_type):
    for player in player_data:
        # get player name
        name = get_element_text(player, player_name_xpath)
        player_name_list.append(name)
        if player is not None:
            print(f"\n{leaderboard_type} page {current_page}")
            print(name)
        else:
            continue

        # get rating
        rating = get_element_text(player, rating_xpath)
        player_rating_list.append(rating)
        print(rating)

        # get win/draw/loss
        stats = get_element_text(player, stats_xpath)
        stats = "".join(stats.split()) # remove unnecessary spaces
        stats_list_formatted = stats.split("/")
        if len(stats_list_formatted) != 3:
            print(f"Skipping player {name} because of invalid stats = {stats}")
            player_win_list.append(None)
            player_draw_list.append(None)
            player_loss_list.append(None)
            continue
        player_win_list.append(stats_list_formatted[0])
        player_draw_list.append(stats_list_formatted[1])
        player_loss_list.append(stats_list_formatted[2])
        print(f"{stats_list_formatted[0]}/{stats_list_formatted[1]}/{stats_list_formatted[2]}")

# Check if there is a next page
def check_next_page(current_page):
    ### for testing purpose only
    #if current_page == 2:
    #    print("test end")
    #    return False
    ############################
    try:
        next_page = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, next_page_button_xpath)))
        if next_page.is_enabled():
            return True
        else:
            print("end")
            return False
    except (NSEE, WebDriverException):
        print("\nfail to click on next page due to error\n")
        try:
            # close ready to play banner
            ready_close = driver.find_element(By.XPATH, banner_close_xpath)
            ready_close.click()
        except NSEE:
            pass
        return False

# Move to next page
def click_next_page(current_page):
    sleep(5)
    try:
        next_page = WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, next_page_button_xpath)))
        next_page.click()
        current_page += 1
    except (NSEE, WebDriverException):
        print("\nfail to click on next page due to error\n")
        try:
            # close ready to play banner
            ready_close = driver.find_element(By.XPATH, banner_close_xpath)
            ready_close.click()
        except NSEE:
            pass
    return current_page

# Export to csv file
def export_to_csv(leaderboard_type):
    filename = f"{leaderboard_type}_leaderboard.csv"
    df = pd.DataFrame(
        {
            "Player name": player_name_list,
            "Rating": player_rating_list,
            "Won": player_win_list,
            "Draw": player_draw_list,
            "Lost": player_loss_list,
        }
    )
    df.to_csv(filename, index=False)
    print(df)

# MAIN PROCESS
def scrape_leaderboard(leaderboard_type, website_url):
    current_page = 1
    
    driver.get(website_url)
    driver.set_window_position(0, 0)
    driver.set_window_size(1440, 900)
    ignored_exceptions = (NSEE, StaleElementReferenceException)
    
    #close ready-to-play-banner (preparation before starting main process)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, banner_close_xpath))
        WebDriverWait(driver, 10).until(element_present)
        ready_close = driver.find_element(By.XPATH, banner_close_xpath)
        ready_close.click()
    except TimeoutException:
        pass
    
    # main process
    continue_scraping = True
    while continue_scraping:
        # Get player list from the current page
        player_data = get_player_data_from_page()

        # Get data of each player on the current page
        process_player_data(player_data, current_page, leaderboard_type)

        # Check if there is a next page
        continue_scraping = check_next_page(current_page)

        # Move to next page
        current_page = click_next_page(current_page)

    export_to_csv(leaderboard_type)
    
# Transition from Blitz -> Bullet -> ...Leaderboard : Run the MAIN PROCESS, scrape_leaderboard(), in each Leaderboard
for leaderboard_type, website_url in leaderboards:
    # reset lists before moving to the next leaderboard
    player_name_list.clear()
    player_rating_list.clear()
    player_win_list.clear()
    player_draw_list.clear()
    player_loss_list.clear()
    
    scrape_leaderboard(leaderboard_type, website_url)

driver.quit()