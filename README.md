# PIPETEST APP
## Description 
The application is periodically checking for Github users publically available gists, and creates Deal in Pipedrive CRM for each gist.

## Build docker image
In order to build a docker image run the following command from the projects root directory

    docker build -t pipetest .

## Configuration
Application configuration is done via environment variables. Application is written in python using Flask framework.

### Mandatory environment variable 
* `PIPETEST_PIEPEDRIVE_COMPANY_NAME` - Comapny name in Pipedrive. Default value is set to **antonsawesomecompany**
* `PIPETEST_PIEPEDRIVE_API_KEY` - API key for Pipedrive API (should match `PIPETEST_PIEPEDRIVE_COMPANY_NAME`) 

### Optional environment variables (have default value)
* `PIPETEST_QUERIED_USERS` - Comma separated list of GitHub users which will be queried by the app. (ex `PIPETEST_QUERIED_USERS=Kiedis,Flea,Smith,Frusciante`) <br>Default value set to **antomer**
* `PIPETEST_QUERYING_INTERVAL` - Interval in *minutes* for how often user gists will be fetched from the GitHub. <br>Default value set to **30**
<em><br><br>!NB As GitHub API has a limit for unauthorized requests. while configuring application it should be considered that amount of queried users * 60 / querying interval should not be more than 60, otherwise, requests will start to fail </em>

## Database
The application is using a local simple database (TinyDB) to store sessions and fetched data. It has two tables: `users`, and `sessions`. Users table stores GitHub username with a list of IDs of publicly available gists. Session table stores unique session_id from the session cookie, and lastly shown gists for a particular session.
<br><br> 
In order to avoid data duplication in Pipedrive CRM (ex multiple organizations for same user), it is recommended to mount `/db/` folder to the container, otherwise on each run DB will be recreated from scratch.

## Run application
Run following command from projects root directory 

    docker run -v ${PWD}:/db PIPETEST_PIEPEDRIVE_COMPANY_NAME=<comapny_name> -e PIPETEST_PIEPEDRIVE_API_KEY=<api_key> -p 8080:8080 -it pipetest:latest

### Access locally run application
    curl localhost:8080/getAllScannedUsers
## HTTP endpoints
#### Health Endpoint
**Path:** /health<br>
**Allowed methods:** GET<br>
**Description:** returns status of application<br>

#### Get all scanned users
**Path:** /getAllScannedUsers<br>
**Allowed methods:** GET<br>
**Description:** returns all users ever scanned by the app.<br>

#### Get all scanned users
**Path:** /getAllScannedUsers<br>
**Allowed methods:** GET<br>
**Description:** returns list of currently being scanned, may be different, if `PIPETEST_QUERIED_USERS` configuration was changed.<br>

#### Get new gists
**Path:** /getGists<br>
**Allowed methods:** GET<br>
**Description:** returns list of new gists for particular session. If session cookie is expired, or not present, then all gists ever fetched by the application will be in response.<br>

#### Get all scanned users
**Path:** /getAllScannedUsers<br>
**Allowed methods:** GET<br>
**Description:** returns list of users currently being scanned, may be different, if `PIPETEST_QUERIED_USERS` configuration was changed.<br>

## Possible improvements
* Remove expired sessions from DB
* Check if an organization or deal in Pipedrive exists before creating.
* And many more..