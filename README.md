# Open Source Health Dashboard

[![CI](https://github.com/carsonblee/open-source-health-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/carsonblee/open-source-health-dashboard/actions/workflows/ci.yml)

A simple web app that analyzes a public GitHub repo and provides a "health report" on its open-source best practices.

## Overview

> [!NOTE]
> *This project repo was built to meet the goals, requirements, and deliverables of the JVN Communications, Inc. technical assessment.*

Upon user input of a public GitHub repository via full URL or shorthand of `user/repo`, this lightweight web app fetches information about this repository using the public [GitHub REST API](https://docs.github.com/en/rest) and compares it to a pre-defined open-source health checklist.

These checks are performed by analyzing the GitHub repo API data returned from the request to check for specific files in the contents, such as a `/contents/README.md` file, or in the metadata, such as the `LICENSE` field.

### :heart: Open Source Health Checklist

- :white_check_mark: Has a `LICENSE` file
- :white_check_mark: Has a `README.md` file
- :white_check_mark: Has a `.gitignore` file
- :white_check_mark: The repository has had a commit within the last 6 months
- :white_check_mark: The repository uses GitHub Actions (i.e., a `.github/workflows` directory exists)

### :gear: DevOps & Automation

1. This application is containerized with [Docker][2] and defined within the [Dockerfile](Dockerfile) and [docker-compose.yml](docker-compose.yml).

2. A pre-commit hook is also implemented and defined in [.pre-commit-config.yaml](.pre-commit-config.yaml) which enforces a quality standard locally by running a linter ([Flake8][1]) as well as some other quality standards before any commits are allowed to be made.

3. Lastly, this project uses a basic Continuous Integration pipeline ([ci.yml](./github/workflows/ci.yml)) throught GitHub Actions that is reponsible for two actions:

   1. **Linting the code:** once again, using [Flake8][1]
   2. **Testing the code:** using automated unit tests using [pytest][4] defined in [test_app.py](./tests/test_app.py)

## How to Set Up & Run

### :toolbox: Pre-Requisites

1. [Docker][2]
2. [Docker Compose](https://docs.docker.com/compose/install/)

### :clipboard: Steps

**Step 1:** Clone this project

```bash
git clone https://github.com/carsonblee/open-source-health-dashboard.git

cd open-source-health-dashboard
```

**Step 2:** Build and start the web app

```bash
docker-compose up --build
```

**Step 3:** Go to localhost in your browser

*MacOS users may experience an issue with port 5000 because it is already in use. You can free this port by turning off “AirPlay Receiver” in the “Sharing” System Preferences*

```bash
open http://localhost:5000
```

**Step 4:** Enter a GitHub repo URL or shorthand of user/repo

Example: ```https://github.com/EbookFoundation/free-programming-books```

**Step 5:** Make sure to shut down the Docker container once finished

## Key Design Choices

### :test_tube: Python & Flask

Flask was used because of its lightweight nature: keeping the project simple, easy to read, with a smaller overhead than alternatives. Its simple integration with Python makes it an obvious choice than building out a massive frontend for a single-page web application.

### :telephone_receiver: GitHub REST API

This web app uses the public GitHub REST API to fetch data about the given repository without the need for a token, which allows for minimal setup for unauthenticated requests (limited to 60 per hour).

### :whale: Multi-stage Dockerfile

The first stage compiles a basic Python wheels while the second stage only copies over wheels and the app source. This optimizes the production image by keeping it small with no uneccesary build tools.

### :hook: Pre-commit Hooks

The pre-commit hook enforces a local quality standard that lints the code before allowing for any commits.

```bash
# To install the pre-commit hook
pre-commit install

# To run the pre-commit hook
pre-commit run --all-files
```

### :mag: CI Pipeline (GitHub Actions)

The Continuous Integration pipeline defined in [.github/workflows/ci.yml][3] is triggered on push and pull requests to the `main` branch. It defines two (2) separate jobs on each run:

1. **Lint:** runs [flake8][1]
2. **Test:** runs [pytest][4] with the tests defined in [`/tests/test_app.py`](./tests/test_app.py)

[1]: https://flake8.pycqa.org/
[2]: https://www.docker.com/
[3]: ./.github/workflows/ci.yml
[4]: https://docs.pytest.org/
