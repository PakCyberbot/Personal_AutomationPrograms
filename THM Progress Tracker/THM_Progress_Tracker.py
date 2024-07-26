from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import time
import os
import pickle
from datetime import datetime
import sys
def progress_logs(data_dict, user_name):
    """
    data_dict:
    {
    no_rooms_completed: int,
    rooms_dict: dict
    time_progress_taken: datetime.now()
    last_2_days_activity: list[yesterday, current]
    }
    """
    names_new_rooms_completed = set()
    if os.path.exists(f"profiles/{user_name}.pkl"):
        # Open the file in binary read mode
        with open(f'profiles/{user_name}.pkl', 'rb') as file:
            # Deserialize and read the list from the file
            load_progress_logs = pickle.load(file)

        rooms_completed_from_last_check = data_dict['no_rooms_completed'] - load_progress_logs[-1]['no_rooms_completed']
        
        if rooms_completed_from_last_check > 0:

            names_new_rooms_completed = set(data_dict['rooms_dict'].keys()) - set(load_progress_logs[-1]['rooms_dict'].keys())
            

            load_progress_logs.append(data_dict)
        else:
            names_new_rooms_completed = set(load_progress_logs[-1]['rooms_dict'].keys()) - set(load_progress_logs[-2]['rooms_dict'].keys())

    else:
        load_progress_logs = [data_dict]

    # Step 3: Open a file in binary write mode
    with open(f'profiles/{user_name}.pkl', 'wb') as file:
        # Step 4: Serialize and write the list to the file
        pickle.dump(load_progress_logs, file)

    return names_new_rooms_completed, load_progress_logs[-2]['time_progress_taken']


def list_all_the_completed_rooms(driver):
    css_selector = "#completed-rooms-more"
    while True:
        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            
            driver.execute_script("completedRoomsAdd()", button)

            time.sleep(1)
        
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException) as e:
            break

    
def scrape_completed_rooms(html_content):
    rooms_dict = {}
    soup = BeautifulSoup(html_content, 'html.parser')

    completed_rooms = soup.find(id='completed-rooms')
    links = completed_rooms.find_all('a')

    for link in links:
        href = link.get('href')

        title_div = link.find('div', class_='room-card-design-title')
        if title_div:
            
            title = title_div.get_text(strip=True)
            rooms_dict[title] = href

    return rooms_dict    

def calendar_activity_get(driver):
    # Calender Event Extraction

    # move to yearly activity tab
    # JavaScript to remove classes 'active' and 'show' from the element with id 'rooms-complete'
    remove_classes_script = """
    document.getElementById('rooms-complete').classList.remove('active', 'show');
    """

    # JavaScript to add classes 'active' and 'show' to the element with id 'yearly-activity'
    add_classes_script = """
    document.getElementById('yearly-activity').classList.add('active', 'show');
    getActivityEvents();
    """

    driver.execute_script(remove_classes_script)
    driver.execute_script(add_classes_script)

    svg_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'svg.js-calendar-graph-svg'))
    )

    # getting latest 2 days activity 
    day_elements = svg_element.find_elements(By.CLASS_NAME, 'day')

    curr_day_element = day_elements[-1]
    yesterday_element = day_elements[-2]


    # Get the 'data-count' attribute of the last 'rect' tag
    curr_day_activity = curr_day_element.get_attribute('data-count')
    yesterday_activity = yesterday_element.get_attribute('data-count')


    return [yesterday_activity, curr_day_activity]

def thm_user_progress_track(user_name):
    THM_profile_url = f'https://tryhackme.com/p/{user_name}'
    firefox_options = Options()
    firefox_options.add_argument("--headless")

    driver = webdriver.Firefox(options=firefox_options)

    driver.get(THM_profile_url)

    # Wait for the page to load completely
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#completed-rooms-more")))

    list_all_the_completed_rooms(driver)

    html_content=driver.page_source

    rooms_url_dict = scrape_completed_rooms(html_content)

    soup = BeautifulSoup(html_content, 'html.parser')

    no_rooms_completed = int(soup.find(id='rooms-completed').text)

    last_2_days_activity = calendar_activity_get(driver)

    data_dict ={"no_rooms_completed":no_rooms_completed,"rooms_dict":rooms_url_dict, "time_progress_taken":datetime.now() , "last_2_days_activity":last_2_days_activity}
    new_rooms_name, last_check_time = progress_logs(data_dict,"Qurratulain")

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"
    LIGHT_BLUE = "\033[94m"

    print("="*100)
    print(f"{RESET}{THM_profile_url}{RESET}".center(100))
    print(f"Total completed rooms: {YELLOW}{no_rooms_completed}{RESET}".center(100))
    print(f"Today's Activity: {GREEN}{last_2_days_activity[-1]}{RESET}".center(100))
    print(f"{RESET}Yesterday's Activity: {last_2_days_activity[-2]}{RESET}".center(100))
    print(f" ".center(100))
    print(f"Activity Checked at {LIGHT_BLUE}{data_dict['time_progress_taken']}{RESET}".center(100))

    if len(new_rooms_name) != 0:
        print(f" ".center(100))        
        print(f"Name of the {GREEN}{len(new_rooms_name)}{RESET} rooms that completed by the {user_name} after your last check at {last_check_time}".center(100))        
        print(f" ".center(100))        
        
        for room in new_rooms_name:
            print(f"{room} : https://tryhackme.com/r{data_dict['rooms_dict'][room]}".center(100))
    print("="*100)

    driver.quit()

if __name__ =="__main__":
    if len(sys.argv) > 1:
        profile_url = sys.argv[1]
        user_name = profile_url.split('/')[-1]
        thm_user_progress_track(user_name)
    else:
        with open("track_profile.txt","r") as f:
            profile_urls = f.readlines()
        for url in profile_urls:
            
            user_name = url.strip('\n').split('/')[-1]
            print("Checking progress of", user_name)
            thm_user_progress_track(user_name)
            
    

    