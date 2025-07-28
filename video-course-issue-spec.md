# Video Course Issue Specification

## Overview
Video course issues are created for proofreading video transcripts of existing courses in the bitcoin-educational-content repository.

## Issue Format

### Title
```
[VIDEO-PROOFREADING] {course_id} - {language_code}
```

Example:
```
[VIDEO-PROOFREADING] btc101 - es
```

### Body
```
English PBN Version: https://planb.network/en/courses/{course_id}/{course-title-slug}-{uuid}
EN GitHub Version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/courses/{course_id}/en.md
{language} GitHub Version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/{branch}/courses/{course_id}/{language}.md
Workspace link shared privately
```

Example:
```
English PBN Version: https://planb.network/en/courses/btc101/bitcoin-what-is-it-97b8bac2-36c5-4bc5-8e5e-85ab61c61ed3
EN GitHub Version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/dev/courses/btc101/en.md
es GitHub Version: https://github.com/PlanB-Network/bitcoin-educational-content/blob/dev/courses/btc101/es.md
Workspace link shared privately
```

### Labels
- `content - course`
- `content proofreading`
- `language - {language_code}` (e.g., `language - es`)
- `video transcript`

### Project Fields
- **Status**: Todo
- **Language**: {language_code} (e.g., "es", "fr", "it")
- **Iteration**: 1st/2nd/3rd
- **Urgency**: not urgent/urgent
- **Content Type**: Video Course

## Key Differences from Regular Course Issues

1. **Title Prefix**: Uses `[VIDEO-PROOFREADING]` instead of `[PROOFREADING]`
2. **Additional Label**: Includes `video transcript` label
3. **Content Type**: Set to "Video Course" instead of "Course"
4. **Workspace Link**: Includes "Workspace link shared privately" text in the body (no input field needed)

## Implementation Notes

- Reuses the same course selection and language search functionality as regular course issues
- Course information is fetched from the existing course metadata
- The workspace link is not collected via form input but added as a standard text line in the issue body