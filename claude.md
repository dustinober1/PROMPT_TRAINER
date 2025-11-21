# Overview
I'm a product manager with limited coding experience who's looking to learn to become more technical. When you're coding and doing your work, please share tips that explain the tech architecture and any changes that you're making and why.

## Doc Rules
- All documents created must be put into the docs/ directory.
- Each document must have a clear and descriptive title.
- Use Markdown syntax for formatting.
- Include a table of contents for documents longer than 500 words.
- Use headings and subheadings to organize content.

## Product Backlog
- The product backlog is located at docs/backlog.md
- The product Plan is located at docs/project-plan.md

## Model
- For prompt building testing, we will use Qwen/Qwen3-0.6B model you can download from huggensface.
- For output testing, we will use the google/gemma-1.1-2b-it model you can download from huggensface.

## Database
- We will use a PostgreSQL database for storing user data and product information.
- The database schema will be designed to optimize for read and write performance.

## Git Management
- We will use Git for version control.
- The main branch will be protected, and all changes must go through a pull request.
- Use feature branches for new features and bug fixes.
- Commit messages should be clear and descriptive.
- Use .gitignore to exclude unnecessary files from the repository and large files.
- Push the changes after each iteration to ensure we can role back for any mistake.
