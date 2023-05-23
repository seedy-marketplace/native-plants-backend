Native Plants Partnership Backend
Run:
* Clone repo
* Install dependencies listed in requirements.txt
* Set environment variables for:
   * DB_HOST_NAME
   * DB_USER
   * DB_PASS
   * DB_NAME
   * DATABASE_URL
   * DATABASE_KEY
* Run python3.9 backend/postgresql_backend.py
   * Or whatever python alias points to a sufficiently updated python version

[Project Backlog](https://github.com/orgs/seedy-marketplace/projects/1/views/1)


All Software (can be found in both READMEs)
* Heroku server (Backend–With PostGIS database added, Frontend)
* Heroku CLI
* NodeJS (most recent version)
* NPM (most recent version)
* Python 3.9 or newer
List of Steps to Run Project
Run Locally
* Front-end
* Clone repo
* Run “npm i”
* Set environment variables for (easy to set from a untracked .env.local file):
   * DATABASE_KEY
   * NEXTAUTH_SECRET
* Run “npm run dev”
* Back-end
* Clone repo
* Install dependencies listed in requirements.txt
* Set environment variables for:
   * DB_HOST_NAME
   * DB_USER
   * DB_PASS
   * DB_NAME
   * DATABASE_URL
   * DATABASE_KEY
* Run python3.9 backend/postgresql_backend.py
   * Or whatever python alias points to a sufficiently updated python version
Push Updates to Heroku
* Clone repo
* Make edits
* Commit
* Run “git push heroku master”
   * Sign into Heroku CLI if needed
Link To Running Website
* https://native-plants-fe.herokuapp.com/
Link to Repos:
* https://github.com/seedy-marketplace/native-plants-backend
* https://github.com/seedy-marketplace/native-plants-frontend

List of unrealized features:
* User edditing of organizations and their properties
* Mapping & Search through Map
* Interaction tracking
* Lab involvement
* bulk import seed collection

