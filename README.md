# FastAPI Sales - README

## Overview

This is a FastAPI-based REST API for managing sales leads. It supports various CRUD operations (Create, Read, Update, Delete) for sales leads, along with advanced features such as sorting, filtering, pagination, and bulk delete. The API also allows exporting leads to a CSV file.

## Features

- **Create Leads**: Add new sales leads to the system.
- **Edit Leads**: Modify existing leads with updates.
- **List Leads**: View all sales leads with customizable pagination.
- **Delete Leads**: Remove leads from the system.
- **Multi-column Sorting**: Sort leads by multiple columns using `Ctrl` (Windows/Linux) or `Cmd` (Mac) for selecting more than one column.
- **Query-based Filtering**: Filter leads based on search criteria.
- **Bulk Deletion**: Select multiple leads for bulk deletion.
- **CSV Export**: Export your sales leads to a CSV file.

## Endpoints

For detailed API documentation, visit the live version of the app's API documentation:

- [FastAPI Sales API Documentation (PROD)](https://sales-leads-backend.onrender.com/docs)


## Installation Guide

### System Requirements

Before setting up the project, ensure that your system meets the following requirements:

- **Git**: Installed ([Download Git](https://git-scm.com/downloads))
- **Docker** (for Docker installation): Installed and running ([Download Docker](https://www.docker.com/get-started))
- **Python 3.8.10+** (for Virtualenv installation): Installed ([Download Python](https://www.python.org/downloads/))

## Installation Steps

### 1. Clone the Repository

```sh
git clone https://github.com/kfahad5607/sales-leads-backend.git
cd sales-leads-backend
```

## Installation Using Docker Compose

This method runs the entire application, including the FastAPI app, PostgreSQL database, and pgAdmin, using Docker.

### 2. Start the Application Using Docker Compose

Run the following command to start the FastAPI application along with the PostgreSQL database and pgAdmin:

```sh
docker-compose up --build
```

This command will:
- Build and start the FastAPI app container.
- Start a PostgreSQL database container.
- Start a pgAdmin container for database management.
- Automatically create the database and seed it with initial data.

### 3. Verify the Setup

Once the containers are up and running, verify the application:

- **FastAPI API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.
- **pgAdmin**: Open [http://localhost:5050](http://localhost:5050) and log in with:
  - **Email**: `admin@admin.com`
  - **Password**: `adminpassword`
  
  To access the database:
  - **Host**: `db`
  - **Username**: `postgres`
  - **Password**: `postgres`
  - **Database**: `salesdb`

### 4. Stopping the Application

To stop the running containers, press `Ctrl+C` or run:

```sh
docker-compose down
```

To remove all containers, volumes, and networks associated with this project:

```sh
docker-compose down -v
```

---

## Installation Using Virtualenv

This method sets up the FastAPI application in a Python virtual environment. PostgreSQL can be run locally or using Docker (without the app service).

### 2. Set Up Virtual Environment

Ensure you have Python **3.8.10+** installed. Then, create and activate a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example `.env` file and configure the necessary values:

```sh
cp .env.example .env
```

Modify `.env` as needed, ensuring correct database connection settings. If using Docker for PostgreSQL:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=salesdb
```

### 5. Start the PostgreSQL Database

If you don’t have PostgreSQL installed locally, start it using Docker:

```sh
docker-compose up -d postgres:17.2-alpine
```

### 6. Prepare the Database

Before running the app, make sure the database with the same name as in the `.env` file is created. Then, run the migrations:

```sh
alembic upgrade head
```

After the migration is successful, seed the database with initial data:

```sh
python3 -m seeds.leads
```

### 7. Run the FastAPI Application

```sh
python3 main.py
```

### 8. Verify the Setup

- **FastAPI API Documentation**: Open [http://localhost:8000/docs](http://localhost:8000/docs).