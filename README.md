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
* NodeJS
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
* https://github.com/RoryMoeller/native-plants-backend
* https://github.com/RoryMoeller/native-plants-frontend
List of unrealized features:
* “Smarter” auto updating database inserts (example from partner: when a user attempts to upload a seed collection history for a stand that doesn’t exist yet, the database should make that stand then make the history. Current build requires the stand be made separately)
* This brings up some general user friendly-ness to be had. Most of which is similar to the last note, where users need there to be already existing data in the database to add some other thing.
* Requests from land managers to send notifications, users can post requests to database, but the database will not tell them if that request has been fulfilled
* There is no storage history for a given seed collection.
* There is not expansion on the plant species table, for adding pseudonyms
* Connection to ITIS database through cronjobs, there is an already existing database and connecting to it would allow us to query it as well as our own database. This would require less set up for the website, as users do not need to re-input data they have in the ITIS database
* Map navigation link export, display collection locations on map & provide a way to let users export data for navigation, like gMaps link.
* Display partial data of the database. The back-end code has been written and the data can be obtained successfully. However, since there is no valid data inserted into the database, the front end cannot display the back-end data at present. For the new capstone group in the future, it only needs to modify the front-end port to obtain the back-end data.
* Get the seed collection coordinates from the database and display them on the front-end map. Since the back end has no coordinates, the front end cannot get coordinates to display the location.


Things to expand:
* Local searching, in the current build when a user calls for data from the database it makes a call to the database each time. In a better world it would do that once and filter that data client side and not make more calls to the database.
* Some changes to certain functions, for example in the accessBackendAPI.js the DELETE call only accepts 1 field for identifying what to delete. In an ideal world this would accommodate any amount of fields
* Store coordinate information from the front end, and then display it from the GIS map. This is a difficult point for front-end and back-end linkage. 
* Map search bar, search for seed names and display related ranges on the map. With sufficient data at the back end, and the seed name can be associated with the coordinate field, this is a function that can be realized.
* User supplied file insertion into database, some users have xml files of data and it would be more convenient if they could upload that instead of retyping it all out
