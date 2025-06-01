import streamlit as st
from streamlit_js_eval import streamlit_js_eval


st.set_page_config(page_title="Web Scraper", page_icon="💬")
st.title("**Product Review Scrapper**")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd
import requests


if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def complete_setup():
    st.session_state.setup_complete = True

if not st.session_state.setup_complete:
   if "url" not in st.session_state:
        st.session_state["url"] = ""
   if "output_file_name" not in st.session_state:
        st.session_state["output_file_name"] = ""

   st.session_state["url"] = st.text_input(label="Product URL", value=st.session_state["url"], placeholder="Paste product url", max_chars=100)
   st.session_state["output_file_name"] = st.text_input(label="Output File Name (.csv)", value=st.session_state["output_file_name"], placeholder="Write output file name", max_chars=100)
   if st.button("Start Scrapping", on_click=complete_setup):
        st.write("Setup complete. Starting scrapping reviews...")

if st.session_state.setup_complete and not st.session_state.chat_complete:
    
    #options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    #options.add_argument('--disable-gpu')
    #driver = webdriver.Chrome(options=options)
    #chrome_options = uc.Chrome(headless=True,use_subprocess=True,
    #version_main=137,  # Match Chrome 137 on Streamlit Cloud                         )
    
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.binary_location = "/usr/bin/chromium-browser"

    #chrome_options.binary_location = "/usr/bin/google-chrome"
    #service = Service("/usr/bin/chromedriver")
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
    #                             options=options)
    #driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = uc.Chrome(
                headless=True,
                use_subprocess=True,
                version_main=137  # Matches Chrome on Streamlit Cloud
            )
    #driver.get("https://www.amazon.in/Apple-iPhone-15-128-GB/dp/B0CHX2F5QT")
    driver.get(st.session_state["url"])
    #driver=requests.get(st.session_state["url"])
    """
    driver = None
    try:
        # Using on Local
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1200')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=options)
        #st.write(f"DEBUG:DRIVER:{driver}")
        driver.get(st.session_state["url"])
        #res = requests.get("https://example.com")
        time.sleep(5)
        #html_doc = driver.page_source
        #driver.quit()
        #soup = BeautifulSoup(html_doc, "html.parser")
        #return soup.get_text()
    except Exception as e:
        st.write(f"DEBUG:INIT_DRIVER:ERROR:{e}")
    finally:
        if driver is not None: driver.quit()"""

    time.sleep(70)

    reviews_data = []

    for page in range(1, 20):  # change this for more pages
      print(f"Scraping Page: {page}")
      #WebDriverWait(driver, 15).until(
      #EC.presence_of_element_located((By.XPATH, '//div[@data-hook="review"]'))
      #)
      soup = BeautifulSoup(driver.page_source, 'html.parser')
      #soup = BeautifulSoup(driver.text, 'html.parser')
      reviews = soup.find_all("div", {"id": "cm_cr-review_list"})
      #reviews=soup.find_all("div",{"class":"a-section a-spacing-none reviews-content a-size-       base"})
      #print(reviews)

      for review in reviews:
        #title = review.find("a", {"data-hook": "review-title"})
        #rating = review.find("i", {"data-hook": "review-star-rating"})
        #body = review.find("span", {"data-hook": "review-body"})
        #date = review.find("span", {"data-hook": "review-date"})
        #author = review.find("span", {"class": "a-profile-name"})

        title = review.find_all("a", {"data-hook": "review-title"})
        #for i in title:
             #title2=i.find_all('span')[-1].get_text(strip=True)
            # print('A:',title2)
        rating = review.find_all("i", {"data-hook": "review-star-rating"})
        body = review.find_all("span", {"data-hook": "review-body"})
        date = review.find_all("span", {"data-hook": "review-date"})
        author = review.find_all("span", {"class": "a-profile-name"})

        for i in range(len(title)):
            title2=title[i].find_all('span')[-1].get_text(strip=True)
            rating2=rating[i].find_all('span')[-1].get_text(strip=True)
            body2=body[i].find_all('span')[-1].get_text(strip=True)
            date2=date[i].get_text(strip=True)
            author2=author[i].get_text(strip=True)

            reviews_data.append({
             "title": title2.strip() if title else "",
             "rating": rating2.strip() if rating else "",
             "review": body2.strip() if body else "",
             "date": date2.strip() if date else "",
             "author": author2.strip() if author else ""
        })

      try:
        next_button = driver.find_element(By.XPATH, '//li[@class="a-last"]/a')
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(2)
      except NoSuchElementException:
        print("No more pages.")
        break

    driver.quit()

    # Save results
    df = pd.DataFrame(reviews_data)
    df.to_csv(st.session_state["output_file_name"], index=False)
    #print("Saved to airpods_reviews.csv")
    st.session_state.chat_complete = True

if st.session_state.chat_complete:
  st.write("Scraping Complete")
  df.to_csv(output_file, index=False)

  st.success(f"Scraping complete. File saved as {output_file}")
  st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False),
    file_name=output_file,
    mime="text/csv"
)
  if st.button("Restart Scraping", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
