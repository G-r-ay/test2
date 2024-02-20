import random
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import streamlit as st
st.set_page_config(layout='wide')
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

@st.cache_data
def generate_sentences():
    def synonym_replacement(sentence, n=1):
        words = word_tokenize(sentence)
        new_words = words.copy()
        for _ in range(n):
            for i, word in enumerate(words):
                syns = wordnet.synsets(word)
                if syns:
                    synonym = syns[0].lemmas()[0].name()
                    if synonym != word and synonym not in stopwords.words('english'):
                        new_words[i] = synonym
                        break
        return ' '.join(new_words)

    def word_insertion(sentence, n=1):
        words = word_tokenize(sentence)
        for _ in range(n):
            word_to_insert = random.choice(words)
            words.insert(words.index(word_to_insert), word_to_insert)
        return ' '.join(words)

    def word_deletion(sentence, n=1):
        words = word_tokenize(sentence)
        for _ in range(n):
            if len(words) > 1:
                word_to_delete = random.choice(words)
                words.remove(word_to_delete)
        return ' '.join(words)

    def paraphrase(sentence):
        return synonym_replacement(sentence, n=1)

    dummy_sentences = [
        "One two three three five",
        "One two three two five",
        "One two three two five",
        "One two three two five",
        "One two three two five",
        "One two three hello five",
        "One two three hi five",
        "One two three hey five",
        "One two three gibberish five",
        "One two three nonsense five",
        "One two three abstract five",
    ]

    sentences = []
    for sentence in dummy_sentences:
        sentences.append(sentence)
        sentences.append(synonym_replacement(sentence))
        sentences.append(word_insertion(sentence))
        sentences.append(word_deletion(sentence))
        sentences.append(paraphrase(sentence))

    return sentences
augmented_sentences = generate_sentences()
