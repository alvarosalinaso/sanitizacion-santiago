"""Dev launcher on port 8091 (avoids clashing with Docker :8056)."""
from dashboard import app

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8091)
