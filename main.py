from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
import os, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from flask_cors import CORS
CORS(app)

app = Flask(__name__)

# ✅ API Key (set in Railway Dashboard > Variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ Please set the OPENAI_API_KEY environment variable in Railway.")

BASE_URL = "https://www.csetechsolution.com"  # Change this to any website you want

# ✅ Crawl website pages & extract text
def crawl_website(base_url, max_pages=10):
    visited = set()
    to_visit = [base_url]
    texts = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            res = requests.get(url, timeout=10)
            soup = BeautifulSoup(res.text, "html5lib")

            page_text = " ".join([p.get_text().strip() for p in soup.find_all(["p", "h1", "h2", "h3", "li"]) if p.get_text().strip()])
            if page_text:
                texts.append(Document(page_content=page_text))

            for link in soup.find_all("a", href=True):
                full_url = urljoin(base_url, link["href"])
                if base_url in full_url and full_url not in visited:
                    to_visit.append(full_url)

            visited.add(url)
        except Exception as e:
            print(f"⚠️ Failed to crawl {url}: {e}")
    return texts

# ✅ Crawl website or fallback
print("🌐 Crawling website...")
website_docs = crawl_website(BASE_URL, max_pages=8)
if not website_docs:
    print("⚠️ No website data found, using fallback docs...")
    website_docs = [
        Document(page_content="CSE Tech Solutions provides IT consulting, cloud, and AI services."),
        Document(page_content="Rose Tavern is a modern upscale hotel in Tema, Ghana.")
    ]

# ✅ Create Vector Store
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(website_docs)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = Chroma.from_documents(docs, embeddings)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
retriever = vectorstore.as_retriever()

@app.route("/")
def home():
    return "✅ Judy Chatbot (Crawling Enabled) is running!"

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "")
    if not user_question:
        return jsonify({"error": "Please provide a question"}), 400

    docs = retriever.get_relevant_documents(user_question)
    context = "\n".join([d.page_content for d in docs])

    if context:
        prompt = f"Answer based ONLY on this information:\n\n{context}\n\nQuestion: {user_question}\nAnswer:"
    else:
        prompt = f"If you don't know the answer, say politely you are not sure.\n\nQuestion: {user_question}\nAnswer:"

    response = llm.predict(prompt)
    return jsonify({"answer": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
