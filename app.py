from flask import Flask
from config import Config
from extensions import db, login_manager
from routes.auth import auth
from routes.main import main
import threading
from pyngrok import ngrok

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(main)

def start_ngrok():
    public_url = ngrok.connect(5000)
    print(f" * Your Flask app is publicly accessible at: {public_url}")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Using database:", app.config['SQLALCHEMY_DATABASE_URI'])

    threading.Thread(target=start_ngrok, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)