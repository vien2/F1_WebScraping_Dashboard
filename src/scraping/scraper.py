from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException,StaleElementReferenceException
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
                if len(cols) >= 6:  # Asegurarse de que haya suficientes columnas
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

def get_fastest_laps(driver, year, race_name):
    fastest_laps = []
    try:
        wait = WebDriverWait(driver, 10)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                fastest_laps.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'lap': None,
                    'time_of_day': None,
                    'time': None,
                    'avg_speed': None
                })
                return fastest_laps
        
        # Espera explícita para la tabla con la clase especificada
        results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
        rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
        
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) == 7:
                # Caso con 7 columnas
                position = cols[0].text
                number = cols[1].text
                driver_name = cols[2].text
                car_html = cols[3].get_attribute("innerHTML")
                soup = BeautifulSoup(car_html, 'html.parser')
                car_name = soup.get_text().strip()
                lap = cols[4].text
                time = cols[5].text
                avg_speed = cols[6].text

                fastest_laps.append({
                    'year': year,
                    'race': race_name,
                    'position': position,
                    'number': number,
                    'driver': driver_name,
                    'car': car_name,
                    'lap': lap,
                    'time_of_day': None,
                    'time': time,
                    'avg_speed': avg_speed
                })
            elif len(cols) == 8:
                # Caso con 8 columnas
                position = cols[0].text
                number = cols[1].text
                driver_name = cols[2].text
                car_html = cols[3].get_attribute("innerHTML")
                soup = BeautifulSoup(car_html, 'html.parser')
                car_name = soup.get_text().strip()
                lap = cols[4].text
                time_of_day = cols[5].text
                time = cols[6].text
                avg_speed = cols[7].text

                fastest_laps.append({
                    'year': year,
                    'race': race_name,
                    'position': position,
                    'number': number,
                    'driver': driver_name,
                    'car': car_name,
                    'lap': lap,
                    'time_of_day': time_of_day,
                    'time': time,
                    'avg_speed': avg_speed
                })
            elif len(cols) == 6:
                # Caso con 6 columnas
                position = cols[0].text
                number = cols[1].text
                driver_name = cols[2].text
                car_html = cols[3].get_attribute("innerHTML")
                soup = BeautifulSoup(car_html, 'html.parser')
                car_name = soup.get_text().strip()
                lap = cols[4].text
                time = cols[5].text

                fastest_laps.append({
                    'year': year,
                    'race': race_name,
                    'position': position,
                    'number': number,
                    'driver': driver_name,
                    'car': car_name,
                    'lap': lap,
                    'time_of_day': None,
                    'time': time,
                    'avg_speed': None
                })
            else:
                print(f"Skipping row with unexpected columns count: {len(cols)} columns found")  # Debugging output

    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return fastest_laps

def get_pit_stop_summary(driver, year, race_name):
    pit_stop_summary = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                pit_stop_summary.append({
                    'year': year,
                    'race': race_name,
                    'stops': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'lap': None,
                    'time_of_day': None,
                    'time': None,
                    'total': None
                })
                return pit_stop_summary
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 7:  # Asegurarse de que haya suficientes columnas
                    stops = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    lap = cols[4].text
                    time_of_day = cols[5].text
                    time = cols[6].text
                    total = cols[7].text
                  
                    pit_stop_summary.append({
                        'year': year,
                        'race': race_name,
                        'stops': stops,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'lap': lap,
                        'time_of_day': time_of_day,
                        'time': time,
                        'total': total
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return pit_stop_summary

def get_starting_grid(driver, year, race_name):
    starting_grid = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                starting_grid.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None
                })
                return starting_grid
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 4:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text

                    starting_grid.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return starting_grid

def get_qualifying(driver, year, race_name):
    qualifying = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                qualifying.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'q1': None,
                    'q2': None,
                    'q3': None,
                    'laps': None
                })
                return qualifying
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) == 8:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    q1 = cols[4].text
                    q2 = cols[5].text
                    q3 = cols[6].text
                    laps = cols[7].text
                    
                    qualifying.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'q1': q1,
                        'q2': q2,
                        'q3': q3,
                        'time': None,
                        'laps': laps
                    })
                elif len(cols) == 5:
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    
                    qualifying.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'q1': q1,
                        'q2': q2,
                        'q3': q3,
                        'time': time,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return qualifying

def get_practice_3(driver, year, race_name):
    practice_3 = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                practice_3.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'gap': None,
                    'laps': None
                })
                return practice_3
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    gap = cols[5].text
                    laps = cols[6].text
                    
                    practice_3.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'gap': gap,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return practice_3

def get_practice_2(driver, year, race_name):
    practice_2 = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                practice_2.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'gap': None,
                    'laps': None
                })
                return practice_2
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    gap = cols[5].text
                    laps = cols[6].text
                    
                    practice_2.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'gap': gap,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return practice_2

def get_practice_1(driver, year, race_name):
    practice_1 = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                practice_1.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'gap': None,
                    'laps': None
                })
                return practice_1
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    gap = cols[5].text
                    laps = cols[6].text
                    
                    practice_1.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'gap': gap,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return practice_1

def get_warm_up(driver, year, race_name):
    warm_up = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                warm_up.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'gap': None,
                    'laps': None
                })
                return warm_up
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) == 7:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    gap = cols[5].text
                    laps = cols[6].text
                    
                    warm_up.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'gap': gap,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return warm_up

def get_overall_qualifying(driver, year, race_name):
    overall_qualifying = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                overall_qualifying.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'laps': None
                })
                return overall_qualifying
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) == 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    laps = cols[5].text
                    
                    overall_qualifying.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return overall_qualifying

def get_qualifying_2(driver, year, race_name):
    qualifying_2 = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                qualifying_2.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'laps': None
                })
                return qualifying_2
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) == 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    laps = cols[5].text
                    
                    qualifying_2.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return qualifying_2

def get_qualifying_1(driver, year, race_name):
    qualifying_1 = []
    try:
        wait = WebDriverWait(driver, 5)
        # Verificar si el mensaje de resultados no disponibles está presente
        no_results_messages = driver.find_elements(By.CSS_SELECTOR, 'p.f1-text.f1-text__body')
        for message in no_results_messages:
            if message.text.strip() == "Results for this session aren’t available yet.":
                qualifying_1.append({
                    'year': year,
                    'race': race_name,
                    'position': None,
                    'number': None,
                    'driver': None,
                    'car': None,
                    'time': None,
                    'laps': None
                })
                return qualifying_1
        else:
            # Espera explícita para la tabla con la clase especificada
            results_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.f1-table.f1-table-with-data.w-full')))
            
            rows = results_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Saltar la cabecera
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) == 6:  # Asegurarse de que haya suficientes columnas
                    position = cols[0].text
                    number = cols[1].text
                    driver_name = cols[2].text
                    car_html = cols[3].get_attribute("innerHTML")
                    soup = BeautifulSoup(car_html, 'html.parser')
                    car_name = soup.get_text().strip()
                    time = cols[4].text
                    laps = cols[5].text
                    
                    qualifying_1.append({
                        'year': year,
                        'race': race_name,
                        'position': position,
                        'number': number,
                        'driver': driver_name,
                        'car': car_name,
                        'time': time,
                        'laps': laps
                    })
    except Exception as e:
        print(f"Error al extraer resultados de la carrera {race_name}: {e}")
    return qualifying_1

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

def main():
    driver = init_webdriver()
    if driver is None:
        return

    year_urls = get_year_urls(driver)

    sections = {
        #'race_result': ['year','race','position', 'number', 'driver', 'car', 'laps', 'time', 'points'],
        #'fastest_laps': ['year','race','position', 'number', 'driver', 'car', 'lap', 'time_of_day', 'time', 'avg_speed'],
        'pit_stop_summary': ['year','race','stops', 'number', 'driver', 'car', 'lap', 'time_of_day', 'time', 'total'],
        #'starting_grid': ['year','race','position', 'number', 'driver', 'car', 'time'],
        #'qualifying': ['year','race','position', 'number', 'driver', 'car', 'q1', 'q2', 'q3', 'laps'],
        #'practice_3': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps'],
        #'practice_2': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps'],
        #'practice_1': ['year','race','position', 'number', 'driver', 'car', 'time', 'gap', 'laps'],
        'warm_up': ['year','race','position', 'number', 'driver', 'car', 'time', 'laps'],
        'overall_qualifying': ['year','race','position', 'number', 'driver', 'car', 'time', 'laps'],
        'qualifying_2': ['year','race','position', 'number', 'driver', 'car', 'time','laps'],
        'qualifying_1': ['year','race','position', 'number', 'driver', 'car','time', 'laps']
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
                    section_url = section_urls[section_name]
                    driver.get(section_url)
                    time.sleep(3)
                    print(f"Extrayendo datos de la sección: {section_name} para la carrera: {race_name} del año {year}")
                    
                    if section_name == 'race_result':
                        race_result = get_race_result(driver, year, race_name)
                        if race_result and all(key in race_result[0] for key in columns):
                            all_data[section_name].extend(race_result)

                    elif section_name == 'fastest_laps':
                        fastest_laps = get_fastest_laps(driver, year, race_name)
                        if fastest_laps and all(key in fastest_laps[0] for key in columns):
                            all_data[section_name].extend(fastest_laps)

                    elif section_name == 'pit_stop_summary':
                        pit_stop_summary = get_pit_stop_summary(driver, year, race_name)
                        if pit_stop_summary and all(key in pit_stop_summary[0] for key in columns):
                            all_data[section_name].extend(pit_stop_summary)

                    elif section_name == 'starting_grid':
                        starting_grid = get_starting_grid(driver, year, race_name)
                        if starting_grid and all(key in starting_grid[0] for key in columns):
                            all_data[section_name].extend(starting_grid)

                    elif section_name == 'qualifying':
                        qualifying = get_qualifying(driver, year, race_name)
                        if qualifying and all(key in qualifying[0] for key in columns):
                            all_data[section_name].extend(qualifying)

                    elif section_name == 'practice_3':
                        practice_3 = get_practice_3(driver, year, race_name)
                        if practice_3 and all(key in practice_3[0] for key in columns):
                            all_data[section_name].extend(practice_3)

                    elif section_name == 'practice_2':
                        practice_2 = get_practice_2(driver, year, race_name)
                        if practice_2 and all(key in practice_2[0] for key in columns):
                            all_data[section_name].extend(practice_2)
                    
                    elif section_name == 'practice_1':
                        practice_1 = get_practice_1(driver, year, race_name)
                        if practice_1 and all(key in practice_1[0] for key in columns):
                            all_data[section_name].extend(practice_1)

                    elif section_name == 'warm_up':
                        warm_up = get_warm_up(driver, year, race_name)
                        if warm_up and all(key in warm_up[0] for key in columns):
                            all_data[section_name].extend(warm_up)

                    elif section_name == 'overall_qualifying':
                        overall_qualifying = get_overall_qualifying(driver, year, race_name)
                        if overall_qualifying and all(key in overall_qualifying[0] for key in columns):
                            all_data[section_name].extend(overall_qualifying)

                    elif section_name == 'qualifying_2':
                        qualifying_2 = get_qualifying_2(driver, year, race_name)
                        if qualifying_2 and all(key in qualifying_2[0] for key in columns):
                            all_data[section_name].extend(qualifying_2)

                    elif section_name == 'qualifying_1':
                        qualifying_1 = get_qualifying_1(driver, year, race_name)
                        if qualifying_1 and all(key in qualifying_1[0] for key in columns):
                            all_data[section_name].extend(qualifying_1)
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