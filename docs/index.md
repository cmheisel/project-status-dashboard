# project-status-dashboard

## Overview

project-status-dashboard is a way to surface information about multiple projects that are tracked in [JIRA](https://www.atlassian.com/software/jira) and to [expose predictions](http://focusedobjective.com/monte-carlo-forecasting-exercises/) about when they're completed.

You manage what projects are tracked and how they're displayed via [a Google spreadsheet](https://www.google.com/sheets/about/).

## How to use the dashboard

### Set up your Google spreadsheet
![Sample spreadsheet](img/sample-gsheet.png)

1. Create a google spreadsheet with *whatever columns* you want to display
1. Create a *special column* called **_jira_filter** this is how we'll tell the dashboard tickets are involved in the project
1. Put one project on each row, filling out as many columns as you like for that project
1. Publish the spreadsheet
    1. File > Publish to Web
    1. Entire Document
    1. [Example spreadsheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vQ950QA97Rfzkya5I1WRmv12wlCPqF5qDeLtQtWKZzH_PZCR9FmApfzZ-83Zbu3bC9hHoi4Tr71UFWd/pubhtml)

### Create a JIRA filter for each project
1. Use whatever *JIRA search criteria* works for your team, common examples include:
    * By Epic: ```"Epic Link" = MYPROJ-101```
    * By tag: ```labels = theawesome-project```
    * By multiple Epics: ```"Epic Link" = MYPROJ-1342 OR "Epic Link" = MYPROJ-1472```
2. Save your JIRA filter
3. Share the JIRA filter with **Everyone**
4. Copy the **JIRA filter ID**: https://jira.example.com/issues/?filter=**12286**
5. Put the **filter ID** into the **_jira_filter** column for that project

![Share the JIRA filter](img/jira-share-filter.png)


### View the dashboard
![Dashboard](img/dashboard-overview.png)
The **_jira_filter** you provided will automatically add several columns to the ones you created

* **JIRA**: A link the filter, so you can dive into specific tickets
* **Forecast**: A link to the Forecast page for the project (see below)
* **Today**: The percentage of complete tickets, and the number of total tickets
    * The arrows indicate a change in completion and/or scope from the prior week
* **Last week**: The percentage of complete tickets, and the number of total tickets from one week ago

### View the forecast
![Forecast overview](img/forecast-overview.png)

The forecast view includes

* A chart displaying the change in scope and completion over time
* A tabular view of that same data
* A forecast of when the work would be completed **assuming the scope doesn't change** with various degress of confidence
* A form to modify the forecast

### Modify the forecast
![Forecast form](img/forecast-form.png)

You can experiment with the forecast to simulate some *"What if"* scenarios

* Modify the number of tickets remaining to see what effect cutting/growing scope might have on the forecasted end date
* Modify how many past days are sampled to generate the forecast if you think the default 30 day view is atypical -- maybe the past month had a lot of PTO, or maybe the team just shrunk because some folks were reassigned.

## How to deploy the dashboard

The dashboard is provided as a [Docker container](https://hub.docker.com/r/cmheisel/project-status-dashboard/) to make deployment relatively straightforward. [Docker machine](https://docs.docker.com/machine/) is an easy way to spin up Docker hosts in the cloud or on VMs, and [Docker compose] is an easy way to spin up the dashboard container on your host.

There's a [sample docker-compose file](https://github.com/cmheisel/project-status-dashboard/blob/master/docker-sample/docker-compose.yml) in the repository that will spin up the dashboard container and a [redis container](http://redis.io/) which is used for caching and for job queing.

The following settings are controlled via environment variables in the docker-compose file:

```
environment:
  - DB_NAME=/data/sample.db  # What you want the database file to be called
  - GOOGLE_SPREADSHEET_ID=1NJ90QUwSgGYwRdDmvOcxi-QKxfdmcB5IZHi9pXhu1Hw  # The ID of your google spreadsheet
  - JIRA_URL=http://jira.example.com  # The URL of your JIRA instance
  - JIRA_SSL_VERIFY=True  # If you want the SSL certificate verified, set to False if you're using a self-signed cert
  - JIRA_AUTH=user,password  # The user and password to connect to JIRA
  - JIRA_DONE=Closed,Merged  # The list of states that should be considered "Done" when analyzing tickets
  - GUNICORN_WORKERS=10  # The number of web server workers to spin up, add more if your dashboard receives high traffic
  - REDIS_URL=redis:6379  # Default set for the docker container, can change it if you're hosting your own redis
```
