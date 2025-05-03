import spacy
from app.models.transaction import Transaction
from collections import defaultdict

# Load English language model
nlp = spacy.load('en_core_web_sm')

# Define category rules and keywords
CATEGORY_RULES = {
    'salary': ['salary', 'payroll', 'wage', 'income', 'payment'],
    'rent': ['rent', 'lease', 'property', 'housing'],
    'utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'utility'],
    'supplies': ['supplies', 'inventory', 'stock', 'materials'],
    'marketing': ['advertising', 'marketing', 'promotion', 'ads'],
    'insurance': ['insurance', 'coverage', 'policy'],
    'taxes': ['tax', 'vat', 'levy', 'duty'],
    'transport': ['transport', 'fuel', 'vehicle', 'travel'],
    'maintenance': ['repair', 'maintenance', 'service'],
    'food': ['food', 'meal', 'restaurant', 'catering'],
    'other': []  # Default category
}

def categorize_transaction(description):
    """
    Categorize a transaction based on its description using NLP.
    """
    # Preprocess description
    doc = nlp(description.lower())
    
    # Extract relevant tokens (nouns and proper nouns)
    tokens = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    
    # Find matching category
    max_matches = 0
    best_category = 'other'
    
    for category, keywords in CATEGORY_RULES.items():
        matches = sum(1 for token in tokens if any(keyword in token for keyword in keywords))
        if matches > max_matches:
            max_matches = matches
            best_category = category
    
    return best_category

def categorize_transactions(transactions):
    """
    Batch categorize a list of transactions.
    """
    for transaction in transactions:
        if not transaction.category:
            transaction.category = categorize_transaction(transaction.description)
    
    return transactions

def analyze_spending_patterns(transactions):
    """
    Analyze spending patterns in transactions using NLP.
    """
    # Group transactions by category
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    
    for transaction in transactions:
        if transaction.transaction_type == 'expense':
            category = transaction.category or categorize_transaction(transaction.description)
            category_totals[category] += transaction.amount
            category_counts[category] += 1
    
    # Calculate average spending per category
    category_averages = {
        category: total / category_counts[category]
        for category, total in category_totals.items()
    }
    
    # Find top spending categories
    top_categories = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return {
        'category_totals': dict(category_totals),
        'category_averages': category_averages,
        'top_categories': dict(top_categories)
    }

def extract_entities(text):
    """
    Extract named entities from text using spaCy.
    """
    doc = nlp(text)
    entities = defaultdict(list)
    
    for ent in doc.ents:
        entities[ent.label_].append({
            'text': ent.text,
            'start': ent.start_char,
            'end': ent.end_char
        })
    
    return dict(entities)

def analyze_transaction_description(description):
    """
    Analyze a transaction description to extract key information.
    """
    doc = nlp(description)
    
    analysis = {
        'entities': extract_entities(description),
        'key_phrases': [],
        'sentiment': 'neutral'
    }
    
    # Extract key phrases (noun chunks)
    analysis['key_phrases'] = [chunk.text for chunk in doc.noun_chunks]
    
    # Simple sentiment analysis based on keywords
    positive_words = {'payment', 'received', 'income', 'profit'}
    negative_words = {'expense', 'paid', 'cost', 'fee'}
    
    text_tokens = set(token.text.lower() for token in doc)
    pos_matches = len(text_tokens.intersection(positive_words))
    neg_matches = len(text_tokens.intersection(negative_words))
    
    if pos_matches > neg_matches:
        analysis['sentiment'] = 'positive'
    elif neg_matches > pos_matches:
        analysis['sentiment'] = 'negative'
    
    return analysis 