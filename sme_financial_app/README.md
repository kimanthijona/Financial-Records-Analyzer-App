# SME Financial Analyzer

An AI- and ML-powered bookkeeping and accounting application for SMEs in Kenya. This application helps small businesses manage their finances by automatically processing financial documents, categorizing transactions, and providing insights and recommendations.

## Features

- **Document Processing**
  - OCR for receipts, invoices, and bank statements
  - Automatic transaction extraction and categorization
  - Support for PDF and image formats

- **Financial Analytics**
  - Cash flow forecasting
  - Expense analysis and categorization
  - Spending pattern detection
  - Financial recommendations

- **User Management**
  - SME registration and authentication
  - Secure document storage
  - Multi-user support

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy (SQLite for development, PostgreSQL for production)
- **ML/AI**: 
  - OCR: Tesseract
  - NLP: spaCy
  - ML: scikit-learn
  - Data Processing: pandas, numpy
- **Authentication**: JWT

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sme-financial-app.git
cd sme-financial-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
- Ubuntu: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`
- Windows: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

5. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

6. Set up environment variables:
Create a `.env` file in the project root with:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///sme_financial.db
TESSERACT_CMD=path/to/tesseract  # Only if not in system PATH
```

7. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Running the Application

1. Development server:
```bash
python run.py
```

2. Production server (using gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## API Endpoints

### Authentication
- `POST /api/auth/register`: Register a new SME
- `POST /api/auth/login`: Login and get JWT token

### Document Upload
- `POST /api/upload/document`: Upload a financial document
- `GET /api/upload/documents`: List uploaded documents

### Analytics
- `GET /api/analytics/cash-flow`: Get cash flow analysis and forecast
- `GET /api/analytics/expense-analysis`: Get expense analysis and recommendations
- `GET /api/analytics/summary`: Get financial summary

## Testing

Run tests using pytest:
```bash
pytest
```

## Project Structure

```
sme_financial_app/
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   ├── static/       # Static files
│   └── templates/    # HTML templates
├── data/
│   ├── raw/         # Uploaded documents
│   ├── processed/   # Processed data
│   └── models/      # Trained ML models
├── notebooks/       # Jupyter notebooks
├── scripts/         # Utility scripts
├── tests/          # Test cases
├── config/         # Configuration files
└── requirements.txt # Dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name <your.email@example.com>

## Acknowledgments

- Thanks to all contributors
- Special thanks to the open-source community 