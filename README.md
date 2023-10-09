# 3942-osproject
### Features
- Programming Language: python
- Runtime Environment: venv
- Testing Framework: pytest
- Continuous Integration: GitHub Actions
- Static Analysis: flake8
- Code Formatting: black
- Package Manager: pip

### Getting Started
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
5. **Run helloworld.py**
   ```
   python helloworld.py
   ```
6. **Run tests**
   ```
   pytest
   ```
7. **Static analysis and formatting**
   ```
   black .
   flake8 .
   ```

### Continuous Integration
This template uses GitHub Actions for CI. Whenever you push a commit or create a pull request, the CI pipeline will automatically run tests and static analysis checks.
