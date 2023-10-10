"""operations-engineering-landing-page"""
from landing_page_app import app

if __name__ == "__main__":
    app.run(port=app.config.get("PORT", 4567))
