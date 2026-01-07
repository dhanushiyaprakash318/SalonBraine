SalonBraine is an AI-powered business intelligence system for salon management software.

It allows users to ask:

"How many customers are there?"
"What is today's revenue?"
"Which service is most popular?"

And automatically:

Converts the question to SQL using LLaMA (via Ollama)

Validates the SQL (SELECT-only)

Executes it on MySQL

Generates:

📊 KPIs

📈 Charts

🧾 Human-readable English answers
-----------------------------------------------------------
Architecture

User Question (English)
        ↓
LLaMA (Text → SQL)
        ↓
SQL Validator (SELECT only)
        ↓
MySQL Database
        ↓
Query Result
        ↓
Analytics Engine
        ↓
English Answer Generator
        ↓
Web Dashboard (Charts + KPIs + Answer)
-----------------------------------------------------------
Features

✅ Natural language to SQL using LLaMA

✅ SQL injection protection (SELECT-only)

✅ Works on live MySQL database

✅ Auto KPI generation

✅ Auto chart generation

✅ English language answers

✅ No raw data exposed to AI model

✅ Web dashboard interface

✅ Perfect for internship / demo / BI system
-----------------------------------------------------------
Tech Stack

Backend: Python, FastAPI

Database: MySQL

AI Model: LLaMA 3.2 (Ollama)

Frontend: HTML, JavaScript, Chart.js

Server: Uvicorn
--------------------------------------------------------------
Backend : python -m uvicorn main:app --reload

Frontend : npm run dev

AI Model : LLaMA 3.2 (Ollama)    ollama serve