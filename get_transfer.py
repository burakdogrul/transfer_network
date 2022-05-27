import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
#from webdriver_manager.chrome import ChromeDriverManager

def main():
    options = Options()
    options.add_argument("window-size=800,600")
    ua = UserAgent()
    user_agent = ua.random

    options.add_argument(f'user-agent={user_agent}')
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver = webdriver.Chrome(r"C:\Users\Burak\.wdm\drivers\chromedriver\win32\101.0.4951.41\chromedriver.exe", options=options)

    name = []
    country=[]
    position = []
    age = []
    from_team = []
    to_team = []
    date = []
    price = []

    len_page=7450

    for i in range(0,len_page+1):
        print(i)
        url = 'https://www.footballtransfers.com/en/transfers/confirmed/'+str(i)
        driver.get(url)
        scrap_data(driver,name,country,position,age,from_team,to_team,date,price)
        if i%10\
                ==0:
            pd.DataFrame({"Name": name, "Country": country, "Position": position, "Age": age, "From": from_team, "To": to_team,"Date": date,"Price": price}).to_csv("temp_all_transfer.csv")

    data = pd.DataFrame({"Name": name, "Country":country,"Position": position, "Age": age, "From": from_team, "To": to_team, "Date": date,
                       "Price": price})
    data.to_csv("all_transfer.csv")

def scrap_data(driver,name,country,position,age,from_team,to_team,date,price):
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find("tbody", attrs={"id": "player-table-body"})

    for row in results.find_all("tr"):
        try:
            name.append(row.find("a").text)
        except (AttributeError,TypeError):
            name.append("x")
        try:
            country.append(row.find("figure", attrs={"class": "small-icon-image"}).find("img",alt=True)["alt"])
        except (AttributeError,TypeError):
            country.append("x")
        try:
            position.append(row.find("span", attrs={"class": "sub-text d-none d-md-block"}).text)
        except (AttributeError,TypeError):
            position.append("x")
        try :
            age.append(row.find("td", attrs={"class": "m-hide age"}).text)
        except (AttributeError,TypeError):
            age.append("x")
        try:
            from_team.append(row.find("div", attrs={"class": "club-from d-flex align-items-center"}).find("img",alt=True)["alt"])
        except (AttributeError,TypeError):
            from_team.append("x")
        try:
            to_team.append(row.find("div", attrs={"class": "club-to d-flex align-items-center"}).find("img",alt=True)["alt"])
        except (AttributeError,TypeError):
            to_team.append("x")
        try :
            date.append(row.find("td", attrs={"class": "text-center date"}).find_all("div")[1].text)
        except (AttributeError,TypeError):
            date.append("x")
        try:
            price.append(row.find("td", attrs={"class": "text-center m-hide"}).find("span", attrs={"class": "only-tag"}).text)
        except (AttributeError,TypeError):
            try:
                price.append(row.find("td", attrs={"class": "text-center m-hide"}).find("span", attrs={"class": "player-tag player-tag-dark"}).text)
            except (AttributeError,TypeError):
                price.append("x")

if __name__ == '__main__':
    main()

