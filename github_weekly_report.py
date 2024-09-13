import os
import json
import re
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException
from collections import defaultdict
from dotenv import load_dotenv
import concurrent.futures
from groq import Groq
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# GitHub API token
github_token = os.getenv('GITHUB_TOKEN')
# Groq API key
groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize GitHub client
g = Github(github_token, per_page=100)  # Increase items per page for efficiency

# Initialize Groq client
groq_client = Groq(api_key=groq_api_key)

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_commit_details(commit):
    return {
        'sha': commit.sha,
        'message': commit.commit.message,
        'url': commit.html_url,
        'date': commit.commit.author.date,
    }

def extract_description_text(description):
    if not description:
        return ""
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', description)
    # Extract relevant text (up to 5 lines)
    lines = cleaned.split('\n')
    start_index = next((i for i, line in enumerate(lines) if "Description:" in line), 0) + 1
    relevant_lines = [line.strip() for line in lines[start_index:start_index+5] if line.strip() and not line.strip().endswith(':')]
    return ' '.join(relevant_lines)

def process_repo(repo_name, username, start_date, end_date):
    activity = defaultdict(list)
    try:
        repo = g.get_repo(repo_name)

        # Fetch commits
        commits = repo.get_commits(author=username, since=start_date, until=end_date)
        activity['commits'] = [get_commit_details(commit) for commit in commits]

        # Fetch pull requests
        prs = repo.get_pulls(state='all', sort='updated', direction='desc')
        for pr in prs:
            if pr.updated_at < start_date:
                break

            # Check if the PR is authored by the user
            if pr.user.login == username:
                # Check if the PR was created in the time frame or has new commits
                pr_commits = list(pr.get_commits())
                recent_commits = [get_commit_details(commit) for commit in pr_commits if start_date <= commit.commit.author.date <= end_date]

                if start_date <= pr.created_at <= end_date or recent_commits:
                    pr_details = {
                        'number': pr.number,
                        'title': pr.title,
                        'description': extract_description_text(pr.body),
                        'state': pr.state,
                        'url': pr.html_url,
                        'created_at': pr.created_at,
                        'updated_at': pr.updated_at,
                        'recent_commits': recent_commits
                    }
                    activity['pull_requests'].append(pr_details)

            # Check for reviews by the user
            reviews = pr.get_reviews()
            user_reviews = [review for review in reviews if review.user.login == username and
                            review.submitted_at and start_date <= review.submitted_at <= end_date]
            if user_reviews:
                activity['reviewed_pull_requests'].append({
                    'title': pr.title,
                    'url': pr.html_url
                })

    except GithubException as e:
        print(f"Error processing repository {repo_name}: {str(e)}")

    return repo_name, activity

def get_user_activity(username, start_date, end_date, repo_list):
    activity = defaultdict(lambda: defaultdict(list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_repo = {executor.submit(process_repo, repo_name, username, start_date, end_date): repo_name for repo_name in repo_list}

        for future in tqdm(concurrent.futures.as_completed(future_to_repo), total=len(repo_list), desc="Processing repositories"):
            repo_name = future_to_repo[future]
            try:
                repo_name, repo_activity = future.result()
                activity[repo_name] = repo_activity
            except Exception as exc:
                print(f'{repo_name} generated an exception: {exc}')

    return activity

def generate_groq_report(activity_data, username, start_date, end_date):
    total_commits = sum(len(repo_data['commits']) for repo_data in activity_data.values())
    total_prs = sum(len(repo_data['pull_requests']) for repo_data in activity_data.values())
    total_reviewed_prs = sum(len(repo_data['reviewed_pull_requests']) for repo_data in activity_data.values())

    pr_summaries = []
    for repo, data in activity_data.items():
        for pr in data['pull_requests']:
            commit_summaries = [f"<li><a href='{commit['url']}'>{commit['sha'][:7]}</a>: {commit['message'].split('\n')[0]}</li>" for commit in pr['recent_commits']]
            commit_summary = "<ul>" + "".join(commit_summaries) + "</ul>"
            pr_summary = f"""<li><a href="{pr['url']}">{pr['title']}</a> [#{pr['number']}]
                                <ul>
                                <li>Description: {pr['description']}</li>
                                <li>Status: {pr['state']}</li>
                                <li>Created: {pr['created_at'].date()}</li>
                                <li>Recent commits:{commit_summary}</li>
                                </ul>
                            </li>"""
            pr_summaries.append(pr_summary)

    reviewed_pr_summaries = [f"<li><a href='{pr['url']}'>{pr['title']}</a></li>" for repo_data in activity_data.values() for pr in repo_data['reviewed_pull_requests']]

    pr_summary_html = "<ul>" + "".join(pr_summaries) + "</ul>"
    reviewed_pr_summary_html = "<ul>" + "".join(reviewed_pr_summaries) + "</ul>"

    with open('template/prompt_template.html', 'r') as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        username=username,
        start_date=start_date.date(),
        end_date=end_date.date(),
        total_commits=total_commits,
        total_prs=total_prs,
        total_reviewed_prs=total_reviewed_prs,
        pr_summary_html=pr_summary_html,
        reviewed_pr_summary_html=reviewed_pr_summary_html
    )

    # Generate the report using Groq
    response = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # or another appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that generates insightful GitHub activity reports in HTML format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=5000  # Increased token limit for more detailed report
    )

    return response.choices[0].message.content

def main():
    config = load_config()
    username = config['github_username']
    repo_list = config['repositories']

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    print(f"Fetching GitHub activity for {username} from {start_date} to {end_date}")
    activity_data = get_user_activity(username, start_date, end_date, repo_list)

    print("Generating report using Groq...")
    report = generate_groq_report(activity_data, username, start_date, end_date)

    print(report)

    # Save the report to a file
    filename = f"groq_detailed_weekly_report_{username}_{end_date.date()}.html"
    with open(filename, "w") as f:
        f.write(report)
    print(f"Groq-generated detailed report saved to {filename}")

if __name__ == "__main__":
    main()