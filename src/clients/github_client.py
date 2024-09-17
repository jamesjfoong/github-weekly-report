from github import Github, Repository
from typing import List

class GitHubClient:
    def __init__(self, token):
        self.client = Github(token, per_page=100)

    def get_repo(self, repo_name: str) -> Repository:
        return self.client.get_repo(repo_name)

    def get_commits(self, repo: Repository, author: str, since: str, until: str) -> List:
        return repo.get_commits(author=author, since=since, until=until)

    def get_pull_requests(self, repo: Repository) -> List:
        return repo.get_pulls(state='all', sort='updated', direction='desc')