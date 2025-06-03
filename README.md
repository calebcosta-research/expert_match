# ExpertMatch

ExpertMatch is a web platform that connects academic and industry experts with organizations seeking specialized skills. This repository contains a minimal starter implementation using Python + FastAPI for the backend, a placeholder React frontend, and Terraform configuration for AWS infrastructure.

## Repository Structure

- `backend/` – FastAPI application and server code
- `frontend/` – Placeholder for a React single page application
- `infra/` – Terraform templates for AWS resources

## Quickstart

1. **Backend**
   - `cd backend`
   - Install dependencies with `pip install -r requirements.txt`
   - Run the development server with `uvicorn app.main:app --reload`
   - Optionally set `DATABASE_URL` to override the default SQLite database

2. **Frontend**
   - `cd frontend`
   - Install Node dependencies with `npm install`
   - Start the development server with `npm start`

3. **Terraform**
   - `cd infra`
   - Initialize with `terraform init`
   - Review variables in `terraform.tfvars`
   - Deploy with `terraform apply`

4. **Testing**
   - Install backend dependencies
   - From the repository root, run `pytest`

This skeleton is meant as a starting point for implementing the full ExpertMatch platform. Consult the project specification for more details.
