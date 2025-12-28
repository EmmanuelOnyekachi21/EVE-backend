# EVE — Simple Project Objectives

> **"EVE helps people decide where and when to move safely by showing risk levels based on recent public information."**

---

## 🌎 What is EVE?
EVE is a tool designed to help people avoid dangerous places by visualizing the risk level of an area or route at a specific time.

### Key Features
- **Risk Assessment:** Produces risk levels (e.g., low, medium, high, or percentage).
- **Proactive Safety:** Useful *before* an incident occurs, helping you plan your movement.
- **Dynamic Analysis:** Shows how risky an area *looks* based on recent, aggregated information.
- **Universal Design:** Built for civilians moving around any city where data can be collected.

### What EVE is NOT
- ❌ An emergency response app or police system.
- ❌ A crime prediction system (it shows current/recent risk, not future predictions).
- ❌ A guarantee of safety.

---

## 🛡️ Risk Communication
EVE does not say "this place is dangerous." Instead, it provides context: 
> *"This place is riskier than usual at this time."*

To ensure accuracy, EVE follows a **confidence-through-consensus** model. It becomes confident in a risk level ONLY when multiple reports support each other, filtering out potentially wrong, fake, or exaggerated individual reports.

---

## 🚀 Getting Started (Docker Implementation)

This project uses Docker to ensure a consistent environment across different machines. Follow these steps to get a similar environment running locally.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd EVE-backend
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the root directory and populate it based on `.env.example`.
   ```bash
   cp .env.example .env
   ```

3. **Build and Start the Containers**
   This command builds the images and starts the database (PostGIS) and the web application.
   ```bash
   docker-compose up --build
   ```

4. **Initialize the Database**
   Run migrations to set up your database schema.
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Access the Application**
   The backend will be running at `http://localhost:8000`.

### Common Commands
- **Stop containers:** `docker-compose down`
- **View logs:** `docker-compose logs -f`
- **Run tests:** `docker-compose exec web python manage.py test`

---

## 🛠️ Technical Overview
- **Storage:** PostGIS (PostgreSQL) for spatial data handling.
- **Backend:** GeoDjango (Python 3.12).
- **Architecture:** Containerized via Docker for seamless deployment.

---

## 🧠 Decision Support
EVE helps users answer critical questions:
- *Should I go this way?*
- *Should I go later?*
- *Should I avoid this place?*
