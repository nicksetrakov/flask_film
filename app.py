# Import the "app" object from the "app" module
from app import app

# Check if the file is being executed as the main script (not imported)
if __name__ == "__main__":
    # Start the Flask web server on the local address 127.0.0.1 and port 5000
    # The "debug=True" parameter enables debugging mode, which is useful for development
    app.run(host='127.0.0.1', port=5000, debug=True)
