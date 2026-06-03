# HabiTrack

## Description
Welcome to my first post-Sofware-Workshop2 module project. I practiced a lot of Python and Flask for this module and wanted to try making my own little personal project that covers similar content from the module. My main part in this project was the inital planning by planning the project, database schema, setting up the forms, the inital logic for the login/registration, index, habit management and progress pages. 

Towards the end, since I'm about to start my actual Summer Project, I then checked out on completing the rest of the project with AI prompts to clean up the rest of my logic regarding how the habit views were altered and other bugs, the front end part by implementing CSS and Bootstrap.

This project in overall is a simple habit tracking website that allows users to:
- Login and Register using flask_login
- Create and track personal habits, you can assign each habit a name, description, category, and frequency
- View a habits dashboard which displays the user's habits, summarising daily, weekly, and monthly progress, and viewing upcoming habits (Querying and filtering)
- Habit management, users can create, update, and delete habits (CRUD operations)
- Analyse their progress through an analytics page, this summarises and visualises their performance and compare different habits

## Usage
To open this project, open up a virtual and install the relevant dependencies:
- pip install flask
- pip install flask-wtf
- pip install flask-sqlalchemy
- pip install flask-login

Then you can flask run to load up the webpage

You may use the username: "admin" and password: "admin" to see the sample data I used while I was testing if the dashboard was working.
