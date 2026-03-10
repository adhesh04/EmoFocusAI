EmoFocus AI
Adaptive Focus Monitoring and Reinforcement Learning Intervention System

Attention AI is an intelligent focus monitoring system that combines computer vision, emotion recognition, behavioral analytics, and contextual bandit reinforcement learning to detect attention levels during study sessions and deploy adaptive interventions that restore user focus.

The system analyzes real-time webcam input, estimates a user's focus score, detects emotional state, monitors digital distractions, and dynamically triggers cognitive reset activities such as puzzles, breathing exercises, and short games.

Unlike traditional productivity tools, Attention AI continuously learns which interventions work best for each user using a reinforcement learning policy model.

Project Overview

Maintaining sustained attention during study or work sessions is challenging due to distractions, cognitive fatigue, and digital multitasking.

Most productivity tools rely on timers or manual self-reporting, which do not reflect real cognitive states.

Attention AI addresses this problem by integrating:

• Real-time computer vision attention monitoring
• Emotion recognition using facial analysis
• Behavioral distraction detection
• Reinforcement learning based intervention selection
• Cognitive micro-interventions to restore focus

The system operates continuously during study sessions and adapts intervention strategies based on user responses.

Key Features
Real-Time Focus Monitoring

Attention AI uses webcam input to analyze user attention levels during a study session.

Facial features are extracted using MediaPipe Face Mesh, which provides detailed facial landmark tracking.

The system analyzes signals such as:

Eye gaze direction

Eye openness and blinking patterns

Head pose orientation

Facial landmark stability

These signals are processed to estimate a continuous focus score representing the user's current attention level.

Technologies used:

MediaPipe Face Mesh

OpenCV

Python

Emotion Recognition with DeepFace

The system performs facial emotion recognition using DeepFace, a deep learning based facial analysis library.

DeepFace analyzes facial expressions and can detect multiple emotional states including:

Happy

Sad

Angry

Fear

Surprise

Disgust

Neutral

These emotional signals are integrated into the system’s focus estimation pipeline.

For example:

Negative or stressed emotional states may reduce the focus score

Neutral or attentive expressions contribute to stable focus estimation

Emotion detection therefore provides an additional behavioral signal that improves attention estimation accuracy.

Technologies used:

DeepFace

OpenCV

Focus Score Estimation

Attention AI computes a real-time focus score using multiple behavioral signals.

Inputs include:

• Eye gaze stability
• Facial orientation and posture
• Blink behavior
• Emotion detection from DeepFace
• Digital distraction indicators

These features are combined to generate a dynamic attention score during a study session.

This score determines when an intervention should be triggered.

Digital Distraction Detection

To detect behavioral distractions beyond facial signals, the system tracks browser tab switching behavior.

Frequent tab switching may indicate:

Loss of attention

Multitasking

External distraction

Tab switching events are logged and influence the focus estimation model.

This allows the system to detect both visual attention loss and behavioral distraction patterns.

Contextual Bandit Reinforcement Learning Intervention Engine

One of the core innovations of Attention AI is its contextual bandit reinforcement learning system for selecting interventions.

Instead of using fixed rules to trigger the same activity every time focus drops, the system learns which intervention is most effective.

Intervention Decision Model

The system uses a deep policy network implemented in PyTorch.

The model operates as a contextual bandit, where:

State (context) includes:

Current focus score

Emotion signal

Session progress

Recent distraction patterns

Action space includes different intervention types.

Examples:

Breathing exercise

Cognitive puzzle

Memory game

Motivational prompt

After an intervention is triggered, the system observes whether the focus score improves.

This improvement acts as the reward signal.

Over time, the model learns which interventions are most effective for restoring focus.

Technologies used:

PyTorch

Contextual bandit reinforcement learning

Deep policy network

Intervention System

When the user's focus score drops below a predefined threshold, the system automatically deploys a micro-intervention designed to restore attention.

The following interventions are implemented:

Breathing Exercise

A short guided breathing routine that helps reduce mental fatigue and reset attention.

Quick Joke

A humorous prompt that provides a brief cognitive reset.

Brain Teaser

A small logical puzzle designed to stimulate cognitive engagement.

Motivation Boost

Short motivational messages encouraging users to regain focus.

Sliding Puzzle Game

A 4x4 sliding tile puzzle that requires logical thinking and problem solving.

This engages spatial reasoning and attention control.

Memory Sequence Game

A memory challenge where users must observe and repeat a sequence of highlighted tiles.

The sequence length increases progressively, encouraging sustained attention.

Mini Sudoku

A simplified 4x4 Sudoku puzzle where users fill missing numbers while satisfying Sudoku constraints.

This activity engages analytical thinking and concentration.

Focus Booster Mode

Apart from automatic AI-triggered interventions, the system also includes a manual Focus Boosters interface.

Users can voluntarily start cognitive refresh activities without waiting for automatic intervention.

Available boosters include:

Breathing Exercise

Quick Joke

Brain Teaser

Motivation Boost

Sliding Puzzle

Memory Sequence

Mini Sudoku

This provides flexibility for users to reset focus whenever needed.

Reflective Journal with AI Analysis

The system includes a journaling feature where users can reflect on their study sessions.

Journal entries are analyzed using a local large language model via Ollama.

The system extracts:

Dominant emotion

Stress score

Cognitive state

One sentence summary

This helps users understand their learning patterns and mental state across sessions.

Technologies used:

Ollama

Llama3

Analytics Dashboard

The dashboard provides insights into attention trends across study sessions.

Displayed metrics include:

Total study sessions

Average focus score

Number of interventions triggered

Peak focus time

The system also displays reinforcement learning metrics such as:

Intervention accuracy

Policy confidence

Reward signal strength

These metrics illustrate how the RL system adapts intervention strategies.

System Architecture

The project follows a modular architecture separating machine learning models, backend APIs, and frontend interfaces.

Backend

Framework:

FastAPI

Responsibilities:

User authentication

Session management

Focus score logging

Emotion tracking

Intervention decisions

Journal analysis

Analytics reporting

Database

PostgreSQL is used to store:

User information

Study sessions

Focus score history

Intervention logs

Journal entries

SQLAlchemy ORM is used for database interaction.

Machine Learning Components

Computer Vision

MediaPipe Face Mesh

OpenCV

Emotion Recognition

DeepFace

Reinforcement Learning

PyTorch

Contextual bandit policy network

NLP

Ollama

Llama3

Frontend

Frontend interfaces are implemented using:

HTML

CSS

JavaScript

Main UI modules include:

Login Interface

Dashboard

Live Monitoring Page

Journal Page

Focus Boosters Interface

Intervention Interface

Project Structure
emofocus-ai/
│
├── app/
│
│   ├── main.py
│
│   ├── api/
│   │   └── v1/
│   │        ├── auth.py
│   │        ├── sessions.py
│   │        ├── focus.py
│   │        ├── emotion.py
│   │        ├── journal.py
│   │        ├── decision.py
│   │        └── analytics.py
│
│   ├── core/
│   │        ├── config.py
│   │        ├── security.py
│   │        └── dependencies.py
│
│   ├── db/
│   │        ├── base.py
│   │        └── session.py
│
│   ├── models/
│   │        ├── user.py
│   │        ├── session.py
│   │        ├── focus_log.py
│   │        ├── emotion_log.py
│   │        ├── intervention.py
│   │        └── journal.py
│
│   ├── schemas/
│   │        ├── user.py
│   │        ├── auth.py
│   │        ├── session.py
│   │        ├── focus.py
│   │        ├── emotion.py
│   │        ├── intervention.py
│   │        ├── journal.py
│   │        └── analytics.py
│
│   ├── services/
│   │        ├── focus_service.py
│   │        ├── deep_policy_bandit.py
│   │        ├── intervention_bandit.py
│   │        └── journal_service.py
│
│   ├── static/
│   │        ├── login.html
│   │        ├── dashboard.html
│   │        ├── monitor.html
│   │        ├── analytics.html
│   │        ├── journal.html
│   │        ├── focus_boosters.html
│   │        └── intervention.html
│
├── policy_model.pth
│
├── requirements.txt
│
├── Dockerfile
│
└── README.md
Technologies Used

Backend

FastAPI

Python

SQLAlchemy

PostgreSQL

Machine Learning

PyTorch

MediaPipe

OpenCV

DeepFace

NLP

Ollama

Llama3

Frontend

HTML

CSS

JavaScript

Running the Project

Clone repository

git clone https://github.com/your-username/attention-ai.git
cd attention-ai

Install dependencies

pip install -r requirements.txt

Run Ollama for journal analysis

ollama run llama3

Start backend server

uvicorn app.main:app --reload

Open application

http://127.0.0.1:8000
Future Improvements

Possible extensions include:

Advanced emotion classification models

Larger cognitive game library

Personalized long-term focus modeling

Mobile application support

Adaptive difficulty interventions

Cross-user policy learning

License

This project is developed for academic and research purposes.

Cloud Deployment and Infrastructure
Supabase PostgreSQL Integration

The system uses Supabase PostgreSQL as a managed cloud database to persist all application data. Supabase provides a fully hosted PostgreSQL database with built-in authentication, APIs, and monitoring tools.

All user session information and behavioral signals are stored in Supabase, allowing the AI system to analyze attention patterns across multiple study sessions.

Data Stored in Supabase

The following entities are stored in the database:

User Data

User profile information

Authentication metadata (local development)

Session Data

Study session metadata

Session start and end times

Focus Logs

Continuous focus score values

Timestamped focus measurements

Emotion Logs

Detected emotional state

Confidence scores

Timestamped emotion observations

Intervention Logs

Intervention type triggered

Reinforcement learning policy confidence

Reward signal (focus improvement)

Journal Entries

User reflective notes

AI-generated emotional analysis

Stress score and cognitive state

The backend interacts with Supabase using:

SQLAlchemy ORM
psycopg2 PostgreSQL driver

Database schema creation is handled automatically during backend initialization.

Containerization with Docker

To enable portable deployment, the backend application was containerized using Docker.

Containerization ensures the system can run consistently across different environments including:

Local development

Cloud infrastructure

Container orchestration platforms

Docker Optimization

Initial builds produced extremely large images due to machine learning dependencies.

Key optimizations were applied:

Multi-Stage Docker Builds

Dependencies are installed in a builder stage and only the required runtime libraries are copied into the final container.

CPU-Only PyTorch Installation

GPU libraries were removed to reduce container size.

Minimal Python Base Image

python:3.10-slim

was used instead of the full Python image.

Image Size Reduction
Stage	Image Size
Initial Docker build	~10.8 GB
After dependency optimization	~1.9 GB
Final optimized container	~480–500 MB

This reduction made the system suitable for deployment on lightweight cloud infrastructure.

Docker Hub Image Distribution

After building the container locally, the image was published to Docker Hub.

Docker Hub acts as a public container registry from which cloud platforms can pull the application image.

Image Repository
adhi044/emofocusai
Build and Push Process

Build the Docker image:

docker build -t adhi044/emofocusai:latest .

Push to Docker Hub:

docker push adhi044/emofocusai:latest

Publishing the container enables automated cloud deployment workflows.

Azure Cloud Deployment

The backend system is deployed using Microsoft Azure Container Instances (ACI).

Azure Container Instances allow running Docker containers without managing servers or Kubernetes clusters.

This approach enables fast deployment while keeping infrastructure simple for demonstration and academic purposes.

Azure Deployment Workflow

The deployment process involved several steps:

1. Azure CLI Authentication
az login

The Azure CLI was used to manage cloud resources directly from the terminal.

2. Resource Group Creation

Azure resources are organized using resource groups.

az group create \
--name emofocus-rg-sea \
--location southeastasia
3. Container Deployment

The container image hosted on Docker Hub is deployed as a container instance.

az container create \
--resource-group emofocus-rg-sea \
--name emofocus-ai \
--image adhi044/emofocusai:latest \
--os-type Linux \
--cpu 2 \
--memory 4 \
--ports 8000 \
--dns-name-label emofocus-ai-demo \
--location southeastasia
4. Public API Endpoint

After deployment, Azure provides a public endpoint:

http://emofocus-ai-demo.southeastasia.azurecontainer.io:8000

This endpoint exposes the FastAPI backend publicly.

Swagger documentation can be accessed at:

http://emofocus-ai-demo.southeastasia.azurecontainer.io:8000/docs
Cloud Architecture Overview

The complete system architecture now includes multiple cloud components.

User Browser
      │
      ▼
Azure Container Instance
(FastAPI Backend)
      │
      ▼
Supabase PostgreSQL
(Database)
Responsibilities

Azure Container Instance

Runs the backend API and machine learning logic.

Supabase PostgreSQL

Stores behavioral logs, sessions, and analytics data.

Docker Hub

Hosts the deployable container image.

Infrastructure Challenges and Solutions

During deployment several technical challenges were encountered and resolved.

Large Docker Image Problem

Machine learning libraries such as PyTorch and MediaPipe significantly increased container size.

Solution

Multi-stage Docker builds and CPU-only ML dependencies reduced image size by over 95%.

Docker Push Failures

Large image layers caused repeated push failures.

Solution

Optimizing the container reduced layer sizes and enabled successful uploads.

Azure Region Restrictions

Azure Student subscriptions restrict resource creation to specific regions.

Allowed regions included:

southeastasia
eastasia
austriaeast
koreacentral
malaysiawest

Deployments outside these regions were blocked by Azure policies.

Container Startup Failures

Early deployments failed due to missing Python dependencies inside the container.

Solution

Dockerfile was updated to install all dependencies from requirements.txt.

Final Deployment Status

The Attention AI backend can now be deployed as a cloud-hosted AI service.

Capabilities of the deployed system include:

Real-time attention monitoring

Emotion recognition

Reinforcement learning intervention engine

Session analytics dashboard

Journal reflection analysis

Cloud-hosted API infrastructure

Summary

The final system demonstrates a complete end-to-end AI application pipeline:

Computer Vision
Emotion Recognition
Reinforcement Learning
Backend API
Database Storage
Cloud Deployment

By integrating machine learning, behavioral analytics, and cloud infrastructure, Attention AI becomes a scalable intelligent productivity system capable of adapting interventions based on user attention dynamics.
