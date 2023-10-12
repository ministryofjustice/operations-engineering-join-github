"""operations-engineering-landing-page"""
from landing_page_app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(port=app.config.get("PORT", 4567))
