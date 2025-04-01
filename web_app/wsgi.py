"""
WSGI (Web Server Gateway Interface) Entry Point

This module serves as the entry point for WSGI servers to interact with the Flask application.
It provides a standardized interface between the web server and the Python web application.

In a production environment, WSGI servers (like Gunicorn, uWSGI, or mod_wsgi) will use this file
to serve the application by importing the 'app' object.
"""

# Import the Flask application instance from the app module
from app import app  # Make sure 'app' is the correct name of your Flask instance

# This conditional ensures that the development server only runs if this script is executed directly
if __name__ == "__main__":
    # Start the development server
    # Note: This should only be used for development purposes, not in production
    app.run()
