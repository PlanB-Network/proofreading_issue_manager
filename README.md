# Proofreading Issue Manager

A web-based tool to automate the creation of GitHub issues for the Bitcoin Educational Content proofreading process.

## Features

- **Course Issue Creation**: Automatically create proofreading issues for courses with proper formatting and project linking
- **Fuzzy Branch Search**: Easily find and select the correct GitHub branch
- **Automatic URL Generation**: Generates both PlanB Network and GitHub URLs
- **Project Integration**: Automatically links issues to the GitHub project board with proper field values
- **Multi-language Support**: Handles proofreading for multiple languages with appropriate URL generation

## Prerequisites

- Python 3.8+
- GitHub Personal Access Token with `repo` and `project` permissions
- Local clone of the [bitcoin-educational-content](https://github.com/PlanB-Network/bitcoin-educational-content) repository

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd proofreading-issue-manager
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file:
```bash
cp .env.example .env
```

5. Edit `.env` and add your configuration:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `BITCOIN_CONTENT_REPO_PATH`: Path to your local bitcoin-educational-content repository
   - `GITHUB_PROJECT_ID`: The project board ID (default is provided)

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Configure the application:
   - Click on "Configuration" 
   - Enter your local repository path
   - Enter your GitHub token
   - Set the default branch (usually "dev")

4. Create a course issue:
   - Click "Create Course Issue"
   - Select or type the course ID (e.g., btc101, csv402)
   - Choose the proofreading language
   - Select the GitHub branch (with fuzzy search)
   - Choose iteration (1st, 2nd, or 3rd proofreading)
   - Set urgency level
   - Preview the issue before creation
   - Click "Create Issue"

## Issue Format

### Title
`[PROOFREADING] {course_id} - [{language}]`

Example: `[PROOFREADING] csv402 - [fa]`

### Body
```
en PBN version: https://planb.network/en/courses/{course-title}-{uuid}
en github version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/courses/{course_id}/en.md
{lang} github version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/courses/{course_id}/{lang}.md
```

### Labels
- content - course
- content proofreading
- language - {language}

### Project Fields
- Status: "To Do"
- Language: Full language name
- Iteration: 1st/2nd/3rd
- Urgency: not urgent/urgent
- Content Type: "course"

## Configuration

### GitHub Token Permissions
Your GitHub token needs the following permissions:
- `repo` - Full control of private repositories
- `project` - Read and write access to projects

### Project Board
The tool is configured to work with the PlanB Network project board. The project ID is set in the configuration.

## Development

### Project Structure
```
proofreading-issue-manager/
├── .claude/spec/           # Specification files
├── static/                 # CSS and JavaScript files
├── templates/              # HTML templates
├── app.py                  # Main Flask application
├── config.py               # Configuration management
├── course_manager.py       # Course-specific logic
├── branch_selector.py      # GitHub branch search
├── github_integration.py   # GitHub API integration
└── requirements.txt        # Python dependencies
```

### Adding New Issue Types
To add support for tutorials or tutorial sections:
1. Create a new spec file in `.claude/spec/`
2. Add a new manager class (e.g., `tutorial_manager.py`)
3. Add routes in `app.py`
4. Create corresponding templates
5. Update the home page to enable the new type

## Troubleshooting

### Common Issues

1. **"Repository path not configured"**
   - Ensure you've set the correct path to your local bitcoin-educational-content repository
   - The path should contain a `courses` directory

2. **"Invalid GitHub token"**
   - Check that your token has the required permissions
   - Ensure the token hasn't expired

3. **"Course not found"**
   - Verify the course ID exists in your local repository
   - Check that the course has a `course.yml` file

4. **Branch not found**
   - The fuzzy search will help find similar branch names
   - Ensure you're connected to the internet for branch fetching

## Future Enhancements

- [ ] Tutorial issue creation
- [ ] Tutorial section issue creation
- [ ] Bulk issue creation
- [ ] Issue status tracking
- [ ] Dashboard for monitoring progress
- [ ] Automatic size evaluation based on content analysis

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]