from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time


def test_submit_valid_blog_url():
    """Selenium E2E: open frontend, fill article URL and submit the form."""
    options = webdriver.ChromeOptions()
    # Use a modern headless flag; keep sandbox disabled for CI
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("http://127.0.0.1:8001")
        # Find the input by placeholder text used in the app
        input_el = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Enter article URL']")
        assert input_el is not None
        input_el.clear()
        input_el.send_keys("https://en.wikipedia.org/wiki/India")

        # Try to find a submit button and click it (graceful fallback)
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except Exception:
            # fallback to first button
            submit_btn = driver.find_element(By.TAG_NAME, 'button')

        submit_btn.click()

        # Small wait for any client-side handling
        time.sleep(1)

        # Validate input still contains the URL (basic verification)
        assert 'wikipedia.org' in input_el.get_attribute('value')

    finally:
        driver.quit()
