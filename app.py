"""Web application for the customer complaint classifier.

Run with: ./.venv/Scripts/python.exe app.py
Then open: http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from train import predict_probabilities, tokenize


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "complaint_classifier.json"
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "static"
MAX_COMPLAINT_LENGTH = 3_000
DISPLAY_STOP_WORDS = {
    "after", "before", "can", "cannot", "day", "days", "every", "get", "got",
    "help", "month", "months", "need", "not", "one", "please", "still", "three",
    "time", "two", "week", "weeks", "when", "will",
}


def load_model() -> dict[str, object]:
    """Load the latest saved model so retraining is reflected after refresh."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "Trained model is missing. Run '.\\.venv\\Scripts\\python.exe train.py' first."
        )
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


def evidence_tokens(model: dict[str, object], category: str, complaint: str) -> list[str]:
    """Return recognizable input words that appear in the predicted class."""
    class_counts = model["class_token_counts"].get(category, {})
    scored = [
        (token, int(class_counts.get(token, 0)))
        for token in dict.fromkeys(tokenize(complaint))
        if int(class_counts.get(token, 0)) > 0 and token not in DISPLAY_STOP_WORDS
    ]
    return [token for token, _ in sorted(scored, key=lambda item: (-item[1], item[0]))[:5]]


def model_information(model: dict[str, object]) -> dict[str, object]:
    return {
        "algorithm": "Multinomial Naive Bayes",
        "training_examples": model["training_examples"],
        "vocabulary_size": model["vocabulary_size"],
        "categories": model["categories"],
    }


class ClassifierHandler(SimpleHTTPRequestHandler):
    """Serve the dashboard and a small JSON API without external packages."""

    server_version = "ComplaintClassifier/1.0"

    def log_message(self, format: str, *args: object) -> None:
        # Keep the terminal focused on meaningful requests.
        if not args or not str(args[0]).startswith("GET /static"):
            super().log_message(format, *args)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self.send_file(TEMPLATE_PATH, "text/html; charset=utf-8")
            return
        if path == "/api/model-info":
            try:
                self.send_json(HTTPStatus.OK, model_information(load_model()))
            except FileNotFoundError as error:
                self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            return
        if path.startswith("/static/"):
            requested_file = (STATIC_DIR / path.removeprefix("/static/")).resolve()
            if STATIC_DIR not in requested_file.parents or not requested_file.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
                return
            media_type, _ = mimetypes.guess_type(str(requested_file))
            self.send_file(requested_file, media_type or "application/octet-stream")
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Page not found")

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        if urlparse(self.path).path != "/api/predict":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            complaint = str(payload.get("complaint", "")).strip()
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Send a valid JSON complaint."})
            return

        if not complaint:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Enter a complaint before analysis."})
            return
        if len(complaint) > MAX_COMPLAINT_LENGTH:
            self.send_json(
                HTTPStatus.BAD_REQUEST,
                {"error": f"Keep the complaint below {MAX_COMPLAINT_LENGTH:,} characters."},
            )
            return

        try:
            model = load_model()
            probabilities = predict_probabilities(model, complaint)
        except FileNotFoundError as error:
            self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": str(error)})
            return

        ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
        predicted_category, confidence = ranked[0]
        runner_up = ranked[1][1] if len(ranked) > 1 else 0.0
        response = {
            "category": predicted_category,
            "confidence": round(confidence, 4),
            "confidence_label": "High confidence" if confidence >= 0.75 else "Review suggested",
            "margin": round(confidence - runner_up, 4),
            "probabilities": [
                {"category": category, "probability": round(probability, 4)}
                for category, probability in ranked
            ],
            "evidence": evidence_tokens(model, predicted_category, complaint),
            "tokens_analyzed": len(tokenize(complaint)),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "model": model_information(model),
        }
        self.send_json(HTTPStatus.OK, response)

    def send_file(self, file_path: Path, content_type: str) -> None:
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status: HTTPStatus, data: dict[str, object]) -> None:
        content = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    # Default to the dashboard port while allowing a hosting platform to
    # supply its own network settings.
    # Cloud providers such as Render route traffic through a public interface.
    # Listening on all interfaces keeps local use working while allowing Render
    # to detect the application port supplied through its PORT environment variable.
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ClassifierHandler)
    print("\nNUT Complaint Intelligence is running.")
    print(f"Open http://{host}:{port} in your browser")
    print("Press Ctrl+C to stop the server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
