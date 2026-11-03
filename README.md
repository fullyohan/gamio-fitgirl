
# Gamio - FitGirl Repack Addon

Addon for [Gamio](https://github.com/fullyohan/gamio), built with FastAPI.

This project scrapes game information from FitGirl Repacks, parses it and stores the results in a database. Gamio can then retrieve the data through the API.

## Features

- Scrapes FitGirl Repacks using BeautifulSoup.
- Extracts game titles, versions and file sizes.
- Provides endpoint for manual synchronization.

## Requirements

- Python 3.10+
- pip
- Git

## Installation

Clone the repository:

```bash
git https://github.com/fullyohan/gamio-fitgirl
cd gamio-fitgirl
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
URL =your_server_url
DB_URL=sqlite:///./database.db
SYNC_SECRET_TOKEN=your_secret_token
```

## Running

Start the server with Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

API documentation:

- `/docs` - Swagger
- `/redoc` - ReDoc

## Endpoints

### `GET /manifest.json`

Loads the extension manifest from a local JSON file and dynamically updates the icon URL using the current server host.

### `POST /sync`

Starts a data synchronization from FitGirl Repacks.

Requires an authorization token:

```http
Authorization: Bearer <SYNC_SECRET_TOKEN>
```

Example:

```bash
curl -X POST http://localhost:8000/sync \\
  -H "Authorization: Bearer your_secret_token"
```

Requests without a valid token are rejected.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- BeautifulSoup
- SQLModel
- python-dotenv