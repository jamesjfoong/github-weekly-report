import asyncio
from datetime import datetime
from tqdm import tqdm
from typing import Dict, List, Any
from aiohttp import ClientSession
from src.utils.helpers import clean_commit_message, extract_description_text
from src.clients import GitHubClient
from github.GithubException import GithubException

def get_commit_details(commit) -> Dict[str, Any]:
    return {
        'sha': commit.sha,
        'message': clean_commit_message(commit.commit.message),
        'url': commit.html_url,
        'date': commit.commit.author.date,
    }

async def get_user_activity(username: str, start_date: datetime, end_date: datetime, repo_list: List[str], github_client: GitHubClient) -> Dict[str, Dict[str, Any]]:
    activity = {}
    async with ClientSession() as session:
        tasks = [asyncio.create_task(process_repo(repo_name, username, start_date, end_date, session, github_client)) for repo_name in repo_list]
        for completed_task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing repositories"):
            repo_name, repo_activity = await completed_task
            activity[repo_name] = repo_activity
    return activity

async def process_repo(repo_name: str, username: str, start_date: datetime, end_date: datetime, session: ClientSession, github_client: GitHubClient) -> Dict[str, Any]:
    activity = {
        'commits': [],
        'pull_requests': [],
        'reviewed_pull_requests': [],
        'prs_to_review': []
    }
    try:
        repo = github_client.get_repo(repo_name)
        commits = repo.get_commits(author=username, since=start_date, until=end_date)
        activity['commits'] = [get_commit_details(commit) for commit in commits]

        prs = repo.get_pulls(state='all', sort='updated', direction='desc')
        for pr in prs:
            if pr.updated_at < start_date:
                break

            if pr.user.login == username:
                pr_commits = list(pr.get_commits())
                recent_commits = [get_commit_details(commit) for commit in pr_commits if start_date <= commit.commit.author.date <= end_date]

                if start_date <= pr.created_at <= end_date or recent_commits:
                    activity['pull_requests'].append({
                        'number': pr.number,
                        'title': pr.title,
                        'description': extract_description_text(pr.body),
                        'state': pr.state,
                        'url': pr.html_url,
                        'created_at': pr.created_at,
                        'updated_at': pr.updated_at,
                        'recent_commits': recent_commits
                    })

            reviews = pr.get_reviews()
            user_reviews = [review for review in reviews if review.user.login == username and
                            review.submitted_at and start_date <= review.submitted_at <= end_date]
            if user_reviews:
                activity['reviewed_pull_requests'].append({
                    'title': pr.title,
                    'url': pr.html_url
                })

            requested_reviewers = pr.get_review_requests()
            if any(reviewer.login == username for reviewer in requested_reviewers[0]):
                activity['prs_to_review'].append({
                    'title': pr.title,
                    'number': pr.number,
                    'url': pr.html_url,
                    'created_at': pr.created_at,
                    'user': pr.user.login
                })

    except GithubException as e:
        print(f"Error processing repository {repo_name}: {str(e)}")

    return repo_name, activity

