<<<<<<< HEAD
from flask import Flask, request, render_template
import pickle
import string
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

app = Flask(__name__)

# =========================
# PATH AMAN (PENTING)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# load data
with open(os.path.join(BASE_DIR, "model/processed_paper.pkl"), "rb") as f:
    documents = pickle.load(f)

with open(os.path.join(BASE_DIR, "model/thesaurus.pkl"), "rb") as f:
    thesaurus = pickle.load(f)

df = pd.read_csv(os.path.join(BASE_DIR, "model/processed_paper.csv"))

# tools
stopword = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = stopword.remove(text)
    text = text.split()
    text = [stemmer.stem(x) for x in text]
    return text

def expand_query(words):
    expanded = []
    for w in words:
        if w in thesaurus:
            expanded += thesaurus[w]
        else:
            expanded.append(w)
    return list(set(expanded))

def search(query):
    words = preprocess(query)
    expanded = expand_query(words)

    final_query = " ".join(expanded)

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([final_query] + documents)

    similarity = cosine_similarity(tfidf[0:1], tfidf[1:])
    scores = similarity.flatten()

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    results = []

    for idx, score in ranked[:10]:
        results.append({
            "title": df.iloc[idx]["Title"],
            "content": df.iloc[idx]["Content"][:200],
            "url": df.iloc[idx]["URL"],
            "score": float(score)
        })

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def result():
    query = request.form.get('query', '')
    results = search(query)
    return render_template('result.html', query=query, results=results)

# =========================
# WAJIB UNTUK RAILWAY
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
=======
from flask import Flask, request, render_template
import pickle
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

app = Flask(__name__)

# load data
with open("processed_paper.pkl", "rb") as f:
    documents = pickle.load(f)

with open("thesaurus.pkl", "rb") as f:
    thesaurus = pickle.load(f)

df = pd.read_csv("processed_paper.csv")

# tools
stopword = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = stopword.remove(text)
    text = text.split()
    text = [stemmer.stem(x) for x in text]
    return text

def expand_query(words):
    expanded = []
    for w in words:
        if w in thesaurus:
            expanded += thesaurus[w]
        else:
            expanded.append(w)
    return list(set(expanded))

def search(query):
    words = preprocess(query)
    expanded = expand_query(words)

    final_query = " ".join(expanded)

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([final_query] + documents)

    similarity = cosine_similarity(tfidf[0:1], tfidf[1:])
    scores = similarity.flatten()

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    results = []

    for idx, score in ranked[:10]:
        results.append({
            "title": df.iloc[idx]["Title"],
            "content": df.iloc[idx]["Content"][:200],
            "url": df.iloc[idx]["URL"],
            "score": float(score)
        })

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def result():
    query = request.form.get('query', '')
    results = search(query)
    return render_template('result.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> c6d4d0ccccecc82aaba4307ae9c5bb84e08b0006
