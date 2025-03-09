# Salesforce Clone - Django CRM

A Django-based CRM system inspired by Salesforce, providing essential features for managing customer relationships, sales opportunities, and tasks.

## Features

- Account Management
- Contact Management
- Lead Management
- Opportunity Tracking
- Task Management
- RESTful API
- Authentication & Authorization
- Search & Filtering
- Sorting & Pagination

## Tech Stack

- Django 5.1.7
- Django REST Framework 3.15.2
- PostgreSQL (recommended)
- Python 3.x

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd salesforce-clone
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your configuration:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

- `/api/accounts/` - Account management
- `/api/contacts/` - Contact management
- `/api/leads/` - Lead management
- `/api/opportunities/` - Opportunity management
- `/api/tasks/` - Task management

Each endpoint supports:
- GET (list & retrieve)
- POST (create)
- PUT/PATCH (update)
- DELETE (remove)

## Authentication

The API uses token-based authentication. To obtain a token:

1. Log in through the browsable API at `/api-auth/login/`
2. Use the token in your requests:
```
Authorization: Token your-token-here
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. # crm_test
