from flask import Flask
from dotenv import load_dotenv
from controllers.search import search_bp
from controllers.predict_controller import predict_bp

load_dotenv()

app = Flask(__name__)

# Register your controller blueprint
app.register_blueprint(search_bp)
app.register_blueprint(predict_bp)

if __name__ == "__main__":
    app.run(debug=True)