# USCIS Humanitarian Parole Stats for Cubans

## Description

This project intends to create reports and display stats based on data reported on social media by citizens of Cuba who have received the USCIS Humanitarian Parole https://www.uscis.gov/CHNV.

The data is sourced from https://migentecuba.com/.

## Process

1. Data is scraped and downloaded from the source website.
2. Data is transformed into our data structure.
3. Save daily data to a file in the data folder.

## Reports

- [ ] Approved by Date for a Date
- [ ] Approved by Month for a Date
- [ ] Approved by Date for a Date Range
- [ ] Approved by Month for a Date Range

### Data Structure needed by reports

#### Table SocialMediaDailyReport

| Column                   | Type    |
| ------------------------ | ------- |
| Id                       | Number  |
| ReportDate               | Date    |
| Country                  | String  |
| TotalApproved            | Number  |
| TotalApprovedUnknownDate | Number  |
| TotalDenied              | Number  |

#### Table SocialMediaDailyReportDetail

| Column        | Type    |
| ------------- | ------- |
| Id            | Number  |
| ReportId      | Number  |
| CaseDate      | Date    |
| TotalApproved | Number  |

## Answers to Respond

1. If I applied on date X, when will my case be reviewed following the chronological order.
2. If I applied on date X, what are the chances of my case being reviewed by date Y.

To answer these questions, we will take into account:
- 1,000 cases reviewed per day between Haiti, Venezuela, Nicaragua and Cuba.
- 500 cases are reviewed in chronological order. It doesn't take into account country quotas.
- 500 cases are randomly reviewed. It doesn't take into account country quotas.