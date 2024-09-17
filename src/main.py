import asyncio
from src.ai.report_generation.client_manager import get_report_generation_client
from src.clients import CalendarClient, GitHubClient
from src.config.config import load_config, load_env_variables
from src.services import generate_ai_report, get_user_activity
from datetime import datetime, timedelta

async def main():
    env_vars = load_env_variables() # Load environment variables
    config = load_config() # Load configuration

    print(env_vars)

    username = config['github_username']
    repo_list = config['repositories']
    days_to_report = config.get('days_to_report', 7)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_to_report)

    # Initialize clients
    github_client = GitHubClient(env_vars['github_token'])
    calendar_client = CalendarClient()

    ai_config = {
        'provider': config['ai_provider'],
        'api_key': env_vars[f"{config['ai_provider']}_api_key"],
        'model_name': config.get('ai_model_name', 'gpt2')  # default to 'gpt2' for HuggingFace
    }
    report_generation_client = get_report_generation_client(ai_config)

    print(f"Fetching GitHub activity for {username} from {start_date} to {end_date}")
    activity_data = await get_user_activity(username, start_date, end_date, repo_list, github_client)

    print("Fetching calendar events")
    meetings = calendar_client.get_events(start_date.date(), end_date.date())

    print("Generating report using Groq...")
    report = generate_ai_report(activity_data, username, start_date, end_date, meetings, report_generation_client)

    filename = f"result/weekly_report_{username}_{end_date.date()}.html"
    with open(filename, "w") as f:
        f.write(report)
    print(f"Groq-generated detailed report saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())