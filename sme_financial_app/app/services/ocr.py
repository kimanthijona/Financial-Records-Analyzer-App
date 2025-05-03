import pytesseract
from pdf2image import convert_from_path
import os
from PIL import Image
from app import db
from app.models.document import Document
from app.models.transaction import Transaction
from datetime import datetime
import re

def process_document(document_id):
    """
    Process a document using OCR to extract text and create transactions.
    """
    document = Document.query.get(document_id)
    if not document:
        return
    
    try:
        # Convert PDF to images if necessary
        if document.filename.lower().endswith('.pdf'):
            images = convert_from_path(document.file_path)
            text = ''
            for image in images:
                text += pytesseract.image_to_string(image)
        else:
            # Process image directly
            image = Image.open(document.file_path)
            text = pytesseract.image_to_string(image)
        
        # Extract transactions from text
        transactions = extract_transactions(text)
        
        # Create transaction records
        for t in transactions:
            transaction = Transaction(
                user_id=document.user_id,
                amount=t['amount'],
                transaction_type=t['type'],
                category=t.get('category'),
                description=t.get('description'),
                date=t['date'],
                source=t.get('source', 'document'),
                document_id=document.id
            )
            db.session.add(transaction)
        
        # Update document status
        document.status = 'processed'
        document.processed_at = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        document.status = 'failed'
        db.session.commit()
        raise e

def extract_transactions(text):
    """
    Extract transaction information from OCR text.
    """
    transactions = []
    
    # Common patterns for transaction extraction
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    amount_pattern = r'[\d,]+\.\d{2}'
    
    # Split text into lines
    lines = text.split('\n')
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Look for date and amount in the line
        date_match = re.search(date_pattern, line)
        amount_match = re.search(amount_pattern, line)
        
        if date_match and amount_match:
            date_str = date_match.group()
            amount_str = amount_match.group().replace(',', '')
            
            try:
                # Parse date
                date = datetime.strptime(date_str, '%d/%m/%Y')
                
                # Parse amount
                amount = float(amount_str)
                
                # Determine transaction type (income or expense)
                # This is a simple heuristic - in practice, you might need more sophisticated logic
                transaction_type = 'income' if amount > 0 else 'expense'
                
                # Create transaction object
                transaction = {
                    'date': date,
                    'amount': abs(amount),
                    'type': transaction_type,
                    'description': line.strip()
                }
                
                transactions.append(transaction)
            except ValueError:
                continue
    
    return transactions 