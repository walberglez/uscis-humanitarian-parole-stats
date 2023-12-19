from datetime import date, timedelta
import sys
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from pathlib import Path
import logging

from utils import daterange, get_latest_date, url_ok

CUBAN_SOCIAL_MEDIA_DAILY_REPORT_BASE_URL = [
  'https://migentecuba.com/lista-de-paroles-aprobados-el-{date}/',
  'https://migentecuba.com/lista-de-paroles-aprobados-{date}/',
  'https://notiparole.com/paroles-aprobados-{date}/',
  'https://notiparole.com/paroles-aprobados-{date}-cuba/',
  'https://notiparole.com/paroles-aprobados-{date}-en-cuba/',
  'https://notiparole.com/paroles-aprobados-{date}-de-cuba/'
]
SPANISH_MONTH_NAMES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
SPANISH_MONTH_ABBR = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
BASE_REPORT_FOLDER = 'data/social-media-daily-report'
INITIAL_REPORT_DATE = date(2023, 5, 5)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('download-cuban-social-media-daily-report')

def get_date_str(date: date) -> str:
  return f'{date.day}-de-{SPANISH_MONTH_NAMES[date.month - 1]}'
 
def get_url(date: date) -> str:
  date_str = get_date_str(date)

  for base_url in CUBAN_SOCIAL_MEDIA_DAILY_REPORT_BASE_URL:
    url = base_url.format(date=date_str)
    if url_ok(url):
      return url
  pass

def export_to_csv(df: DataFrame, report_date: date, name: str) -> None:
  date = report_date.strftime("%Y-%m-%d")
  filepath = Path(f'{BASE_REPORT_FOLDER}/{date}/{date}-{name}.csv')
  filepath.parent.mkdir(parents=True, exist_ok=True)
  df.to_csv(filepath, index=False)

def get_case_date(report_date: date, date_text: str) -> date:
  day_month = date_text.split(',')
  
  if day_month.__len__() != 2:
    day_month = date_text.split('-')
  
  if day_month.__len__() != 2:
    raise ValueError('Invalid case date ' + date_text)
  
  day = int(day_month[0])
  month_text = day_month[1].strip()[:3]
  month = SPANISH_MONTH_ABBR.index(month_text) + 1
  year = report_date.year

  return date(year, month, day)

def download_stats(report_date: date) -> None:
  logger.info(f'Download Stats for {report_date}')

  url = get_url(report_date)

  if url is None:
    raise ValueError('stats URL not valid')

  page = requests.get(url)

  if page.status_code != 200:
    raise ValueError('could not get stats page')

  soup = BeautifulSoup(page.text, 'lxml')
  table = soup.find('table')

  if table is None:
    raise ValueError('could not find stats table')

  total = None
  total_unknown = None
  total_denied = None
  total_calculated = 0
  dates = []
  approved_cases = []

  for row in table.find_all('tr'):
    cells = row.find_all('td')
    date_text = cells[0].text.strip()
    value = None

    try:
      value = int(cells[1].text)
    except:
      continue

    if date_text == 'TOTAL':
      total = value
    elif 'desconoce' in date_text:
      total_unknown = value
      total_calculated += total_unknown
    elif 'precisar' in date_text:
      total_unknown = value
    elif 'Denegados' in date_text:
      total_denied = value
    elif value == 0:
      continue
    else:
      date = get_case_date(report_date, date_text)
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