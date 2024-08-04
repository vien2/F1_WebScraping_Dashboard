from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException,StaleElementReferenceException
import csv
from utils import *
from bs4 import BeautifulSoup

def init_webdriver():
    try:
        chrome_service = Service(r'C:\ChromeDriver\chromedriverwin64\chromedriver.exe')
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")

        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error al crear el driver: {e}")
        return None

def aceptar_cookies(driver):
    try:
        iframe = driver.find_element(By.XPATH, '//iframe[@id="sp_message_iframe_1149950"]')
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
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                race_result.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'laps': None,
                    'time': None,
                    'points': None
                })
                return race_result
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 7:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    laps = cols[4].text
                    time_retired = cols[5].text
                    points = cols[6].text
                    
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
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return race_result

def get_race_urls(driver, year_url):
    driver.get(year_url)
    time.sleep(3)

    race_urls = []
    try:
        wait = WebDriverWait(driver, 10)
        # Espera explícita para cualquier li con data-name="races"
        race_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.f1-menu-item[data-name="races"]')))

        for race in race_elements:
            try:
                race_text = race.find_element(By.TAG_NAME, 'a').text.strip().lower()
                if 'all' not in race_text:
                    race_url = race.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    race_urls.append(race_url)
            except Exception as e:
                print(f"Error al procesar la carrera: {e}")

    except Exception as e:
        print(f"Error al extraer URLs de los circuitos: {e}")
    return race_urls

def get_year_urls(driver):
    base_url = "https://www.formula1.com/en/results.html"
    driver.get(base_url)
    time.sleep(3)
    aceptar_cookies(driver)
    year_urls = []

    try:
        # Espera explícita para el ul con la clase especificada
        wait = WebDriverWait(driver, 10)
        years_ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.f1-menu-wrapper.flex.flex-col.gap-micro.f1-filters-wrapper.max-h-\\[7\\.5em\\].max-laptop\\:bg-brand-offWhite.overflow-y-auto.p-normal.relative')))

        # Captura inicial de los elementos
        years = years_ul.find_elements(By.CSS_SELECTOR, 'li.f1-menu-item[data-name="year"]')

        for i in range(len(years)):
            retries = 0
            while retries < 3:  # Limitar a 3 reintentos
                try:
                    # Encuentra los elementos año nuevamente para evitar stale references
                    years_ul = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.f1-menu-wrapper.flex.flex-col.gap-micro.f1-filters-wrapper.max-h-\\[7\\.5em\\].max-laptop\\:bg-brand-offWhite.overflow-y-auto.p-normal.relative')))
                    years = years_ul.find_elements(By.CSS_SELECTOR, 'li.f1-menu-item[data-name="year"]')
                    year = years[i]
                    
                    # Captura data-value y href individualmente
                    data_value = year.get_attribute('data-value')
                    href = year.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    
                    if is_number(data_value):
                        year_value = int(data_value)
                        if 'races' in href and 1950 <= year_value <= 2023:
                            year_urls.append(href)
                    break  # Sal del bucle si se capturan correctamente
                except StaleElementReferenceException:
                    print(f"Stale element at index {i}, retrying {retries+1}/3")
                    retries += 1
                except Exception as e:
                    print(f"Error al capturar data-value y href: {e}")
                    break
        
    except Exception as e:
        print(f"Error al extraer URLs de los años: {e}")

    return year_urls

def get_section_urls(driver, race_url):
    driver.get(race_url)
    time.sleep(3)
    section_urls = {}
    try:
        wait = WebDriverWait(driver, 10)
        section_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.f1-menu-wrapper.flex.flex-col.gap-micro.f1-sidebar-wrapper li a')))
        for section in section_elements:
            section_name = section.text.strip().lower().replace(' ', '_')
            section_url = section.get_attribute('href')
            section_urls[section_name] = section_url
    except Exception as e:
        print(f"Error al extraer URLs de las secciones: {e}")
    return section_urls

def save_to_csv(data, filename, fieldnames):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Datos guardados en {filename}")
    except Exception as e:
        print(f"Error al guardar en CSV: {e}")

def main():
    driver = init_webdriver()
    if driver is None:
        return

    year_urls = get_year_urls(driver)

    sections = {
        'race_result': ['year','race','position', 'number', 'driver', 'car', 'laps', 'time', 'points'],
        #'fastest_laps': ['year','race','position', 'number', 'driver', 'car', 'lap', 'time_of_day', 'time', 'avg_speed'],
        #'pit_stop': ['year','race','stops', 'number', 'driver', 'car', 'lap', 'time_of_day', 'time', 'total'],
        #'starting_grid': ['year','race','position', 'number', 'driver', 'car', 'time'],
        #'qualifying': ['year','race','position', 'number', 'driver', 'car', 'q1', 'q2', 'q3', 'laps'],
        #'practice_3': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps'],
        #'practice_2': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps'],
        #'practice_1': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps']
    }

    all_data = {section: [] for section in sections}
    
    #with open('./data/raw/f1_race_results.csv', mode='w', newline='', encoding='utf-8') as file:
    #    writer = csv.writer(file)
    #    writer.writerow(['year', 'race', 'position', 'number', 'driver', 'car', 'laps', 'time', 'points'])

    for year_url in year_urls:
        year = year_url.split('/')[-2]
        print(f"Extrayendo datos del año {year}")
        
        race_urls = get_race_urls(driver, year_url)

        for race_url in race_urls:
            race_name = race_url.split('/')[-2].replace('-', ' ').title()
            print(f"Extrayendo datos de la carrera: {race_name} para el año: {year}")

            section_urls = get_section_urls(driver, race_url)

            for section_name, columns in sections.items():
                if section_name in section_urls:
                    #section_url = section_urls[section_name]
                    print(f"Extrayendo datos de la sección: {section_name} para la carrera: {race_name} del año {year}")
                    #aqui va la parte de cada seccion con un if
                    race_result = get_race_result(driver, year, race_name)
                    if race_result and all(key in race_result[0] for key in columns):
                        all_data[section_name].extend(race_result)
                        #save_to_csv(race_result, f'./data/raw/f1_{section_name}.csv', columns)
                    #save_to_csv(race_result, f'./data/raw/f1_{section_name}.csv', columns)
                else:
                    print(f"No existe la sección {section_name} para la carrera {race_name} del año {year}")

    for section_name, data in all_data.items():
        if data:
            save_to_csv(data, f'./data/raw/f1_{section_name}.csv', sections[section_name])
        #race_urls = get_race_urls(driver, year_url)
        
        #for race_url in race_urls:
        #    race_name = race_url.split('/')[-2].replace('-', ' ').title()
        #    print(f"Extrayendo datos de la carrera: {race_name} para el año: {year}")
            
        #    driver.get(race_url)
        #    time.sleep(3)
            
        #    race_result = get_race_result(driver, year, race_name)
        #    for result in race_result:
        #        writer.writerow([
        #            result['year'], result['race'], result['position'], result['number'],
        #           result['driver'], result['car'], result['laps'], result['time'], result['points']
        #        ])
    
    driver.quit()

if __name__ == '__main__':
    main()