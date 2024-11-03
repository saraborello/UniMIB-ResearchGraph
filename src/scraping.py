from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.disco.unimib.it/it/dipartimento/staff")


content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

staff_data = {}


for person in soup.find_all('div', class_='views-row'):
    
    name_tag = person.find('div', class_='nomepersona').find('a') if person.find('div', class_='nomepersona') else None
    full_name = name_tag.get_text(strip=True) if name_tag else None

    if not full_name:
        continue

    
    ssd_div = person.find("div", class_="views-field views-field-field-ssd")
    if ssd_div:
        ssd_tag = ssd_div.find("span", class_="field-content")
        ssd = ssd_tag.get_text(strip=True) if ssd_tag else "SSD not available"
    else:
        ssd = "SSD not available"

    
    role_div = person.find_previous("div", class_="paragraphs-item-testo titolo-evidenziato")
    if role_div:
        role_tag = role_div.find("h3", class_="js-views-accordion-group-header titolo_paragrafo")
        role = role_tag.get_text(strip=True) if role_tag else "Role not available"
    else:
        role = "Role not available"

    # Special case 
    if full_name == "ANTONIOTTI MARCO":
        staff_data[full_name] = {'ssd': ssd, 'role': "Full Professor"}
    elif full_name not in staff_data or (staff_data[full_name]['ssd'] == "SSD not available" and ssd != "SSD not available"):
        staff_data[full_name] = {'ssd': ssd, 'role': role}

driver.quit()

with open('data/raw/staff_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Full Name', 'SSD', 'Role'])
    for name, details in staff_data.items():
        writer.writerow([name, details['ssd'], details['role']])

print("Extraction completed and data saved to 'staff_data.csv'")

