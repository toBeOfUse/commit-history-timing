import requests
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter, defaultdict
import os
import pytz


def timestamp_to_eastern(timestamp):
    eastern_tz = pytz.timezone("US/Eastern")
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=pytz.UTC).astimezone(eastern_tz)
    return dt


def get_commits(repo_owner, repo_name, token):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {"Authorization": f"token {token}"}
    all_commits = []
    page = 1

    while True:
        response = requests.get(
            url, headers=headers, params={"page": page, "per_page": 100}
        )
        if response.status_code != 200:
            print(f"Failed to fetch commits: {response.status_code}")
            return []

        commits = response.json()
        if not commits:
            break

        all_commits.extend(commits)
        page += 1

    return all_commits


def extract_commit_info(commits):
    aliases = {
        "Christian Wierzbicki": "cwierzbicki00",
        "Mitch J.": "toBeOfUse",
        "Mitch J": "toBeOfUse",
        "emreedcodes": "EmReedCodes",
        "Emily Reed": "EmReedCodes",
        "Nicholas Llewellyn": "nllewellyn12",
        "Nick Llewellyn": "nllewellyn12",
        "Russel Heiser": "RHThree",
        "Ryan S": "ryan smith"
    }
    commit_hours = defaultdict(list)
    commit_dates = []
    for commit in commits:
        author = commit["commit"]["author"]["name"]
        author = aliases.get(author, author)
        timestamp = commit["commit"]["author"]["date"]
        dt = timestamp_to_eastern(timestamp)
        commit_hours[author].append(dt.hour)
        commit_dates.append(dt.date())
    return commit_hours, commit_dates


def plot_histogram(hours, filename, title):
    plt.figure(figsize=(16, 6))
    bottom = [0] * 24
    for author, counts in hours.items():
        counts_counter = Counter(counts)
        plt.bar(
            [f"{h}:00" for h in range(24)],
            [counts_counter[hour] for hour in range(24)],
            label=author,
            bottom=bottom,
        )
        for hour in range(24):
            bottom[hour] += counts_counter[hour]
    plt.xlabel("Hour of Day (US/Eastern)")
    plt.ylabel("Number of Commits")
    plt.title(title)
    plt.xticks(range(24))
    if len(hours) > 1:
        plt.legend(loc="upper right")
    plt.savefig(filename)
    plt.close()


def main():
    repo_owner = input("Enter the repository owner: ")
    repo_name = input("Enter the repository name: ")
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Please set the GITHUB_TOKEN environment variable.")
        return

    commits = get_commits(repo_owner, repo_name, token)
    if not commits:
        return

    commit_hours, commit_dates = extract_commit_info(commits)

    filename = f"commit_histogram_{repo_owner}_{repo_name}.png"
    title = f"{repo_owner}/{repo_name}\nCommits by Hour of the Day\n({min(commit_dates)} to {max(commit_dates)})"
    plot_histogram(commit_hours, filename, title)
    print(f"Histogram saved as '{filename}'")

    # Output additional statistics
    total_commits = len(commits)
    print(f"Total number of commits: {total_commits}")
    print(
        f"Date range of commits: {min(commit_dates)} to {max(commit_dates)} (US/Eastern)"
    )


if __name__ == "__main__":
    main()
