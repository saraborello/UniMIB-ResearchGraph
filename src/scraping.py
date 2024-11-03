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
        ssd = ssd_tag.get_text(strip=True) if ssd_tag else "SSD non disponibile"
    else:
        ssd = "SSD non disponibile"

    role_div = person.find_previous("div", class_="paragraphs-item-testo titolo-evidenziato")
    if role_div:
        role_tag = role_div.find("h3", class_="js-views-accordion-group-header titolo_paragrafo")
        ruolo = role_tag.get_text(strip=True) if role_tag else "Ruolo non disponibile"
    else:
        ruolo = "Ruolo non disponibile"

    if full_name == "ANTONIOTTI MARCO":
        staff_data[full_name] = {'ssd': ssd, 'ruolo': "Professore/ssa ordinario/a"}
    elif full_name not in staff_data or (staff_data[full_name]['ssd'] == "SSD non disponibile" and ssd != "SSD non disponibile"):
        staff_data[full_name] = {'ssd': ssd, 'ruolo': ruolo}

driver.quit()

with open('data/raw/staff_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Nome Completo', 'SSD', 'Ruolo'])
    for name, details in staff_data.items():
        writer.writerow([name, details['ssd'], details['ruolo']])

print("Estrazione completata e dati salvati in 'staff_data.csv'")
