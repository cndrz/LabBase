import spacy
from heapq import nlargest
import re
from datetime import datetime

nlp = spacy.load("en_core_web_sm")

def categorize_request(text):
    text_lower = text.lower()
    if "calibrate" in text_lower:
        return "Calibration"
    elif any(word in text_lower for word in ["maintain", "check", "clean", "routine"]):
        return "Preventive Maintenance"
    else:
        return "Uncategorized"

def summarize_text(text, max_sentences=2):
    doc = nlp(text)
    sentences = list(doc.sents)
    if len(sentences) <= max_sentences:
        return text
    word_freq = {}
    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        word = token.text.lower()
        word_freq[word] = word_freq.get(word, 0) + 1
    sentence_scores = {}
    for sent in sentences:
        for word in sent:
            if word.text.lower() in word_freq:
                sentence_scores[sent] = sentence_scores.get(sent, 0) + word_freq[word.text.lower()]
    best_sentences = nlargest(max_sentences, sentence_scores, key=sentence_scores.get)
    return " ".join(sent.text.strip() for sent in best_sentences)

def extract_keywords(text):
    doc = nlp(text)
    keywords = [chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip().split()) > 1]
    return list(set(keywords))

def detect_urgency(text):
    urgent_words = ["asap", "urgent", "immediately", "critical", "not working", "emergency", "high priority"]
    return "High" if any(word in text.lower() for word in urgent_words) else "Normal"

def extract_schedule(text):
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    if not dates:
        return None
    formatted_dates = []
    for date_str in dates:
        match = re.match(r"(January|February|March|April|May|June|July|August|September|October|November|December)\\s+(\\d{1,2})\\s*(?:–|-)?\\s*(\\d{1,2})?", date_str)
        if match:
            month, start_day, end_day = match.groups()
            year = datetime.now().year
            if end_day:
                formatted = f"{month} {start_day}, {year} to {month} {end_day}, {year}"
            else:
                formatted = f"{month} {start_day}, {year}"
            formatted_dates.append(formatted)
        else:
            formatted_dates.append(date_str)
    return ", ".join(formatted_dates)
