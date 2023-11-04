from datetime import date, datetime, timedelta
import os
import requests

def daterange(start_date: date, end_date: date) -> any:
  for n in range(int((end_date - start_date).days)):
    yield start_date + timedelta(n)

def url_ok(url: str) -> bool:
  try:
    response = requests.head(url)
    return response.status_code == 200
  except requests.ConnectionError as e:
    return False
  
def get_latest_date(path: str) -> date:
  if os.path.exists(path) == False:
    return None
  
  try:
    dates = os.listdir(path)
    if dates is None:
      return None

    dates.sort()

    latest_date_str = dates[-1]
    return datetime.strptime(latest_date_str, '%Y-%m-%d').date()
  except:
    return None