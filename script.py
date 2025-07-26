import os
import requests
import tabula
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.message import EmailMessage

'''
Get link to court schedule pdf 
'''
def get_url():
    url = "https://www.nysd.uscourts.gov/about/news-and-events"
    # Fetch the page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            if 'Proceedings' in link_str:
                pdf_path = 'https://www.nysd.uscourts.gov/' + link_str
                print("PDF: ", pdf_path)
                return pdf_path

'''
Read first page of the PDF
'''
def build_table(pdf_path):
    # Read the table from the PDF on page 1 excluding header stuff
    dfs = tabula.read_pdf(pdf_path, area=[170, 0, 1000, 1000], pages=1, multiple_tables=True)
    df = dfs[0]

    # Rename columns
    df.columns = ['Case Name', 'Case No.', 'Proceeding', 'Judge', 'Room/Telephone', 'Date', 'Time', 'NA']
    df = df.drop(columns=['NA'])
    first_table = df

    # Get remaining pages of schedule
    all_tables = tabula.read_pdf(pdf_path, pages='all', pandas_options={'header': None}, multiple_tables=True)
    for table in all_tables[1:]:
        table = table.drop(columns=[0, 8])
        table.columns = ['Case Name', 'Case No.', 'Proceeding', 'Judge', 'Room/Telephone', 'Date', 'Time']
        first_table = pd.concat([first_table, table], axis=0)

    all_cases = first_table.reset_index(drop=True)
    all_cases= all_cases.dropna(how='all')
    return all_cases

def main():
    path_url = get_url()

    is_new = False
    with open('latest.txt', 'r+', encoding='utf-8') as file:
        last_schedule = file.read()
        if last_schedule != path_url:
            is_new = True
            file.write(str(path_url))

    if is_new:
        table = build_table(path_url)

        # Compose the email
        msg = EmailMessage()
        week_i = path_url.find("Proceedings%2") + len("Proceedings%2")
        week = path_url[week_i:].split('%',1)[0]
        msg["Subject"] = f"Court Schedule {week}"
        msg["From"] = "molly.taylor@ft.com"
        msg["To"] = ", ".join(["molly.taylor@ft.com", "mollypt@princeton.edu"])
        msg.set_content("Attached is the latest court schedule report.")
        msg.add_attachment(
            table.to_csv(index=False).encode("utf-8"),
            maintype="text",
            subtype="csv",
            filename="court_report.csv"
        )
        # Send using Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("molly.taylor@ft.com", "adxz qttq drvy zpnu")  # Use app password, not your real one
            smtp.send_message(msg)

        print("Email sent with CSV attached.")
    else:
        print("Schedule already sent.")

if __name__ == '__main__':
    main()
