from typing import Dict, Any
from datetime import datetime
from typing import List
from src.ai.report_generation.base import ReportGenerationClient

def generate_ai_report(activity_data: Dict[str, Dict[str, Any]], username: str, start_date: datetime, end_date: datetime, meetings: List[Dict[str, str]], report_client: ReportGenerationClient) -> str:
    total_commits = sum(len(repo_data['commits']) for repo_data in activity_data.values())
    total_prs = sum(len(repo_data['pull_requests']) for repo_data in activity_data.values())
    total_reviewed_prs = sum(len(repo_data['reviewed_pull_requests']) for repo_data in activity_data.values())

    pr_summaries = []
    prs_to_review = []
    for repo, data in activity_data.items():
        for pr in data['pull_requests']:
            commit_summaries = []
            for commit in pr['recent_commits']:
                commit_message = commit['message'].replace('\n', '<br>')
                commit_summaries.append(f"<li><a href='{commit['url']}'>{commit['sha'][:7]}</a>: {commit_message}</li>")
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

        for pr in data['prs_to_review']:
            pr_summary = f"""<li><a href="{pr['url']}">{pr['title']}</a> [#{pr['number']}]
                            <ul>
                                <li>Repository: {repo}</li>
                                <li>Created by: {pr['user']}</li>
                                <li>Created at: {pr['created_at'].date()}</li>
                                </ul>
                            </li>"""
            prs_to_review.append(pr_summary)

    reviewed_pr_summaries = [f"<li><a href='{pr['url']}'>{pr['title']}</a></li>" for repo_data in activity_data.values() for pr in repo_data['reviewed_pull_requests']]

    meeting_summaries = []
    for meeting in meetings:
        meeting_summary = f"<li>{meeting['summary']}: from {meeting['start']} to {meeting['end']}</li>"
        meeting_summaries.append(meeting_summary)

    pr_summary_html = "<ul>" + "".join(pr_summaries) + "</ul>"
    reviewed_pr_summary_html = "<ul>" + "".join(reviewed_pr_summaries) + "</ul>"
    prs_to_review_html = "<ul>" + "".join(prs_to_review) + "</ul>"
    meetings_html = "<ul>" + "".join(meeting_summaries) + "</ul>"

    with open('templates/prompt_template.html', 'r') as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        username=username,
        start_date=start_date.date(),
        end_date=end_date.date(),
        total_commits=total_commits,
        total_prs=total_prs,
        total_reviewed_prs=total_reviewed_prs,
        pr_summary_html=pr_summary_html,
        reviewed_pr_summary_html=reviewed_pr_summary_html,
        prs_to_review_html=prs_to_review_html,
        meetings_html=meetings_html
    )

    # Generate the report using Groq
    return report_client.generate_report(prompt)