# Judy Chatbot (Railway + Crawling Ready)

A Flask-based Retrieval-Augmented Generation (RAG) chatbot that:
✅ Crawls your website automatically  
✅ Embeds content into Chroma vector DB  
✅ Answers user questions using OpenAI GPT

## 🚀 Deploy on Railway
1. Push this repo to GitHub.
2. Go to https://railway.app and create a new project.
3. Connect your GitHub repo & deploy.
4. Add environment variable in Railway:
   - `OPENAI_API_KEY = your_openai_api_key`

## ✅ Test
POST to `/ask` with:
{
  "question": "What services does CSE Tech Solutions provide?"
}

The bot will answer based on your crawled website.
