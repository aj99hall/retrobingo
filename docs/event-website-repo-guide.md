# Event Website Repository Guide

## Overview

This repository contains the source code and configuration for the event
website. It is designed to be containerised and deployed to Render using
Docker.

The structure supports: - A static holding page - Future expansion
(backend services, form handling, APIs) - Clean collaboration between
multiple contributors

------------------------------------------------------------------------

# Repository Structure

    event-website/
    │
    ├── app/                     # Application source
    │   ├── public/              # Static files served directly
    │   │   ├── index.html
    │   │   ├── assets/
    │   │   │   ├── css/
    │   │   │   ├── js/
    │   │   │   └── images/
    │   │   └── favicon.ico
    │   │
    │   └── server/              # Optional backend code (future use)
    │
    ├── docker/                  # Container-related configuration
    │   └── nginx.conf           # Optional custom Nginx config
    │
    ├── Dockerfile               # Defines container image
    ├── .dockerignore            # Prevents unnecessary files from entering image
    ├── render.yaml              # Optional Render deployment config
    ├── .env.example             # Template for environment variables
    ├── README.md                # Project overview and setup instructions
    └── .gitignore               # Git exclusions

------------------------------------------------------------------------

# Directory Responsibilities

## app/public/

Contains all static content served by Nginx.

Examples: - HTML pages - CSS stylesheets - JavaScript files - Images and
assets

This folder is copied into the container at build time.

## app/server/

Reserved for backend code if needed later (e.g., form handling, APIs).

## docker/

Stores container-specific configuration such as custom Nginx settings.

## Dockerfile

Defines how the container image is built.

## render.yaml

Optional infrastructure-as-code file for configuring deployment on
Render.

------------------------------------------------------------------------

# Local Development

## Build the container

    docker build -t event-website .

## Run locally

    docker run --rm -p 8080:80 event-website

Open: http://localhost:8080

------------------------------------------------------------------------

# Collaboration Workflow

## Branching Strategy

-   `main` → Production-ready code
-   `feature/<feature-name>` → New features
-   `fix/<description>` → Bug fixes

Examples: - feature/landing-layout - feature/email-signup -
fix/mobile-alignment

------------------------------------------------------------------------

## Pull Request Process

1.  Create a feature branch.
2.  Commit small, focused changes.
3.  Open a Pull Request (PR).
4.  Request at least one review before merging.
5.  Merge only after approval.

------------------------------------------------------------------------

## Commit Guidelines

-   Use clear, descriptive commit messages.
-   Keep commits atomic (one logical change per commit).
-   Avoid committing secrets or environment-specific values.

Example commit messages: - Add initial landing page layout - Improve
mobile responsiveness - Add email signup form placeholder

------------------------------------------------------------------------

# Deployment to Render

1.  Push changes to GitHub.
2.  Render automatically builds from the Dockerfile.
3.  On successful build, deployment is automatic.

Free tier note: Render free services may spin down after inactivity.

------------------------------------------------------------------------

# Environment Variables

If environment variables are required in the future: - Add them to
`.env.example` - Configure them in the Render dashboard - Never commit
real secrets to Git

------------------------------------------------------------------------

# Future Expansion

This structure supports: - Adding a backend service - Integrating
payment or ticketing - Implementing email capture and storage -
Splitting into multiple services if necessary

------------------------------------------------------------------------

# Ownership and Maintenance

All collaborators are responsible for: - Reviewing pull requests -
Keeping dependencies minimal - Maintaining a clean and readable codebase

------------------------------------------------------------------------

End of document.
