# autokubex/main.py

from models.feedback_db import init_feedback_db
init_feedback_db()


from interface.cli import app

if __name__ == "__main__":
    app()
