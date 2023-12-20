# Google Task Collector App
### About
This is an application to collect all of a user's tasks from Google and display it in a webpage ensuring easy tracking and management of all tasks across a user's Google applications. In this project, tasks are task items from 'Google Tasks' as well as comments a user is tagged in from 'Google Drive' services such as Google Docs. The application uses Google API's to aggregate all of user's tasks (as defined previously) across different Google applications, and display them all in a single webpage. 

### Features
- Logging in and Authentification through Google
- Aggregating all of a user's 'Google Tasks'
- Displaying all of a user's 'Google Tasks'
- Aggregating all of the comments a user is tagged in from 'Google Drive' (i.e. Google Docs)
- Displaying all of the comments a user is tagged in
- Adding new tasks to Google Tasks
- Deleting tasks from Google Tasks
- Logging out of application

### Requirements
- Please install the 'requirements.txt' file (see Installation instructions below)
- Create a .env file containing APP_KEY, CIENT_ID, CLIENT_SECRET, testing (set it to true), DB_NAME (set it to anything you want)
- The project is provided with a `docker-compose.yml` file to build and run. Please install docker to skip the `requirements.txt` installation step

### Installation
1. **Clone the repository**
   ```
   git clone https://github.com/davidchiii/3942-osproject.git
   cd 3942-osproject
   ```
2. **Create .env
   It should have at least the following components:**
   ```
   APP_KEY=
   CLIENT_ID=
   CLIENT_SECRET=
   testing=This must be true or false
   DB_NAME=
   ```
4. **Create and activate new virtual environment**
   ```
   python -m .venv venv

   # On macOS and Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```
5. **Install dependencies using pip**
   ```
   pip install -r requirements.txt
   ```
6. **Run the MongoDB database**
   ```
   docker compose up -d 
   ```
7. **Export PythonPath**
   ```
   export PYTHONPATH=$(pwd)/app
   ```
7. **Run the app**
   ```
   flask run
   ```

### Usage
1. After running the app, open the Flask site on your web browswer. Press the login button and log in using a valid Google account
2. If prompted with the warning 'Google hasn’t verified this app,' click on advanced and then click on 'Go to TaskCollector (unsafe).'
3. If prompted with 'TaskCollector wants additional access to your Google Account' check the 'select all' box and then continue
4. Once at the homepage of the website you can click 'fetch tasks' to aggregate and display all of the current tasks you have.
5. Click 'fetch comments' to aggregate and display off the the comments you are tagged in
6. Every task list has an ID and Every task within a list has an ID. To add a new task enter the specific Task List ID and the new task's name and press 'Add Task'
7. To delete a task, enter the specific Task List ID and Task ID and select 'delete task'
8. Press 'logout' to logout of the application

### Continuous Integration
This template uses GitHub Actions for CI. Whenever you push a commit or create a pull request, the CI pipeline will automatically run tests and static analysis checks.

### Contribution Guidelines
**Reporting Bugs**
- Use the GitHub Issues tracker to report bugs. Check if the issue has already been reported.
- Clearly describe the issue including steps to reproduce the bug, and the expected and actual outcomes.

**Suggesting Enhancements**
- Use the GitHub Issues tracker to suggest enhancements.
- Clearly describe your enhancement, including the motivation for the change and any examples from other projects or contexts.

**Pull Requests**
- Fork the repository by creating your branch from main.
- Ensure your code adheres to the coding standards (use linting tools and adhere to the coding style of the project).
- Write meaningful commit messages.
- Before creating a pull request, please run ```black .``` and ```flake8 .``` to ensure that your code matches our formatting guidelines.
- Submit a pull request targeting the main branch.

**Code Review**
- All submissions, including submissions by project members, require review.
- We use GitHub pull requests for this purpose.
- Reviewers will consider the design, functionality, and documentation.
- Reviewers may ask for changes to your pull request. This is a normal part of the review process, and ensures that all code is of the highest possible quality.
