import requests
import selectorlib
import smtplib, ssl
from dotenv import load_dotenv
import os
import time
import sqlite3


URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect("data.db")


# Define the scraping function get information from url
def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


# Extract the information from the source variable  and return the desire value
def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)["tours"]
    return value


# send email function
def send_email(message):
    load_dotenv()
    host = "smtp.gmail.com"
    port = 465

    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    receiver = os.getenv("EMAIL")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)

    print("Email was sent!")


# it stores the extracted values into the database using SQLite
def store(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES (?,?,?)", row)
    connection.commit()


# Query data from the database
def read(extracted):
    row = extracted.split(',')
    row = [item.strip() for item in row]
    band, city, date = row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


# Main loop that keeps sending email each time there is a new tour
if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)

        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                body = "Subject: New event found" + "\n"
                message = body + "Hey, new event was found!" + "\n" + \
                    f"{extracted}"
                send_email(message)
        time.sleep(2)