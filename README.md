# 1Now (One-now_rental) – Private Car Rental Platform

## Introduction

**1Now** is an all-in-one software platform that empowers car rental operators to run private rentals directly from their own branded websites—enabling renters to book without relying on third-party platforms like Turo. Designed with scalability and independence in mind, 1Now streamlines rental operations and maximizes revenue potential for car rental businesses of all sizes.

## Table of Contents

- [Features](#features)
- [Who It's For](#who-its-for)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Running the Server](#running-the-server)
- [License](#license)

## Features

1Now includes a suite of integrated tools to streamline every aspect of your car rental operation:

- 🚗 **Fleet Management**
- 📱 **Mobile App Integration**
- 📊 **Real-Time Analytics**
- 💰 **Financial Dashboards**
- 🛡️ **Liability Protection**
- 🚘 **Damage Coverage**

These features work together to help you:

- Eliminate third-party platform fees.
- Streamline day-to-day workflows.
- Build and strengthen direct customer relationships.

## Who It's For

1Now is ideal for:

- **Turo Hosts**  
  Reduce dependency on third-party platforms, avoid high commission fees, and take full ownership of your rental business.

- **Private Car Rental Businesses**  
  Especially those managing multi-car fleets who want a professional web presence and complete control over their bookings.

- **Companies Needing Full Operational Control**  
  Built for trust, transparency, and integrated protection for your assets and customers.

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/yourusername/car-rental-api.git
cd car-rental-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
