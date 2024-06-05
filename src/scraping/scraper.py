from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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

def main():
    url_base = 'https://www.formula1.com/'
    driver = init_webdriver()

    try:
        driver.get(url_base)
        driver = aceptar_cookies(driver)

    except Exception as e:
        print(e)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
