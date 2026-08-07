from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import shutil
from llm_rag import LLMRAGHandler
from conversation import ConversationManager
from utils import UPLOAD_FOLDER

app = Flask(__name__)
CORS(app)

# Initialize handler once
handler = LLMRAGHandler()
conversation_manager = ConversationManager()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/upload', methods=['POST'])
def upload_pdfs():
    files = request.files.getlist('files')
    saved = []

    UPLOAD_FOLDER.mkdir(exist_ok=True)

    for f in files:
        dest = UPLOAD_FOLDER / f.filename
        f.save(dest)
        handler.add_pdf_to_context(dest)
        saved.append(f.filename)

    return jsonify({'uploaded': saved})


@app.route('/ask', methods=['POST'])
def ask():
    question = request.form.get('question') or request.json.get('question') if request.is_json else None
    if not question:
        return jsonify({'error': 'question is required'}), 400
    # Run generation with timeout to avoid hanging the HTTP request
    from concurrent.futures import ThreadPoolExecutor, TimeoutError

    with ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(handler.generate_response, question)
        try:
            answer = future.result(timeout=20)
        except TimeoutError:
            return jsonify({'error': 'LLM generation timed out'}), 504

    return jsonify({'answer': answer})


@app.route('/history', methods=['GET'])
def get_history():
    history = handler.get_history()
    out = []
    for m in history:
        role = 'user' if m.type == 'human' else ('system' if m.type == 'system' else 'assistant')
        out.append({'role': role, 'content': m.content})
    return jsonify({'history': out})


@app.route('/index_websites', methods=['POST'])
def index_websites():
    data = request.get_json() or {}
    urls = data.get('urls', [])
    handler.vector_store.index_websites(urls)
    return jsonify({'indexed': len(urls)})


@app.route('/ask_quick', methods=['POST'])
def ask_quick():
    data = request.get_json() or {}
    question = data.get('question')
    if not question:
        return jsonify({'error': 'question is required'}), 400

    docs = handler.retrieve(question)
    snippets = [getattr(d, 'page_content', str(d))[:800] for d in docs]
    return jsonify({'retrieved': snippets})


@app.route('/clear', methods=['POST'])
def clear():
    handler.reset()
    conversation_manager.clear()
    return jsonify({'cleared': True})


@app.route('/routes', methods=['GET'])
def routes():
    # Return a list of registered routes for debugging
    rules = []
    for rule in app.url_map.iter_rules():
        rules.append({'rule': str(rule), 'methods': list(rule.methods)})
    return jsonify({'routes': rules})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
