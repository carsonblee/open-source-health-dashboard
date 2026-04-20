# Open Source Health Dashboard

A simple web app that analyzes a public GiTHub repo and provides a "health report" on its open-source best practices.

> [!NOTE]
> *This project repo was built to meet the goals, requirements, and deliverables of the JVN Communications, Inc. technical assessment.*

## Open Source Health Checklist

- :white_check_mark: Has a `LICENSE` file
- :white_check_mark: Has a `README.md` file
- :white_check_mark: Has a `.gitignore` file
- :white_check_mark: The repository has had a commit within the last 6 months
- :white_check_mark: The repository uses GitHub Actions (i.e., a `.github/workflows` directory exists)

## How to Run

```bash
# 0. Open Virtual Environment
. .venv/bin/activate

# 1. Build and Start
docker-compose up --build

# 2. Go to LocalHost in Browser
open http://localhost:5000
```
