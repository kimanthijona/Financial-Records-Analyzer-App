from app import create_app
from config.config import get_config
import logging.config
import os

# Set up logging
logging_conf_path = os.path.join(os.path.dirname(__file__), 'config', 'logging.conf')
logging.config.fileConfig(logging_conf_path)

# Create Flask app with configuration
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV', 'development') == 'development'
    ) 