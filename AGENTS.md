# Instructions for the AI Agents

This document provides instructions and guidelines for the AI agents working on this project.

Every agent MUST follow the rules and guidelines outlined in this document when performing their work.

## Initialization

You MUST run the next commands on the start of your work session:

- `donna -p llm -r <project-root> artifacts view '*:intro'` — to get an introduction to the project and its context.

## Resticted changes / operations

You ABSOLUTELY MUST NOT perform the following operations without explicit instructions to do so:

- Changing `docker-compose.yml` or any Docker-related configuration.
- Changing Docker runtime parameters (like allocated resources, volumes, etc.).
- Changing running Docker services related to other projects or unrelated to development environment.
- Installing any new dependencies, both for frontend and backend.
- Updating lock files.
- Installing any new tools, utilities, or software on the host machine or in the development containers.
- Changing project structure, such as moving files around, creating new directories, etc.

If you want to change something in the above list, you MUST ask for explicit instructions and permission to do so.

## Top priority tools

These tools MUST have the highest priority when an agent is deciding which tool to use for a given task:

### `ast-grep`

`ast-grep` — a tool for searching and manipulating Abstract Syntax Trees in code. Use it when you work with particular code patterns, structures, or constructs in the codebase.

You MUST use it to:

- Search for specific code patterns or structures in the codebase.
- Extract information from code, such as function definitions, variable declarations, or specific code constructs.
- Analyze code for specific patterns or anti-patterns, such as code smells, security vulnerabilities, performance issues, specific usage of libraries or APIs, etc.
- Refactor particular code patterns or structures across the codebase.
- Introduce new small behaviors or features into existing code.

You MUST NOT use it for:

- Implementing huge features or behaviors that require adding massive blocks of code (like adding a new class, module, writing a huge function, etc.).
