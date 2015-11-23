# Overview

AutoRegisterBot is an automated course registration tool. My hope is to build this out into an application that registers you for courses as they become available on InTouch.

There are three main components

- Registration automation
	- ghost.py webkit client and Beautiful Soup
	- Can be run through Flask app or with command line interface
- Querying Registrar API to check course status
	- Consumes and builds an API
	- Requests and Flask routing
- Using Registrar API to build list of available classes for JSON file
	- Consumes an API 
	- Requests

# To Run
Everything must be run in the virtual environment.

To run the command line interface for course registration: 
	- Pass in the following arguments: username, password, subject, course, section
	- Use the --display flag to run with visual mode
			
To create the JSON file (only needs to be done once, and I have already done it), run the create_courses_json() function in bot.py. 

In order to run the web application you need the Pip modules listed in requirements.txt. To start the Flask server, enter the directory with bot.py, and run:
	python bot.py

This will start the Flask server up. From there, browse to http://localhost:5000 to visit the application. The application itself is relatively self-explanatory. You can search for classes with the input. You can only select classes that are available this semester. These classes are found in the dropdown. Once you select a class, the application will tell you whether the class is currently open or closed. If it is open, it will present you with another form, where you can register for the class. You type in your Penn credentials (PennKey and password), and the fun begins. The application uses a headless browser to go to Penn InTouch and register for the course you selected. When registration completes, the application returns a picture of the result on InTouch, alerting you to whether it completed successfully or not. 

I used a decorator to indicate when the registration function starts and finishes. I used a custom class to manage the stateful API parsing.
	
The logic of the application is separated between two files, bot.py and register.py. Bot.py handles the Flask logic, as well as the JSON parsing. Register.py handles the actual registration and the headless browsing. There is also a fair amount of HTML, CSS, and JavaScript handling the templating, styles, and animations.

# Re
I use re in two places. For one, I use it to easily find text matching my description in a BeautifulSoup instance. This allowed me to easily target parts of the page for the headless browsing. I also used it to parse pieces of information in the Registrar API, namely to extract the subject and course number from the course description IDs.

# OS
I used os to get around a limitation in the GUI toolkit used by ghost.py. Namely, instances of ghost had to begin in the main thread, and any further access to it had to happen in the same thread. Flask does some weird stuff with threads, so I ended up using os.system to run the ghost script. This allowed me to circumvent the thread issue.
	
There is a lot of cool stuff going on behind the scenes here, and I can go through most of it with you in person. A couple highlights:  
- Using requests to parse the Registrar API 
- Building the courses.json file
- Checking whether courses are open or closed
- Circumventing limitations with QT
- Signing users up for classes
- Using JavaScript and Skeleton for the styling and animations
- Populating the auto-complete form
- Using BeautifulSoup to navigate the InTouch DOM. InTouch is very tricky to automate, but I used BeautifulSoup along with Ghost.py to extract and execute the right JavaScript functions. 