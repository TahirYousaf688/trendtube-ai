# TrendTube AI architecture

## Overview
TrendTube AI is a cloud-native content factory for YouTube automation. It combines event-driven workflows, secure APIs, and scalable AI orchestration to discover topics, generate scripts, render media, and publish content with human review.

## Core components
- Frontend: Next.js + TypeScript + Tailwind + ShadCN UI
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Redis + Celery/RabbitMQ
- AI: LangGraph or CrewAI workflow orchestration with specialized agents
- Storage: AWS S3 for media assets, PostgreSQL for metadata, Chroma/Pinecone for embeddings
- Observability: Prometheus + Grafana + structured logs

## Deployment model
- Containerized services deployed on Docker/Kubernetes
- GitHub Actions for CI/CD and automated testing
- Managed secrets in Kubernetes secrets or AWS Secrets Manager
