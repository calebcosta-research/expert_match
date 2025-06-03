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

2. **Frontend**
   - `cd frontend`
   - Install Node dependencies with `npm install`
   - Start the development server with `npm start`
   - Build optimized static assets with `npm run build`

3. **Terraform**
   - `cd infra`
   - Initialize with `terraform init`
   - Review variables in `terraform.tfvars`
   - Deploy with `terraform apply`

## Environment Variables

No environment variables are required for the sample configuration. The
frontend scripts use the default Vite port `5173`. You may override this by
setting the `PORT` variable before running `npm start`.

This skeleton is meant as a starting point for implementing the full ExpertMatch platform. Consult the project specification for more details.
