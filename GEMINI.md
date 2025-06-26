# Gemini Workspace Guide: BlogCommerce

This document provides a comprehensive guide for developers to set up, run, and understand the BlogCommerce project.

## 1. Project Overview

BlogCommerce is a full-stack application combining a blog with an e-commerce platform.

- **Backend:** Built with Python, using the **FastAPI** framework for the API and **SQLAlchemy** for database interactions.
- **Frontend:** A modern single-page application (SPA) built with **Vue.js** and managed by **Vite**.
- **Database:** Supports PostgreSQL and MySQL, managed via Alembic for migrations.
- **Testing:** Utilizes `pytest` for the backend and `vitest` with `playwright` for the frontend.

## 2. Getting Started

### Prerequisites

- **Node.js:** v16 or higher
- **Python:** v3.8 or higher
- `pip` for Python package management
- `npm` for Node.js package management

### Installation

1.  **Backend Dependencies:**
    Install all required Python packages from the root directory.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Frontend Dependencies:**
    Navigate to the `frontend` directory and install the Node.js packages.
    ```bash
    cd frontend
    npm install
    cd ..
    ```

## 3. Development & Execution

### Running the Application

Use the `start_server.sh` script to launch the entire application.

```bash
./start_server.sh [PORT]
```

- **[PORT]** (Optional): Specify a port, defaults to `8001`.

**Script Actions:**
- **Builds Frontend:** Automatically builds the admin SPA.
- **Handles Port Conflicts:** Kills any process using the specified port.
- **Unified Service:** Serves all parts of the application under a single port.

### Running Tests

-   **Backend Tests:**
    Execute Python tests using `pytest`.
    ```bash
    python -m pytest
    ```
    *Alternatively, use the provided script:*
    ```bash
    ./run_tests.sh
    ```

-   **Frontend Tests:**
    Run unit and end-to-end tests from the `frontend` directory.
    ```bash
    cd frontend
    npm test
    ```
    *To run only end-to-end tests:*
    ```bash
    npm run test:e2e
    ```

## 4. Key Files & Directories

-   `app/`: Contains the core backend FastAPI application.
-   `app/main.py`: The main entry point for the backend server.
-   `app/database.py`: Database connection and session management.
-   `app/models/`: SQLAlchemy database models.
-   `app/routes/`: API route definitions.
-   `frontend/`: Contains the Vue.js frontend application.
-   `frontend/src/`: Main source code for the frontend.
-   `frontend/src/router/index.js`: Frontend routing configuration.
-   `frontend/src/stores/`: Pinia state management stores.
-   `requirements.txt`: Python package dependencies.
-   `frontend/package.json`: Node.js project dependencies and scripts.
-   `start.sh`: Main script for starting the application.
-   `run_tests.sh`: Script for running backend tests.
-   `GEMINI.md`: This guide.
