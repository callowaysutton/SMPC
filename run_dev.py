from app import app
import os

if __name__ == "__main__":
    if os.getenv("FLASK_ENV") == "production":
        app.run(debug=False, host='0.0.0.0', port=5000)
    app.run(debug=True, port=5000)