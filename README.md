# Google Task Collector App
### About
This is an application to collect tasks from Google. Tasks can be created on the Gmail page and on a Google Doc.

### Features
- 

### Installation
1. **Clone the repository**
   ```
   git clone https://github.com/davidchiii/3942-osproject.git
   cd 3942-osproject
   ```
3. **Create and activate new virtual environment**
   ```
   python -m venv venv

   # On macOS and Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```
4. **Install dependencies using pip**
   ```
   pip install -r requirements.txt
   ```
5. **Run the app**
   ```
   python app/__init__.py
   ```

### Continuous Integration
This template uses GitHub Actions for CI. Whenever you push a commit or create a pull request, the CI pipeline will automatically run tests and static analysis checks.

### Contributing
Before creating a pull request, please run ```black .``` and ```flake8 .``` to ensure that your code matches our formatting guidelines.