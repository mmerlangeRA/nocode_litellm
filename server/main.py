"""FastAPI app creation, logger configuration and main API routes."""
from server.di import global_injector
from server.launcher import create_app
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

app = create_app(global_injector)
