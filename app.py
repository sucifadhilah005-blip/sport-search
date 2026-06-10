from flask import Flask, request, render_template
import pickle
import string
import pandas as pd
import os
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

app = Flask(__name__)

# =========================
# PATH
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# LOAD DATA
# =========================

with open(os.path.join(BASE_DIR, "processed_paper.pkl"), "rb") as f:
    documents = pickle.load(f)

with open(os.path.join(BASE_DIR, "thesaurus.pkl"), "rb") as f:
    thesaurus = pickle.load(f)

df = pd.read_csv(
    os.path.join(BASE_DIR, "processed_paper.csv")
)

# =========================
# NLP TOOLS
# =========================

stopword = StopWordRemoverFactory().create_stop_word_remover()
stemmer = StemmerFactory().create_stemmer()

# =========================
# PREPROCESS
# =========================

def preprocess(text):

    text = text.lower()

    text = text.translate(
        str.maketrans('', '', string.punctuation)
    )

    text = stopword.remove(text)

    text = text.split()

    text = [
        stemmer.stem(word)
        for word in text
    ]

    return text

# =========================
# SEARCH ENGINE
# =========================

def search(query):

    # ----------------------
    # PREPROCESS QUERY
    # ----------------------

    query_words = preprocess(query)

    # ----------------------
    # QUERY EXPANSION
    # ----------------------

    synonym_lists = []

    for word in query_words:

        if word in thesaurus:

            synonym_lists.append(
                thesaurus[word]
            )

        else:

            synonym_lists.append(
                [word]
            )

    expanded_queries = []

    for combo in itertools.product(*synonym_lists):

        combo = [
            stemmer.stem(x)
            for x in combo
        ]

        expanded_queries.append(
            [" ".join(combo)]
        )

    # ----------------------
    # TF-IDF + COSINE
    # ----------------------

    vectorizer = TfidfVectorizer(use_idf=True)

    all_results = []

    for q in expanded_queries:

        tfidf = vectorizer.fit_transform(
            q + documents
        )

        query_vector = tfidf[0]

        similarity = cosine_similarity(
            tfidf,
            query_vector
        )

        temp_result = [

            [idx, score[0], q]

            for idx, score
            in enumerate(similarity)

            if score[0] > 0

        ]

        all_results += temp_result

    # ----------------------
    # SORTING
    # ----------------------

    all_results = sorted(

        all_results,

        key=lambda x: x[1],

        reverse=True

    )

    # ----------------------
    # TANPA DEDUPLIKASI
    # AGAR JUMLAH HASIL
    # SAMA DENGAN NOTEBOOK
    # ----------------------

    SIMILARITY_THRESHOLD = 0

    filtered_results = [

        item

        for item in all_results[1:]

        if item[1] >= SIMILARITY_THRESHOLD

    ]

    # ----------------------
    # FORMAT OUTPUT
    # ----------------------

    results = []

    for item in filtered_results:

        doc_idx = item[0] - 1

        if doc_idx < 0:
            continue

        results.append({

            "title":
                str(df.iloc[doc_idx]["Title"]),

            "content":
                str(df.iloc[doc_idx]["Content"])[:200],

            "url":
                str(df.iloc[doc_idx]["URL"]),

            "score":
                round(float(item[1]), 4)

        })

    return results

# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def result():

    if request.method == 'POST':
        query = request.form.get('query', '')
        page = 1
    else:
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))

    results = search(query)

    per_page = 5

    total_results = len(results)

    total_pages = (
        total_results + per_page - 1
    ) // per_page

    start = (page - 1) * per_page

    end = start + per_page

    paginated_results = results[start:end]

    return render_template(
        'result.html',
        query=query,
        results=paginated_results,
        current_page=page,
        total_pages=total_pages,
        total_results=total_results
    )

# =========================
# RUN APP
# =========================

if __name__ == '__main__':

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host='0.0.0.0',
        port=port
    )