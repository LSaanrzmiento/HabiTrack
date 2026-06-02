# HabiTrack

## Description
Welcome to my first post-Sofware-Workshop2 module project. I practiced a lot of Python and Flask for this module and wanted to try making my own little personal project that covers similar content from the module. This project in partiular is a simple habit tracking website that allows users to:
- Login and Register using flask_login
- Create and track personal habits, you can assign each habit a name, description, category, and frequency
- View a habits dashboard which displays the user's habits, summarising daily, weekly, and monthly progress, and viewing upcoming habits (Querying and filtering)
- Habit management, users can create, update, and delete habits (CRUD operations)
- Analyse their progress through an analytics page, this summarises and visualises their performance and compare different habits (This is new to me, wish me luck)

I have also put comments almost everywhere, this is mainly for me because looking back at my notes, I need comments to figure out what the helly I was typing back when I made those notes.

## Usage
To open this project, open up a virtual environment and flask run

## Latest Updates (02/06/2026):
Okay I have now done some work on the database. I did the exercise of working out the ER diagrams. Most of it was pretty straight forward for the most part. I identified they key classes and relationship:
- User has a 1-M relationship with a Habit, a user can have many habits, and each habit is associated with a user
- Habit has a 1-1 relationship with a Category, each habit has a present category which I will set
- Habit has a 1-M relationship with Habit Log, each Habit will have multiple logs for each instance a habit is to be completed, and each log is associated with that one habit

![ER Diagram](/app/static/Images/HabiTrack_ER_Diagram.png)

Now the trickier part was when I was figuring out how to set the frequency of generating the Habit Logs with regards to the Habit Schedule. I wanted to cover:
- Daily
- Every nth day(s) of the week
- Every nth day of the month
- Every n days intervals

Daily, monthly, and intervals was very straightforward in the sense that each habit by default is a daily habit. Monthly and interval habits will have a nullable attribute in the schedule class, so if the frequency type was set to interval, Interval days are set, same for monthly and day of month. 

I wanted to now see how to model weekly intervals for multiple days of the week like every Monday and Thursday because the intervals are not fixed. AI then helped suggest I add another Entity called Schedule Day of Week specifically for habits which are weekly habits. So for each day of the week selected, the Habit Schedule will pick up those days of the week and set those as days to create the habit logs.

Moving forward here is my updated To Do List:
### 1. Test the database works with a working dashboard
Now that we have the database, I want to make sure it works like I think it should. I'll do the setup.py file and fill it in with dummy data at first and creating some habits for each type of data frequency. 

I think the challenge will be how I approach generating multiple habit logs for each type of data frequency. Also how long should I actually generate these logs for? If I set something as a monthly habit, how far does the habit log generation extend to? I'll probably check out how calendar and other habit tracking apps do this without extending to the end of time, or see if theres libraries that sort this out.

If I need to alter any changes with the database I've figured out how to use flask migrate now, but we'll see it in action if theres any bugs or changes needed to the schema.

### 2. Developing the habit management features (CRUD)
Once I can generate a working dashbaord, I'll add the funcitonality of adding, editting, and deleting the habits.

### 3. CSS and Bootstrap

## Previous Update (31/05/2026):
So far I have just completed the login and registration logic and pages. There is quite some work to do over the week omg. This is my to do list:

### 1. Developing dashboard, habit management, and analytics pages
I still need to do the logic for each page in the website, I think I'll have to do the dashboard and habit management in parallel since it's all about setting up the database and relationships. Which reminds me that I need to do an E-R diagram to figure out the objects and the relationships between them.

The analytics page can come last because thats built on top once the database has been established. Eh, we'll see how this goes over the next couple of days.

### 1.1. Working out how to Flask migrate
This module has taught me how to create_all() and drop_all() but I'll need to learn how to migrate the database because the models.py will probably be going through a lot of versions and at some point it might be better for me to migrate the data instead of restarting it completely every time.

### 2. CSS and Bootstrap
We actually need to make the website pretty with CSS and Bootstrap. Maybe I'll do this for the dashboard and habit management pages once their logic is done, then figure it out for the analytics. I still need to finalise what kind of analytics and visuals we're putting on that page.
