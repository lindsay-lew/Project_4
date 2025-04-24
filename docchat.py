import readline

from dotenv import load_dotenv
load_dotenv()  

def llm(messages, temperature=1):
    '''
    This function is my interface for calling the LLM.
    The messages argument should be a list of dictionaries.

    >>> llm([
    ...     {'role': 'system', 'content': 'You are a helpful assistant.'},
    ...     {'role': 'system', 'content': 'What is the capital of France?'},
    ...     ], temperature=0)
    'The capital of France is Paris!'
    '''
    import groq
    client = groq.Groq()

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        temperature=temperature,
    )
    return chat_completion.choices[0].message.content


def chunk_text_by_words(text, max_words=100, overlap=50):
    '''
    Splits text into overlapping chunks by word count.

    Examples:
        >>> text = "The quick brown fox jumps over the lazy dog. It was a sunny day and the birds were singing."
        >>> chunks = chunk_text_by_words(text, max_words=5, overlap=2)
        >>> len(chunks)
        7
        >>> chunks[0]
        'The quick brown fox jumps'
        >>> chunks[1]
        'fox jumps over the lazy'
        >>> chunks[4]
        'sunny day and the birds'
        >>> chunks[-1]
        'singing.'
    '''
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_words - overlap

    return chunks


def load_text(filepath_or_url):
    '''
    Loads text from a given file path or URL. Supports .txt, .html, and .pdf formats.
    '''
    import os
    import requests
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup
    from PyPDF2 import PdfReader
    from io import BytesIO

    def is_url(path):
        parsed = urlparse(path)
        return parsed.scheme in ("http", "https")

    def get_extension(path):
        return os.path.splitext(urlparse(path).path)[1].lower()

    def load_txt(content):
        return content

    def load_html(content):
        soup = BeautifulSoup(content, "html.parser")
        return soup.get_text(separator=' ', strip=True)

    def load_pdf(content):
        try:
            reader = PdfReader(content)
            return "\n".join(page.extract_text() or '' for page in reader.pages).strip()
        except Exception:
            raise ValueError("Could not extract text from PDF: file may be invalid or empty.")

    ext = get_extension(filepath_or_url)

    if is_url(filepath_or_url):
        response = requests.get(filepath_or_url)
        response.raise_for_status()
        content = response.content
    else:
        with open(filepath_or_url, 'rb') as f:
            content = f.read()

    if ext == ".txt":
        return load_txt(content.decode("utf-8", errors="ignore"))
    elif ext == ".html":
        return load_html(content)
    elif ext == ".pdf":
        from io import BytesIO
        return load_pdf(BytesIO(content))
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


"""
import spacy
def load_spacy_model(language: str):
    '''
    Loads a spaCy model for the specified language.
    '''
    LANGUAGE_MODELS = {
        'french': 'fr_core_news_sm',
        'german': 'de_core_news_sm',
        'spanish': 'es_core_news_sm',
        'english': 'en_core_web_sm',
    }

    if language not in LANGUAGE_MODELS:
        raise ValueError(f"Unsupported language: {language}")

    return spacy.load(LANGUAGE_MODELS[language])
"""

'''
Examples (French):
        >>> round(score_chunk("Le soleil est brillant et chaud.", "Quelle est la température du soleil ?", language="french"), 2)
        0.33
        >>> round(score_chunk("La voiture rouge roule rapidement.", "Quelle est la couleur de la voiture ?", language="french"), 2)
        0.25
        >>> score_chunk("Les bananes sont jaunes.", "Comment fonctionnent les avions ?", language="french")
        0.0

    Examples (Spanish):
        >>> round(score_chunk("El sol es brillante y caliente.", "¿Qué temperatura tiene el sol?", language="spanish"), 2)
        0.33
        >>> round(score_chunk("El coche rojo va muy rápido.", "¿De qué color es el coche?", language="spanish"), 2)
        0.25
        >>> score_chunk("Los plátanos son amarillos.", "¿Cómo vuelan los aviones?", language="spanish")
        0.0
'''


def score_chunk(chunk: str, query: str, language: str = "french") -> float:
    '''
    Scores a chunk against a user query using Jaccard similarity of lemmatized word sets with stopword removal.

    Examples (English):
        >>> round(score_chunk("The sun is bright and hot.", "How hot is the sun?", language="english"), 2)
        0.5
        >>> round(score_chunk("The red car is speeding down the road.", "What color is the car?", language="english"), 2)
        0.25
        >>> score_chunk("Bananas are yellow.", "How do airplanes fly?", language="english")
        0.0
    '''
    chunk_words = set(chunk.lower().split())
    query_words = set(query.lower().split())

    if not chunk_words or not query_words:
        return 0.0

    intersection = chunk_words & query_words
    union = chunk_words | query_words

    return len(intersection) / len(union)
    '''
    def preprocess(text):
        doc = nlp(text.lower())
        return set(
            token.lemma_ for token in doc
            if token.is_alpha and not token.is_stop
        )

    chunk_words = preprocess(chunk)
    query_words = preprocess(query)

    if not chunk_words or not query_words:
        return 0.0

    intersection = chunk_words & query_words
    union = chunk_words | query_words

    return len(intersection) / len(union)
    '''

def find_relevant_chunks(text, query, num_chunks=5):
    '''
    This function will: 
    1) split the document into chunks 
    2) compute the score for each of these chunks
    3) return the num_chunks chunks that have the largest score

    >>> text = "The sun is bright and hot. Bananas are yellow. The red car speeds by."
    >>> query = "How hot is the sun?"
    >>> find_relevant_chunks(text, query, num_chunks=1)
    ['The sun is bright and hot.']
    '''
    chunks = chunk_text_by_words(text, max_words=10, overlap=5)
    scored = [(chunk, score_chunk(chunk, query, language=language)) for chunk in chunks]
    top_chunks = sorted(scored, key=lambda x: x[1], reverse=True)[:num_chunks]
    return [chunk for chunk, _ in top_chunks]






if __name__ == '__main__':
    messages = []
    messages.append({
        'role': 'system',
        'content': "You are a helpful assistant. You always speak like a pirate. You always answer in 1 sentence",
    })
    while True:
        # Get input from the user 
        text = input('docchat>')
        # Pass that input to llm
        messages.append({
            'role': 'user',
            'content': text,
        })
        result = llm(messages)

        # Add the "assistant" role to the messages list so that the 'llm' has access to the whole conversation history
        # and will know what it has previously says, and update its response based on that information 
        messages.append({
            'role': 'assistant',
            'content': result,
        })

        # Print the llm's response to the user
        print('result=', result)
        import pprint
        pprint.pprint(messages)