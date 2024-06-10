from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
from utils import *

def init_webdriver():
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    except Exception as e:
        print(f"Error al crear el diver: {e}")
    return driver

def aceptar_cookies(driver):
    try:
        iframe = driver.find_element(By.XPATH, '//iframe[@id="sp_message_iframe_1122886"]')
        driver.switch_to.frame(iframe)
        try:
            wait = WebDriverWait(driver, 20)
            cookies_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="ACEPTAR TODO"]')))
            cookies_button.click()
        except Exception as e:
            print(f"Error al intentar aceptar las cookies: {e}")
    except Exception as e:
        print(f"Error al intentar cambiar al iframe: {e}")
    finally:
        driver.switch_to.default_content()
    return driver

def get_race_result(driver, year, race_name):
    race_result = []
    try:
        results_table = driver.find_element(By.CLASS_NAME, 'resultsarchive-table')
        rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) >= 7:  # Asegurarse de que haya suficientes columnas
                position = cols[1].text
                number = cols[2].text
                driver_name = cols[3].text
                car_name = cols[4].get_attribute('innerText').strip()  # Acceder al texto del elemento
                laps = cols[5].text
                time_retired = cols[6].text
                points = cols[7].text
                
                race_result.append({
                    'year': year,
                    'race': race_name,
                    'position': position,
                    'number': number,
                    'driver': driver_name,
                    'car': car_name,
                    'laps': laps,
                    'time': time_retired,
                    'points': points
                })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera: {e}")
    return race_result

def get_race_urls(driver, year_url):
    driver.get(year_url)
    time.sleep(3)
    
    # Obtener URLs de los circuitos, excluyendo "ALL"
    race_urls = []
    try:
        races = driver.find_elements(By.CSS_SELECTOR, '.resultsarchive-filter-item-link.FilterTrigger')
        for race in races:
            race_text = race.find_element(By.TAG_NAME, 'span').text.strip().lower()
            if 'meetingKey' in race.get_attribute('data-name') and 'all' not in race_text:
                race_urls.append(race.get_attribute('href'))
    except Exception as e:
        print(f"Error al extraer URLs de los circuitos: {e}")
    return race_urls

def get_year_urls(driver):
    base_url = "https://www.formula1.com/en/results.html"
    driver.get(base_url)
    time.sleep(3)
    year_urls = []
    try:
        years = driver.find_elements(By.CSS_SELECTOR, '.resultsarchive-filter-item-link.FilterTrigger')
        for year in years:
            data_value = year.get_attribute('data-value')
            if is_number(data_value):
                year_value = int(data_value)
                if 'races.html' in year.get_attribute('href') and 1950 <= year_value <= 2023:
                    year_urls.append(year.get_attribute('href'))
    except Exception as e:
        print(f"Error al extraer URLs de los años: {e}")
    return year_urls

def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    all_data = {}
    
    year_urls = get_year_urls(driver)
    
    for year_url in year_urls:
        year = year_url.split('/')[-2]
        print(f"Extrayendo datos del año {year}")
        
        race_urls = get_race_urls(driver, year_url)
        race_data = {}
        
        for race_url in race_urls:
            race_name = race_url.split('/')[-2].replace('-', ' ').title()
            print(f"Extrayendo datos de la carrera: {race_name}")
            
            driver.get(race_url)
            time.sleep(3)
            
            race_result = get_race_result(driver, year, race_name)
            print(race_result)
            race_data[race_name] = {
                'race_result': race_result
            }
        
        all_data[year] = race_data
    
    driver.quit()
    
    with open('f1_race_results.json', 'w') as f:
        json.dump(all_data, f, indent=4)

if __name__ == '__main__':
    main()
