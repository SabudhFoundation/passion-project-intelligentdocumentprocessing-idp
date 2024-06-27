from flask import Flask, request, render_template
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from collections import defaultdict
import re
import heapq

from transformers import BartTokenizer, BartForConditionalGeneration

# Initialize Flask app
app = Flask(__name__)

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load BART model and tokenizer
model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

# Function for TextRank summarization
def calculate_similarity(s1, s2):
    s1 = set(s1)
    s2 = set(s2)
    overlap = len(s1.intersection(s2))
    return overlap / (len(s1) + len(s2))

def summarize_text_rank(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = [word_tokenize(sentence.lower()) for sentence in sentences]
    stop_words = set(stopwords.words('english') + list(punctuation))
    filtered_words = [[word for word in sentence if word not in stop_words] for sentence in words]
    word_freq = defaultdict(int)
    for sentence in filtered_words:
        for word in sentence:
            word_freq[word] += 1
    sentence_scores = defaultdict(int)
    for i, sentence in enumerate(filtered_words):
        for word in sentence:
            sentence_scores[i] += word_freq[word] / sum(word_freq.values())
    for i, sentence in enumerate(filtered_words):
        for j, other_sentence in enumerate(filtered_words):
            if i == j:
                continue
            similarity = calculate_similarity(sentence, other_sentence)
            sentence_scores[i] += similarity
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_sentences = [sentences[i] for i, score in top_sentences]
    summary = ' '.join(top_sentences)
    return summary

# Function for TF-IDF summarization
def summarize_tf_idf(text, num_sentences=3):
    sentences = sent_tokenize(text)
    cleaned_text = ""
    dict = {}
    for sentence in sentences:
        temp = re.sub("[^a-zA-Z]", " ", sentence)
        temp = temp.lower()
        dict[temp] = sentence
        cleaned_text += temp
    stop_words = set(stopwords.words('english'))
    word_frequencies = defaultdict(int)
    for word in word_tokenize(cleaned_text):
        if word not in stop_words:
            word_frequencies[word] += 1
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] /= max_freq
    sentence_scores = defaultdict(int)
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if len(sentence.split(' ')) < 30:
                    sentence_scores[sentence] += word_frequencies[word]
    top_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(top_sentences)
    return summary

# Function for BART summarization
def summarize_bart(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = model.generate(inputs.input_ids, num_beams=4, max_length=250, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form['text']
    method = request.form['method']
    if method == 'bart-cnn':
        summary = summarize_bart(text)
    elif method == 'textrank':
        summary = summarize_text_rank(text)
    elif method == 'tfidf':
        summary = summarize_tf_idf(text)
    else:
        summary = "Invalid summarization method."
    return render_template('index.html', summary=summary, original_text=text)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8083)
