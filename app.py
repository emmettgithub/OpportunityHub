from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# ---------------- Selenium Scraper ----------------
def scrape_fluke_portal(email, password):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    df = None

    try:
        driver.get("https://partnerportal.fluke.com/en/user/login")
        driver.find_element(By.NAME, "name").send_keys(email)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.NAME, "op").click()
        time.sleep(5)

        # Navigate to Opportunities
        opp_menu = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Opportunities"))
        )
        opp_menu.click()
        time.sleep(2)

        rep_opp_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Representative Opportunities"))
        )
        rep_opp_item.click()
        time.sleep(5)

        # Sort by Created On descending
        try:
            created_on_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Created On')]"))
            )
            created_on_item.click()  # ascending
            time.sleep(2)
            created_on_item.click()  # descending
            time.sleep(5)
        except TimeoutException:
            print("Created On column not found or not clickable.")

        # Scrape table
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        table_body = table.find_element(By.TAG_NAME, "tbody")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue
            first_col_text = cells[0].text.strip()
            try:
                created_date = datetime.strptime(first_col_text, "%m/%d/%Y").date()
            except ValueError:
                continue
            if created_date >= datetime.now().date() - timedelta(days=14):
                row_data = [cell.text.strip() for cell in cells]
                data.append(row_data)

        df = pd.DataFrame(data, columns=headers if headers else None)

    except Exception as e:
        print(f"Error during automation: {e}")
    finally:
        driver.quit()

    return df

# ---------------- Flask Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            df = scrape_fluke_portal(email, password)
            if df is not None and not df.empty:
                table_html = df.to_html(classes="table table-striped", index=False)
                return render_template("result.html", table_html=table_html)
            else:
                return render_template("index.html", warning="No data found for the last 14 days.")
        else:
            return render_template("index.html", warning="Please enter email and password.")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
