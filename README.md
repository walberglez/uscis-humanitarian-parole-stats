# USCIS Humanitarian Parole Stats

## Description

This project intends to collect data and stats related to the USCIS Humanitarian Parole https://www.uscis.gov/CHNV.

## Process

1. Data is scraped and downloaded from the source website.
2. Data is transformed into our data structure.
3. Data is saved to a file in the data folder.

## Data

### Social Media Daily Report

Daily data is being reported for one country in social media right now, Cuba.

The Cuban Social Media Daily Report data is sourced from https://migentecuba.com/.

#### File SocialMediaDailyReport

| Column                   | Type    |
| ------------------------ | ------- |
| Country                  | String  |
| ReportDate               | Date    |
| TotalApproved            | Number  |
| TotalApprovedUnknownDate | Number  |
| TotalDenied              | Number  |

#### File SocialMediaDailyReportDetail

| Column        | Type    |
| ------------- | ------- |
| CaseDate      | Date    |
| TotalApproved | Number  |
