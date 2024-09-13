# GitHub Weekly Report Generator

## Overview

This project is a Python script that generates detailed weekly reports of GitHub activity for a specified user. It fetches information about commits, pull requests, and code reviews across multiple repositories and uses the Groq API to generate an insightful summary report.

## Features

- Fetches GitHub activity (commits, pull requests, code reviews) for a specified user and time range
- Processes multiple repositories concurrently for improved efficiency
- Generates a detailed Markdown report using the Groq API
- Customizable report template
- Saves the generated report as a Markdown file

## Prerequisites

- Python 3.7+
- GitHub API token
- Groq API key

## Dependencies

- PyGithub
- python-dotenv
- groq
- tqdm

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/github-weekly-report.git
   cd github-weekly-report
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with the following content:

   ```env
   GITHUB_TOKEN=your_github_token_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Create a `config.json` file in the project root directory with the following content:

   ```json
   {
     "github_username": "your_github_username",
     "repositories": [
       "owner/repo1",
       "owner/repo2",
       "owner/repo3"
     ]
   }
   ```

## Usage

Run the script using the following command:

```bash
python github_weekly_report.py
```

The script will generate a Markdown report file named `groq_detailed_weekly_report_<username>_<date>.md` in the project directory.

## Customization

You can customize the report template by modifying the `template/prompt_template.md` file. This template is used to generate the prompt for the Groq API, which then produces the final report.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
