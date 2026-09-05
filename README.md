# XShip – Courier Management System

XShip is a web-based **Courier Management System** developed to simplify and manage courier and parcel operations through a centralized database.

The system provides features for parcel management, shipment tracking, delivery status management, payment management, and analytics through a user-friendly web interface.

---

## Features

- User authentication and login
- Role-based access for Admin, Staff, and Client
- Parcel booking and management
- Shipment tracking
- Delivery status updates
- Payment management
- Dashboard with statistics
- Analytics and reporting
- Centralized MySQL database
- Responsive web interface

---

## Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- MySQL
- MySQL Connector

### Development Tools

- Visual Studio Code
- XAMPP
- MySQL Workbench

---

## Project Structure

```text
xship-courier-management-system/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── add_parcel.html
│   ├── analytics.html
│   ├── base.html
│   ├── dashboard.html
│   ├── delivery.html
│   ├── login.html
│   ├── payments.html
│   ├── shipments.html
│   └── tracking.html
│
├── app.py
├── config.py
├── database.sql
├── requirements.txt
└── .gitignore
```

---

## System Modules

### Admin Module

The Admin can:

- Access the main dashboard
- Manage courier operations
- Manage parcels
- Monitor deliveries
- View payment information
- View analytics and statistics

### Staff Module

The Staff can:

- Manage parcels
- Add parcel information
- Update shipment status
- Manage delivery operations
- Track shipments

### Client Module

The Client can:

- Track parcels
- View shipment information
- Check delivery status
- View payment information

---

## Database

XShip uses **MySQL** as its relational database.

The database manages information related to:

- Users
- Parcels
- Payments

The database structure and sample data are provided in:

```text
database.sql
```

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ppraju7709/xship-courier-management-system.git
cd xship-courier-management-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 4. Install Required Packages

```bash
pip install -r requirements.txt
```

### 5. Start MySQL

Start **MySQL** using XAMPP.

Make sure the MySQL server is running before starting the Flask application.

### 6. Create the Database

Open **MySQL Workbench** or **phpMyAdmin**.

Create the XShip database and import the:

```text
database.sql
```

file.

### 7. Configure the Database

Update the MySQL connection details in `config.py` according to your local MySQL configuration.

### 8. Run the Application

```bash
python app.py
```

### 9. Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## Demo Login

The project contains fictional demo accounts for testing and demonstration purposes.

| User Type | Email | Password |
|-----------|-------|----------|
| Admin | admin@xship.com | admin123 |
| Staff | staff@xship.com | staff456 |
| Client | client@xship.com | client789 |

> **Note:** These are fictional accounts created only for project demonstration.

---

## Project Objective

The main objective of XShip is to reduce manual work involved in courier management by providing a centralized web-based system for:

- Parcel booking
- Shipment tracking
- Delivery management
- Status updates
- Payment management
- Data management
- Analytics

The system provides a structured way to store, retrieve, update, and manage courier-related information using a MySQL database.

---

## Application Workflow

```text
User
  │
  ▼
Login
  │
  ▼
Dashboard
  │
  ├── Parcel Management
  │
  ├── Shipment Tracking
  │
  ├── Delivery Management
  │
  ├── Payment Management
  │
  └── Analytics
          │
          ▼
     MySQL Database
```

---

## Screenshots

Screenshots of the application can be added here to demonstrate the user interface.

### Login Page

_Add screenshot here_

### Dashboard

_Add screenshot here_

### Parcel Management

_Add screenshot here_

### Shipment Tracking

_Add screenshot here_

### Analytics

_Add screenshot here_

---

## Future Enhancements

- Online payment gateway integration
- Email and SMS notifications
- Real-time GPS tracking
- Improved role-based access control
- Cloud deployment
- Secure password hashing
- Advanced analytics and reporting
- Automated delivery notifications

---

## Learning Outcomes

Through this project, we gained practical experience in:

- Python programming
- Flask web development
- HTML, CSS, and JavaScript
- MySQL database management
- Database design and CRUD operations
- Web application development
- Backend and frontend integration
- User authentication
- Project development and documentation

---

## Contributors

### Prajakta Patil

Computer Science Engineering

---

## Project Information

| Category | Details |
|----------|---------|
| Project Name | XShip – Courier Management System |
| Project Type | Web-Based Application |
| Backend | Python Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | MySQL |
| Development Environment | Visual Studio Code, XAMPP, MySQL Workbench |

---

## License

This project was developed for academic and educational purposes.
