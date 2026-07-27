# Deployment guide

1. Build the backend image
   - docker compose build
2. Start the stack
   - docker compose up -d
3. Apply the database schema
   - psql $DATABASE_URL -f backend/app/db/init.sql
4. Visit the API docs
   - http://localhost:8000/docs
5. Start the frontend
   - cd frontend && npm install && npm run dev
