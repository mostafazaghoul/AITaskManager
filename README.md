# AI-Powered To-Do List API

A smart, extensible REST API for managing daily tasks — with AI-assisted task categorization, overdue task summaries, and smart scheduling suggestions. Built with Python, FastAPI, and the OpenAI API, this project demonstrates backend design, clean architecture, and the practical application of Large Language Models (LLMs) in a real-world service.

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Project Overview

This project was built to showcase a modern, production-ready backend service. It goes beyond a simple CRUD application by integrating AI to provide intelligent features that add real user value.

The primary goals were to:
1.  **Scalability:** Implementing a well-structured, scalable, and maintainable API using FastAPI.
2.  **Showcase Clean Architecture:** Separating concerns into distinct layers (routes, services, CRUD, models) for clarity and testability.
3.  **Highlight Practical AI Integration:** Using an LLM for core backend logic (categorization, planning) rather than just a chatbot interface.
4.  **Ensure Code Quality:** Writing unit tests with Pytest and mocking external services to ensure reliability.
5.  **Emphasize Deployability:** Containerizing the application with Docker for consistent and easy deployment.

---

## Key Features

-   **Full Task CRUD:** Standard Create, Read, Update, and Delete operations for tasks.
-   **AI-Powered Categorization:** Automatically categorizes tasks (e.g., `Work`, `Personal`, `Learning`) based on their title and description using the OpenAI API.
-   **Overdue Task Summary:** An endpoint to quickly retrieve all tasks that are past their due date and incomplete.
-   **Smart Daily Plan Generation:** A dedicated endpoint that uses GPT-4 to analyze your incomplete tasks and generate a prioritized, motivational daily schedule.
-   **Robust Unit Testing:** Comprehensive tests using Pytest, ensuring endpoints and services function as expected. Mocks are used for external API calls to keep tests fast and reliable.
-   **Dockerized Deployment:** Comes with a `Dockerfile` for easy, consistent, and isolated deployment.
-   **Interactive API Documentation:** Automatic, interactive API documentation powered by FastAPI via Swagger UI and ReDoc.

---

## Tech Stack

| Component        | Technology & Rationale                                       |
| ---------------- | ------------------------------------------------------------ |
| **Backend**      | **Python + FastAPI**: For high performance, async capabilities, and developer-friendly features like automatic docs. |
| **Database**     | **SQLite**: For simplicity in development and testing. The architecture allows for easy swapping to PostgreSQL in production. |
| **ORM**          | **SQLAlchemy**: The de-facto standard for robust, flexible interaction with SQL databases in Python. |
| **AI Integration** | **OpenAI API (GPT-3.5/GPT-4)**: To power the intelligent categorization and planning features. |
| **Data Validation**| **Pydantic**: Used by FastAPI for robust data validation, serialization, and settings management. |
| **Testing**      | **Pytest & `TestClient`**: For writing clean, scalable tests. `unittest.mock` is used to isolate external services. |
| **Deployment**   | **Docker**: For containerizing the application, ensuring a consistent environment from development to production. |

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.9+
-   Docker (optional, for containerized deployment)
-   An OpenAI API Key