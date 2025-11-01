# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import app  # <-- adjust if your FastAPI app lives elsewhere

client = TestClient(app)


@pytest.fixture(scope="session")
def test_client():
    return client


@pytest.fixture(scope="session")
def sample_data():
    return [
        {
            "name": "Apple iPhone 15 Pro",
            "title": "Flagship smartphone with A17 chip",
            "description": "The latest iPhone with an advanced A17 Bionic processor, titanium frame, and powerful camera system designed for professionals.",
            "tags": ["smartphone", "apple", "mobile", "electronics"],
        },
        {
            "name": "Tesla Model 3",
            "title": "Electric sedan with autopilot features",
            "description": "A sleek electric car that combines performance, safety, and technology. Includes full self-driving capabilities and long battery range.",
            "tags": ["electric", "car", "tesla", "automobile"],
        },
        {
            "name": "MacBook Air M3",
            "title": "Ultra-light laptop for productivity",
            "description": "Apple’s latest MacBook Air with M3 chip offers remarkable performance and battery life, ideal for students and remote workers.",
            "tags": ["laptop", "macbook", "apple", "computer"],
        },
        {
            "name": "Sony WH-1000XM5",
            "title": "Noise cancelling wireless headphones",
            "description": "Industry-leading noise cancellation with crystal-clear sound, adaptive EQ, and 30-hour battery life for immersive listening.",
            "tags": ["headphones", "audio", "sony", "music"],
        },
        {
            "name": "The Lean Startup",
            "title": "Book on innovation and entrepreneurship",
            "description": "Eric Ries introduces a scientific approach to creating and managing successful startups in an age of uncertainty.",
            "tags": ["book", "startup", "business", "entrepreneurship"],
        },
        {
            "name": "Nike Air Zoom Pegasus 41",
            "title": "Running shoes built for speed and comfort",
            "description": "Lightweight, cushioned running shoes ideal for daily training. Responsive midsole and breathable upper for maximum performance.",
            "tags": ["shoes", "running", "sports", "nike"],
        },
        {
            "name": "Samsung Galaxy Tab S9",
            "title": "Android tablet for creativity",
            "description": "A high-end tablet with AMOLED display and S Pen support, perfect for drawing, note-taking, and productivity on the go.",
            "tags": ["tablet", "samsung", "android", "electronics"],
        },
        {
            "name": "Kindle Paperwhite",
            "title": "E-reader with glare-free display",
            "description": "Lightweight waterproof e-reader with adjustable warm light, allowing you to read comfortably anytime, anywhere.",
            "tags": ["ebook", "kindle", "reading", "books"],
        },
        {
            "name": "Bose SoundLink Revolve+",
            "title": "Portable Bluetooth speaker",
            "description": "360° sound experience with deep bass and durable build, ideal for outdoor gatherings and travel.",
            "tags": ["speaker", "bose", "audio", "portable"],
        },
        {
            "name": "Notion",
            "title": "Productivity and collaboration tool",
            "description": "All-in-one workspace for notes, tasks, and databases that helps teams stay organized and productive.",
            "tags": ["software", "productivity", "collaboration", "tools"],
        },
    ]


@pytest.fixture(scope="session", autouse=True)
def load_sample_data(test_client, sample_data):
    """
    Load the sample data once before all tests.
    We assume you have POST /items that accepts the above payload.
    If your endpoint is different, change it here.
    """
    for item in sample_data:
        resp = test_client.post("/items", json=item)
        assert resp.status_code in (200, 201)
    return True
