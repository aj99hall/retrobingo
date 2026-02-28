# Retro Bingo Website Repository Guide

## Overview

This repository contains the source code for the **Retro Bingo web
application**.

The application currently includes:

-   A retro-themed landing page
-   A player details capture page
-   A game page
-   A structured questions dataset (`questions.json`)
-   Client-side state management using `localStorage` and
    `sessionStorage`

The project is designed to:

-   Run as a static site
-   Be containerised with Docker
-   Deploy to Render
-   Support future backend/API expansion if required

------------------------------------------------------------------------

# Repository Structure

    retro-bingo/
    │
    ├── app/
    │   ├── public/
    │   │   ├── index.html
    │   │   ├── details.html
    │   │   ├── game.html
    │   │   │
    │   │   ├── data/
    │   │   │   └── questions.json
    │   │   │
    │   │   ├── assets/
    │   │   │   ├── css/
    │   │   │   ├── js/
    │   │   │   │   ├── storage.js
    │   │   │   │   ├── game.js
    │   │   │   │   └── questions.js
    │   │   │   └── images/
    │   │   │
    │   │   └── favicon.ico
    │   │
    │   └── server/
    │
    ├── docker/
    │   └── nginx.conf
    │
    ├── Dockerfile
    ├── .dockerignore
    ├── render.yaml
    ├── .env.example
    ├── README.md
    └── .gitignore

------------------------------------------------------------------------

# Directory Responsibilities

## app/public/

Contains all static content served directly by Nginx:

-   HTML pages
-   CSS styles
-   JavaScript logic
-   Images and static assets
-   Game data (`data/questions.json`)

------------------------------------------------------------------------

## Data Storage Strategy

### Player Data

Stored in browser `localStorage`.

Example key:

    retroBingo.player

### Game State

Stored in `sessionStorage`.

Example key:

    retroBingo.game

### Questions Dataset

Located at:

    app/public/data/questions.json

Loaded using:

``` javascript
fetch("data/questions.json")
```

------------------------------------------------------------------------

# Local Development

## Build the container

    docker build -t retro-bingo .

## Run locally

    docker run --rm -p 8080:80 retro-bingo

Open:

    http://localhost:8080

------------------------------------------------------------------------

# Collaboration Workflow

## Branching Strategy

-   `main` → Production-ready
-   `feature/<name>` → New functionality
-   `fix/<issue>` → Bug fixes
-   `refactor/<area>` → Code improvements

------------------------------------------------------------------------

## Pull Request Process

1.  Create a feature branch.
2.  Keep changes focused and atomic.
3.  Open a Pull Request.
4.  Require at least one review.
5.  Merge only after approval and successful build.

------------------------------------------------------------------------

# Deployment to Render

1.  Push to GitHub.
2.  Render builds using Dockerfile.
3.  Static files served via Nginx.
4.  Deployment occurs automatically on successful build.

------------------------------------------------------------------------

# Future Expansion

The architecture supports:

-   Backend API integration
-   Persistent database storage
-   Admin UI for managing questions
-   Multiplayer support
-   Leaderboards
-   Authentication
-   Theming support
-   Sound effects and animations

------------------------------------------------------------------------

End of document.
