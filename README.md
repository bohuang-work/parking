# Parking System

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.36.0-brightgreen?style=for-the-badge)

## Introduction

A Parking backend system, able to:

1. show free parking slots.
2. buy parking tickets and reserve parking slot.
3. cancle parking tickets.
4. pay parking tickets.

## Dependecies

RESTful-api implemented using Fast-API framework:

- FastAPI
- SQLite
- Pydantic
- SQLAlchemy
- Sqlmodel

## Run

- `docker build -t app .`
- `docker run -d -p 8000:8000 app`
