# Parking System

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3.36.0-brightgreen?style=for-the-badge)
![AWS](https://img.shields.io/badge/AWS-Cloud-brightgreen?style=for-the-badge)
![Terraform](https://img.shields.io/badge/Terraform-623CE4?style=for-the-badge&logo=terraform&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)

## Introduction

A Parking backend system, able to:

1. show free parking slots.
2. buy parking tickets and reserve parking slot.
3. cancle parking tickets.
4. pay parking tickets.

Can be deployed to EC2 or Lambda (serverless approach) on AWS.

## Dependecies

RESTful-api implemented using Fast-API framework:

- FastAPI
- SQLite
- Pydantic
- SQLAlchemy
- Sqlmodel
- AWS
- Terraform

## Run with Docker

- `docker build -t app .`
- `docker run -d -p 8000:8000 app`

## Run APP in AWS

#### EC2

1. `cd terraform/ec2/`
2. `terraform apply`
3. go to ec2 instance then run:

```shell
docker run -d --name parking-app -p 80:8000 \
-e DATABASE_ENV="aws" \
-e POSTGRES_USER="admin" \
-e POSTGRES_PASSWORD="adminAdmin123!" \
-e POSTGRES_HOST="parking-db.ch24acy4ksfc.eu-central-1.rds.amazonaws.com" \
-e POSTGRES_DB="parkingdb" \
bohuang910407/fastapi-parking:latest
```

#### Lambda (serverless approach)

1. `cd terraform/lambda`
2. `terraform apply`

## start grafana in local k8s

1. run helm install:
   `helm install -n monitoring prometheus prometheus-community/kube-prometheus-stack -f values.yaml`
2. port forward:
   `kubectl port-forward -n monitoring grafana-fcc55c57f-fhjfr 3000:3000`

<img src="https://github.com/bohuang-work/parking/blob/main/img/grafana.png" alt="Grafana Dashboard" width="600"/>
