from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Tuple, Dict, List, Any
import pandas as pd

def build_vector_store(tabs_data: Dict[str, pd.DataFrame]) -> Tuple[List[str], TfidfVectorizer, Dict[int, str]]:
    """
    Flatten each tab's DataFrame into a document string and build a TF-IDF matrix.

    Returns:
        docs: List of strings (one per tab)
        vectorizer: Fitted TfidfVectorizer
        index_to_tab: Mapping from index to tab name
    """
    docs = []
    index_to_tab = {}
    for i, (tab_name, df) in enumerate(tabs_data.items()):
        if df.empty:
            continue
        text = df.astype(str).apply(lambda row: " | ".join(row), axis=1).str.cat(sep=" || ")
        doc = f"{tab_name} || {text}"
        docs.append(doc)
        index_to_tab[i] = tab_name

    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit(docs)
    return docs, vectorizer, index_to_tab


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def query_vector_store(query: str, docs: List[str], vectorizer: TfidfVectorizer, index_to_tab: Dict[int, str], top_n: int = 3) -> List[Tuple[str, str]]:
    """
    Returns top-n most similar documents (tab name + content) based on cosine similarity to the query.
    """
    if not docs:
        return []

    query_vec = vectorizer.transform([query])
    doc_vecs = vectorizer.transform(docs)
    similarities = cosine_similarity(query_vec, doc_vecs).flatten()
    top_indices = similarities.argsort()[::-1][:top_n]

    return [(index_to_tab[i], docs[i]) for i in top_indices]


def generate_answer_from_docs(matched_docs: List[Tuple[str, str]]) -> str:
    """
    Given a list of (tab_name, doc_text), generate a summarized answer.

    For now, returns a stub summary from the tab names.
    """
    if not matched_docs:
        return "No relevant information found in the uploaded data."

    response = "Here's a summary of what I found:\n\n"
    for tab_name, _ in matched_docs:
        response += f"• Relevant data found in **{tab_name}** tab\n"

    return response