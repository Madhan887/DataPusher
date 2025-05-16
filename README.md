# DataPusher API

A Django REST Framework project to manage accounts, destinations, and incoming data logs with token authentication.

## Features

- User registration and login with token authentication
- Manage accounts and assign roles (admin, normal)
- Add destinations per account
- Receive incoming data with headers, log, and dispatch to destinations
- View logs with filters and pagination

---

## API Endpoints

### Auth

- **POST /api/register/**  
  Register new user  
  Payload: `{ "username": "", "email": "", "password": "" }`  
  Auth: No

- **POST /api/login/**  
  Login user and get token  
  Payload: `{ "username": "", "password": "" }`  
  Auth: No

- **POST /api/logout/**  
  Logout user (invalidate token)  
  Auth: Yes

### Accounts

- **GET /api/accounts/**  
  List user’s accounts  
  Auth: Yes

- **POST /api/accounts/**  
  Create new account  
  Payload: `{ "name": "Account Name" }`  
  Auth: Yes

### Destinations

- **GET /api/destinations/**  
  List destinations  
  Auth: Yes

- **POST /api/destinations/**  
  Create new destination  
  Payload: `{ "name": "", "url": "", "http_method": "", "headers": {} }`  
  Auth: Yes

### Incoming Data Handler

- **POST /api/destinations/server/incoming_data/**  
  Receive incoming data, create logs  
  Required Headers: `CL-X-TOKEN`, `CL-X-EVENT-ID`  
  Payload: JSON body  
  Auth: Yes

### Logs

- **GET /api/logs/**  
  List logs with optional filters  
  Query Parameters: `destination_id`, `status`, `received_timestamp`, `processed_timestamp`  
  Auth: Yes

---

## Installation & Run

```bash
git clone <your-repo-url>
cd your-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
