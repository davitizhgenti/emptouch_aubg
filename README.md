# Emptouch

A modern, modular Django client for the AUBG (American University in Bulgaria) Empower SIS.

## About The Project

The Empower Student Information System (SIS) used by AUBG is built on a ColdFusion framework (`fusebox.cfm`). While functional, its interface and architecture can be rigid.

**Emptouch** is a Django-based web application that acts as a client for the SIS. It provides a modern, responsive user interface and a robust, extensible backend. It communicates with the Empower SIS by replicating browser requests, parsing the resulting HTML, and presenting the data in a clean and user-friendly way.

The project is designed to be highly modular, allowing new features (like viewing grades, schedules, or registration) to be added as self-contained "pluggable apps."

## Features

-   **Secure Authentication:** User login is verified directly against the Empower SIS. Local Django user accounts are automatically created and updated.
-   **Resilient Session Management:** The client automatically handles session timeouts and re-authentication, providing a seamless user experience.
-   **Modern UI:** A clean, responsive interface built with Bootstrap 5 and `django-crispy-forms`.
-   **Modular Dashboard:** A dynamic dashboard that automatically discovers and displays "widgets" from any installed feature app.
-   **Advanced Networking:** The client can handle standard GET/POST navigation as well as complex two-step AJAX requests that require token scraping.
-   **Built-in SIS Explorer:** A powerful testing tool that allows developers to experiment with `fuseactions`, payloads, and AJAX endpoints to discover SIS functionality.

## Architectural Design

Emptouch uses a **service-oriented architecture**. The core logic for communicating with the external SIS is encapsulated within the `core` app, which provides a "client" service.

-   **`core/network.py` (`HttpClient`):** The low-level "engine." It manages the `requests.Session`, handles all HTTP/HTTPS communication, and contains the logic for authentication and session expiry detection.
-   **`core/client.py` (`EmpowerClient`):** The high-level "driver's cockpit." It provides a clean API (`.get()`, `.post()`, `.ajax_post()`) for the rest of the Django application to use, orchestrating the `HttpClient` and the parsing layer.
-   **Feature Apps (`testing`, `grades`, etc.):** These are self-contained Django apps that consume the `EmpowerClient` service. They define their own SIS endpoints, parsers, and dashboard widgets.

This separation ensures that changes to the Empower SIS website only require updates in the `core` app, leaving the feature apps untouched.

## Getting Started

Follow these steps to set up a local development environment.

### Prerequisites

-   Python 3.8+
-   `pip` and `venv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/davitizhgenti/emptouch_aubg.git
    cd emptouch
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Linux/macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Create a `requirements.txt` file:**
    If one doesn't exist, create it. These are the essential packages.
    ```
    Django
    requests
    beautifulsoup4
    django-crispy-forms
    crispy-bootstrap5
    ```

4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run database migrations:**
    This will create the necessary database tables for Django's user and session management.
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000`.

## How to Extend Emptouch (Creating a New Feature App)

The project is designed for easy extension. To add a new feature, like a "Grades" viewer:

1.  **Start a new app:**
    ```bash
    python manage.py startapp grades
    ```

2.  **Add it to `INSTALLED_APPS`** in `emptouch/settings.py`.

3.  **Define Endpoints and Parsers:**
    -   In `grades/endpoints.py`, define the `fuseaction` for the grades page.
    -   In `grades/parsers.py`, create a `GradesParser` that inherits from `core.parsers.BaseParser` and implements the logic to scrape grade data from the HTML.

4.  **Create a Dashboard Widget:**
    -   In `grades/widgets.py`, define a `fetch_grades_data(user)` function that uses the `EmpowerClient` to get the data.
    -   Create a template for the widget in `grades/templates/grades/grades_widget.html`.

5.  **Register the Widget:**
    In `grades/apps.py`, use the `ready()` method to register your widget with the `core` app's widget registry. This will make it appear on the dashboard automatically for users with the correct permissions.

## Roadmap

-   [ ] Implement a full-featured `grades`, `courses`, `students`  apps.
-   [ ] Create a `schedule` app to display the student's weekly schedule.
-   [ ] Develop a `registration` app to interact with course registration automatically (that one's most needed).
-   [ ] Add notifications for new grades or important dates.

## License

Distributed under the MIT License. See `LICENSE` for more information.
