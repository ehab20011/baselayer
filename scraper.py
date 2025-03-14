from playwright.sync_api import sync_playwright
from pathlib import Path
import os

#CONSTS
BASE_URL = "https://data.sba.gov/organization/"
DOWNLOAD_DIR = str(Path.home()/"Downloads")
CUSTOM_FILE_NAME = "PPP_loan_dataset.csv"


def main():
    #start the playwright context
    with sync_playwright() as p:
        #Launch a chromium browser (set headless=True so it can run in the background)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        #Go to the organization index page
        page.goto(BASE_URL)
        print(f"Navigated to {BASE_URL}")

        #Click on the PPP FOIA dataset link from the navbar
        try:
            page.wait_for_selector('a[href="/dataset/"]', timeout=5000)
            page.locator('a[href="/dataset/"]').click()
            print("Clicked on the Dataset link from the Navbar")
        except Exception as e:
            print(f"Error clicking on PPP FOIA Dataset link: {e}")
            browser.close()
            return

        #From the dataset listings, click the "PPP FOIA" link
        try:
            page.wait_for_selector('h2.dataset-heading a[href="/dataset/ppp-foia"]', timeout=5000)
            page.locator('h2.dataset-heading a[href="/dataset/ppp-foia"]').click()
            print("Navigated to the PPP FOIA dataset page.")
        except Exception as e:
            print(f"Error clicking on PPP FOIA link: {e}")
            browser.close()
            return
        
        #Click a link for a CSV file
        try:
            page.wait_for_selector('a[href="/dataset/ppp-foia/resource/cff06664-1f75-4969-ab3d-6fa7d6b4c41e"]', timeout=5000)
            page.locator('a[href="/dataset/ppp-foia/resource/cff06664-1f75-4969-ab3d-6fa7d6b4c41e"]').nth(0).click()
            print("Clicked the link for the CSV file page")
        except Exception as e:
            print(f"Error clicking the CSV file page: {e}")
            browser.close()
            return
        
        #Click the Downlaod link
        try:
            page.wait_for_selector('a.btn.btn-primary.resource-url-analytics', timeout=5000)
            download_button = page.locator('a.btn.btn-primary.resource-url-analytics')
            
            with page.expect_download() as download_info:
                download_button.click()
            download = download_info.value # get the download object

            #Download the file to the specified directory with the specified name
            download_path = os.path.join(DOWNLOAD_DIR, CUSTOM_FILE_NAME)
            download.save_as(download_path)
            print(f"File Downloaded to: {download_path}")
        except Exception as e:
            print(f"Error clicking the download button: {e}")
            browser.close()
            return
        
    
        browser.close()
        
if __name__ == "__main__":
    main()