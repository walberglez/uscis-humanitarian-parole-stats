from datetime import date, timedelta
import re
import sys
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from pathlib import Path
import logging

from utils import daterange, get_latest_date, url_ok

CUBAN_SOCIAL_MEDIA_DAILY_REPORT_BASE_URL = 'https://notiparole.com'
SPANISH_MONTH_NAMES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
SPANISH_MONTH_ABBR = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
BASE_REPORT_FOLDER = 'data/social-media-daily-report'
INITIAL_REPORT_DATE = date(2023, 5, 5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('download-cuban-social-media-daily-report')

def get_date_str_v1(date: date) -> str:
  return f'{date.day}-de-{SPANISH_MONTH_NAMES[date.month - 1]}'

def get_date_str_v2(date: date) -> str:
  return f'{date.day}-{SPANISH_MONTH_NAMES[date.month - 1]}'

def get_page_url(page: int) -> str:
  base_url = CUBAN_SOCIAL_MEDIA_DAILY_REPORT_BASE_URL
  
  if page > 1:
    return f'{base_url}/page/{page}/'
  
  return base_url

def find_date_urls(text: str, dates: list[str]) -> list[str]:
  soup = BeautifulSoup(text, 'lxml')

  for date_str in dates:
    links = soup.find_all(href=re.compile(date_str))
    if links:
      return map(lambda link: link.get('href'), links)
  
def get_url(date: date) -> list[str]:
  date_strs = [get_date_str_v1(date), get_date_str_v2(date)]
  urls = None
  pagination = 1

  while urls is None:
    page_url = get_page_url(pagination)
    if not url_ok(page_url):
      return None
    
    page = requests.get(page_url)
    urls = find_date_urls(page.text, date_strs)
    pagination += 1
    
  return urls

def export_to_csv(df: DataFrame, report_date: date, name: str) -> None:
  date = report_date.strftime("%Y-%m-%d")
  filepath = Path(f'{BASE_REPORT_FOLDER}/{date}/{date}-{name}.csv')
  filepath.parent.mkdir(parents=True, exist_ok=True)
  df.to_csv(filepath, index=False)

def get_case_date(date_text: str) -> date:
  date_elems = date_text.split(',')
  
  if date_elems.__len__() != 2:
    date_elems = date_text.split('-')

  if date_elems.__len__() != 2:
    date_elems = date_text.split(' ')
  
  if date_elems.__len__() == 2:
    day = int(date_elems[0])
    month_text = date_elems[1].strip()[:3]
    month = SPANISH_MONTH_ABBR.index(month_text) + 1
    year_text = date_elems[1].strip()[4:]
    year = int(year_text) if year_text else INITIAL_REPORT_DATE.year 

    return date(year, month, day)
  elif date_elems.__len__() == 3:
    day = int(date_elems[0])
    month_text = date_elems[1].strip()[:3]
    month = SPANISH_MONTH_ABBR.index(month_text) + 1
    year = int(date_elems[2]) 

    return date(year, month, day)
  
  raise ValueError('Invalid case date ' + date_text)

def find_table(text: str):
  soup = BeautifulSoup(text, 'lxml')
  tables = soup.find_all('table')

  for table in tables:
    first_row = table.find('tr')

    if not first_row:
      continue
    
    if 'cuba' in first_row.text.lower():
      return table 

  return None

def download_stats(report_date: date) -> None:
  logger.info(f'Download Stats for {report_date}')

  urls = get_url(report_date)

  if urls is None:
    raise ValueError('stats URL not found')

  for url in urls:
    page = requests.get(url)

    if page.status_code != 200:
      raise ValueError('could not get stats page')

    table = find_table(page.text)
    if not table:
      break

  if not table:
    raise ValueError('could not find stats table')

  total = None
  total_unknown = None
  total_denied = None
  total_calculated = 0
  dates = []
  approved_cases = []

  for row in table.find_all('tr'):
    cells = row.find_all('td')
    
    if not cells:
      continue

    date_text = cells[0].text.strip().lower()
    value = None

    try:
      value = int(cells[1].text)
    except:
      continue

    if date_text == 'total':
      total = value
    elif 'desconoce' in date_text \
      or 'precisar' in date_text \
      or 'sin fecha' in date_text:
      total_unknown = value
      total_calculated += total_unknown
    elif 'denegados' in date_text:
      total_denied = value
    elif value == 0:
      continue
    else:
      date = get_case_date(date_text)
      dates.append(date)
      approved_cases.append(value)
      total_calculated += value

  if total is None:
    total = total_calculated

  report_data = {
    'Country': ['Cuba'],
    'ReportDate': [report_date],
    'TotalApproved': [total],
    'TotalApprovedUnknownDate': [total_unknown],
    'TotalDenied': [total_denied]
  }
  report_DF = DataFrame(data=report_data)
  export_to_csv(report_DF, report_date, 'SocialMediaDailyReport')

  report_detail_data = {
    'CaseDate': dates,
    'TotalApproved': approved_cases
  }
  report_detail_DF = DataFrame(data=report_detail_data)
  export_to_csv(report_detail_DF, report_date, 'SocialMediaDailyReportDetail')

  logger.info(f'Stats downloaded for {report_date}')

def download_stats_for_range(start_date, end_date):
  for report_date in daterange(start_date, end_date):
    download_stats(report_date)

def main():
  start_date = get_latest_date(BASE_REPORT_FOLDER)
  if start_date is None:
    start_date = INITIAL_REPORT_DATE
  else:
    start_date += timedelta(1)
  end_date = date.today()
  download_stats_for_range(start_date, end_date)

if __name__ == "__main__":
    sys.exit(main())