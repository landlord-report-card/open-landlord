## Overview
Open Landlord (AKA Landlord Report Card) is a web application that can be used to surface information relating to landlords and property owners in a particular area. Currently (as of October 2022), there is only one instance of the project deployed publicly, in the City of Albany, NY, accessible at albanylandlord.com

## Technology
The web application uses the Flask framework, which is as Python-language framework for building web applications. Data is stored in a Postgres database, and the application uses a framework called SQL Alchemy to interact with the database. The frontend uses simple HTML, CSS, Javascript, and Bootstrap. The application gets deployed using Heroku.

## Data
The application uses publicly-available data to seed the database. Currently, it depends on tenant complaints, code violations, and landlord/tenant police incidents as provided by the City of Albany. While the database holds additional data, only these fields are used in the scoring process.

The database is populated and updated using the populate_db.py script within the repo. It assumes that the data uses the CSV format of exports that is currently used by the Tolemi Building Blocks software used by Albany, but could be modified to be populated with data in another format or from another source.

## Developing and Running Locally
If you'd like to develop or contribute changes, the first step is likely to get a version of the app running locally. Steps:

1. Clone the repository locally (Details: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)

2. Install the needed requirements in the requirements.txt file. (Details: https://note.nkmk.me/en/python-pip-install-requirements/)

3. Connect the app to a database. You'll need credentials for an existing database for the app to read from. This is dependent on the LANDLORD_DATABASE_URI environment variable. Set this variable locally to the JDBC connection string for your database. (e.g. LANDLORD_DATABASE_URI=postgresql://username:password@database-server-name-here)

4. Type "flask run" into your terminal. This should launch the app.

5. Access the app in your browser at http://localhost:5000/
