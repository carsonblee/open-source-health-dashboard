import re
from datetime import datetime, timezone, timedelta

import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Pre-defined GH API base URL and headers for request
GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json"}

# Day threshold for recent commits (6 months = 183 days)
DAYS_RECENT_THRESHOLD = 183


# %%%%%%%%%%%%%%% A: PARSE GH REPO AND OWNER FROM USER INPUT %%%%%%%%%%%%%%%
def parse_repo(url: str) -> tuple[str, str] | None:
    """
    Extract GH owner/repo from a GitHub URL or 'owner/repo' string
    """

    url = url.strip().rstrip(
        "/"
    )  # Strip whitespace and any trailing slashes from URL to sanitize
    pattern = r"(?:https?://github\.com/)?([^/\s]+)/([^/\s]+)"  # Outline regex pattern to be matched
    m = re.fullmatch(
        pattern, url
    )  # Check to see if URL matches outlined regex pattern for GH user and repo
    if not m:  # If not, return None and abort
        return None
    return m.group(1), m.group(
        2
    )  # Returns [GH user, repo] as long as everything goes according to plan


# %%%%%%%%%%%%%%% B: FETCH REPO DATA FROM GITHUB API %%%%%%%%%%%%%%%
def gh_get(path: str) -> tuple[dict | list | None, int]:
    """
    Make a GET request to the GitHub API to fetch data,
    returns (data, status_code)
    """

    r = requests.get(
        f"{GITHUB_API}{path}", headers=HEADERS, timeout=10
    )  # Make GET request w/ predefined GH API base and header

    if r.status_code == 200:  # Successful request = return JSON of data
        return r.json(), 200
    return (
        None,
        r.status_code,
    )  # Unsuccessful request = return None and status code for error handling


# %%%%%%%%%%%%%%% C: CHECK REPO FILES/CONTENTS %%%%%%%%%%%%%%%
def check_file_exists(owner: str, repo: str, path: str) -> bool:
    """
    Checks repo contents to see if a file exists
    """

    _, status = gh_get(
        f"/repos/{owner}/{repo}/contents/{path}"
    )  # Calls B: gh_get, to check for specific file based on return status
    return status == 200


# %%%%%%%%%%%%%%% D: CHECK RECENT REPO COMMITS %%%%%%%%%%%%%%%
def check_recent_commit(owner: str, repo: str) -> tuple[bool, str | None]:
    """
    Checks if repo has had a recent commit (last 6 months).
    Returns [is_recent: bool, last_commit_date: str]
    """

    data, status = gh_get(
        f"/repos/{owner}/{repo}/commits?per_page=1"
    )  # Calls B: gh_get, to check for most recent commits

    if (
        status != 200 or not data
    ):  # Failed request = [not recent commit, no last commit date]
        return False, None

    try:  # Tries to find most recent commit date to compare
        date_str = data[0]["commit"]["committer"]["date"]
        commit_dt = datetime.fromisoformat(
            date_str.replace("Z", "+00:00")
        )  # Convert to datetime object, can adjust for timezone if needed
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=DAYS_RECENT_THRESHOLD
        )  # Calculate cutoff date for recent commits
        return (
            commit_dt >= cutoff,
            date_str,
        )  # Return [if it was recent commit, last commit date]

    except (
        KeyError,
        ValueError,
    ):  # If any expected data missing or date parsing fails,
        # return error and say not recent commit
        return False, None


# %%%%%%%%%%%%%%% E: CHECK GITHUB ACTIONS %%%%%%%%%%%%%%%
def check_github_actions(owner: str, repo: str) -> bool:
    """
    Checks if repo has any GitHub Actions workflows defined in .github/workflows/
    """

    data, status = gh_get(
        f"/repos/{owner}/{repo}/contents/.github/workflows"
    )  # Calls B: gh_get, to check for contents of .github/workflows to see if any GH Actions
    return (
        status == 200 and isinstance(data, list) and len(data) > 0
    )  # Return True if request successful AND data is a non-empty list


# %%%%%%%%%%%%%%% F: ANALYZE REPO FOR HEALTH SCORE %%%%%%%%%%%%%%%
def analyze_repo(url: str) -> dict:
    """
    Main function to analyze a GH repo based on health checklist and return results
    """

    parsed = parse_repo(
        url
    )  # Calls A: parse_repo to extract GH user and repo from input URL
    if not parsed:
        return {
            "error": "Invalid GitHub URL. Use https://github.com/owner/repo or owner/repo"
        }  # Throws error if URL parsing fails

    owner, repo = parsed  # Sets tuple [GH owner, cleaned repo name]

    # F.1: FETCH BASIC REPO DATA AND MAKE SURE GOOD STATUS
    repo_data, status = gh_get(f"/repos/{owner}/{repo}")
    if status == 404:  # Not allowed access, either private or doesn't exist
        return {"error": f"Repository '{owner}/{repo}' not found or is private."}
    if status == 403:  # Most likely hit rate limit
        return {"error": "GitHub API rate limit exceeded."}
    if status != 200 or not repo_data:  # Catch-all for any other errors
        return {"error": f"GitHub API error (status {status}). Please try again later."}

    # F.2: CHECK FOR LICENSE
    has_license = repo_data.get("license") is not None
    license_name = repo_data["license"]["name"] if has_license else None

    # F.3: CHECK FOR README
    has_readme = check_file_exists(owner, repo, "README.md") or check_file_exists(
        owner, repo, "readme.md"
    )

    # F.4: CHECK FOR .GITIGNORE
    has_gitignore = check_file_exists(owner, repo, ".gitignore")

    # F.5: CHECK IF HAS RECENT COMMITS
    recent_commit, last_commit_date = check_recent_commit(owner, repo)

    # F.6: CHECK FOR GITHUB ACTIONS
    has_actions = check_github_actions(owner, repo)

    # F.7: COMPLILE CHECKS INTO LIST OF DICTIONARIES FOR FRONTEND
    checks = [
        {
            "id": "license",
            "label": "Has a LICENSE file",
            "passed": has_license,
            "detail": license_name,
        },
        {
            "id": "readme",
            "label": "Has a README.md file",
            "passed": has_readme,
            "detail": None,
        },
        {
            "id": "gitignore",
            "label": "Has a .gitignore file",
            "passed": has_gitignore,
            "detail": None,
        },
        {
            "id": "recent",
            "label": "Commit within the last 6 months",
            "passed": recent_commit,
            "detail": last_commit_date,
        },
        {
            "id": "actions",
            "label": "Uses GitHub Actions (.github/workflows/)",
            "passed": has_actions,
            "detail": None,
        },
    ]

    # F.8: CALCULATE SCORE
    score = sum(1 for c in checks if c["passed"])

    # F.9: RETURN DICT OF REPO DATA AND CHECK RESULTS FOR FRONTEND
    return {
        "owner": owner,
        "repo": repo,
        "full_name": repo_data.get("full_name"),
        "description": repo_data.get("description"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "html_url": repo_data.get("html_url"),
        "checks": checks,
        "score": score,
        "total": len(checks),
    }


# %%%%%%%%%%%%%%% W1: DEFINES BASIC/DEFAULT WEB APP ROUTE %%%%%%%%%%%%%%%
@app.route("/")
def index():
    return render_template("index.html")


# %%%%%%%%%%%%%%% W2: DEFINES WEB APP FUNCTIONALITY TO ANALYZE REPO AND DISPLAY %%%%%%%%%%%%%%%
@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Called by frontend to analyze a repo based on user input URL,
    displays JSON of results or error
    """

    body = (
        request.get_json(silent=True) or {}
    )  # Get JSON body from request, or use empty dict to avoid errors
    url = body.get("url", "").strip()  # Extract 'url' field from body, cleaning string

    if not url:
        return (
            jsonify({"error": "Please provide a repository URL."}),
            400,
        )  # Flags error if no URL provided

    result = analyze_repo(
        url
    )  # Main web app functionality, calling F: analyze_repo to run all checks and return results

    if (
        "error" in result
    ):  # If we get an error, pass it to frontend with 400 status code
        return jsonify(result), 400
    return jsonify(result)  # Otherwise, return regular results to frontend


# %%%%%%%%%%%%%%% W3: RUNS THE WEB APP %%%%%%%%%%%%%%%
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
