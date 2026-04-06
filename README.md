# Thulaganyo's Chatbot / YT Summarizer

A personal YouTube transcript downloader, summarizer, and AI chat app built with PyQt6 and Ollama.

## Requirements
- Python 3.10+
- Ollama

## Installation

### Step 1: Install Ollama
Download and install from https://ollama.com

### Step 2: Pull the AI models
Open terminal and run these one by one:

ollama pull dolphin-llama3
ollama pull llava

Note: dolphin-llama3 is 4.7GB and llava is 4.5GB so make sure you have enough storage and a decent PC with at least 16GB RAM to run both smoothly. If you only have 8GB RAM, replace dolphin-llama3 with tinydolphin:

ollama pull tinydolphin

And change the model name in app.py from dolphin-llama3:latest to tinydolphin:latest

### Step 3: Install Python dependencies
py -m pip install PyQt6 markdown youtube-transcript-api openai

### Step 4: Make sure Ollama is running
ollama serve

### Step 5: Run the app
py app.py

## Features
- Download YouTube transcripts
- Summarize videos with AI
- Upload and analyze images
- Chat with Beans (your personal AI)
- Load transcripts into chat to ask questions

## Notes
- Make sure Ollama is running in the background before launching the app
- You need a CSS file named cool.css in the same folder (included in repo)
- Do not close the Ollama terminal while using the app
## HEAVILY INSPIRED BY Jie Jehn "Create Your Own YouTube AI Summarizer (& Transcript Downloader) Using Python and PyQt6"
