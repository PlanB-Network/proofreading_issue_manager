# Proofreading Issue Manager

A web-based tool to automate the creation of GitHub issues for the Bitcoin Educational Content proofreading process.

## Features

- **Course Issue Creation**: Automatically create proofreading issues for courses with proper formatting and project linking
- **Tutorial Issue Creation**: Create proofreading issues for individual tutorials with category-based organization
- **Tutorial Section Issue Creation**: Create proofreading issues for tutorial subfolders/sections
- **Weblate Issue Creation**: Create proofreading issues for website translations on Weblate
- **Video Course Issue Creation**: Create proofreading issues for video course transcripts
- **Image Course Issue Creation**: Create proofreading issues for course images
- **Fuzzy Search**: Smart search for courses, tutorials, and languages with intelligent matching
- **Fuzzy Branch Search**: Easily find and select the correct GitHub branch with context-aware suggestions
- **Automatic URL Generation**: Generates both PlanB Network and GitHub URLs
- **Project Integration**: Automatically links issues to the GitHub project board with proper field values
- **Multi-language Support**: Handles proofreading for multiple languages with appropriate URL generation

## Prerequisites

- Python 3.8+
- GitHub Personal Access Token with `repo` and `project` permissions
- Local clone of the [bitcoin-educational-content](https://github.com/PlanB-Network/bitcoin-educational-content) repository

## Installation

### Quick Install (Recommended)

1. Clone this repository:

```bash
git clone <repository-url>
cd proofreading-issue-manager
```

2. Make the script executable and run it:

```bash
chmod +x run_pim_app.sh
./run_pim_app.sh
```

That's it! The script will:

- Set up a virtual environment
- Install all dependencies
- Guide you through configuration (if needed)
- Start the application
- Open your browser automatically

On first run, you'll be prompted for:

- GitHub Personal Access Token (with 'repo' and 'project' permissions)
- Path to your bitcoin-educational-content repository
- Optional: Custom project ID and default branch

### Windows Installation

Simply double-click `run_pim_app.bat` or run it from Command Prompt:

```bash
run_pim_app.bat
```

## Usage

After installation, simply run:

```bash
./run_pim_app.sh  # Linux/macOS
```

or

```bash
run_pim_app.bat   # Windows
```

The application will start and open in your browser at `http://localhost:5000`

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
├── static/                 # CSS and JavaScript files
├── templates/              # HTML templates
├── app.py                  # Main Flask application
├── config.py               # Configuration management
├── course_manager.py       # Course-specific logic
├── tutorial_manager.py     # Tutorial-specific logic
├── branch_selector.py      # GitHub branch search
├── github_integration.py   # GitHub API integration
└── requirements.txt        # Python dependencies
```

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

## Issue Types

### Course Issues
Creates issues for course proofreading with:
- Title format: `[PROOFREADING] {course_id} - [{language}]`
- Labels: `content - course`, `content proofreading`, `language - {lang}`
- Project fields: Status, Language, Iteration, Urgency, Content Type

### Tutorial Issues
Creates issues for tutorial proofreading with:
- Title format: `[PROOFREADING] {category}/{name} - {language}`
- Labels: `content - tutorial`, `content proofreading`, `language - {lang}`
- Project fields: Status, Language, Iteration, Urgency, Content Type

### Tutorial Section Issues
Creates issues for tutorial section/subfolder proofreading with:
- Title format: `[PROOFREADING] {subfolder}_section - {language}`
- Labels: `content - tutorial`, `content proofreading`, `language - {lang}`
- Project fields: Status, Language, Iteration, Urgency, Content Type
- Supports nested folder structures within tutorials

### Weblate Issues
Creates issues for website translation proofreading with:
- Title format: `[PROOFREADING] weblate - {language}`
- Labels: `website translation`, `language - {lang}`
- Project fields: Status, Language, Iteration, Urgency, Content Type
- Automatic Weblate URL generation for the selected language

### Video Course Issues
Creates issues for video course transcript proofreading with:
- Title format: `[VIDEO-PROOFREADING] {course_id} - {language}`
- Labels: `content - course`, `content proofreading`, `language - {lang}`, `video transcript`
- Project fields: Status, Language, Iteration, Urgency, Content Type (Video Course)
- Includes "Workspace link shared privately" in issue body

### Image Course Issues
Creates issues for course image proofreading with:
- Title format: `[IMAGE-PROOFREADING] {course_id} - {language}`
- Labels: `content - course`, `content - images`, `language - {lang}`
- Project fields: Status, Language, Iteration, Urgency, Content Type (Image Course)
- Points to course assets folder on GitHub
- Includes "Workspace link shared privately" in issue body

## Future Enhancements

- [x] Course issue creation
- [x] Tutorial issue creation
- [x] Tutorial section issue creation
- [x] Weblate issue creation
- [x] Video course issue creation
- [x] Image course issue creation

## License

MIT License

Copyright (c) 2024 Proofreading Issue Manager Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
