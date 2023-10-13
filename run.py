from app import create_app

app = create_app()

if __name__ == '__main__':
    """
    Entry point for the Flask application.
    Starts the Flask development server if this script is executed directly.
    """
    app.run(debug=True, use_reloader=False)
