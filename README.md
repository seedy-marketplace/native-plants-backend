[Project Backlog](https://github.com/orgs/seedy-marketplace/projects/1/views/1)

[Project Planning and Documentation](https://drive.google.com/drive/folders/1ivcA0_8ouJqmQ-Y3_hFjtCpC_T124ceZ?usp=share_link)

Link To Running Website
* https://native-plants-fe.herokuapp.com/
Link to Repos:
* https://github.com/seedy-marketplace/native-plants-backend
* https://github.com/seedy-marketplace/native-plants-frontend

Environment Information
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


List of unrealized features:
* Mapping & Search through Map
* Interaction tracking
* Implement Lab data interfaces
* Bulk import seed collection

