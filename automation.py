import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

@app.route("/items", methods=["POST"])
def search_items():
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.amazon.in/")
        page.get_by_placeholder("Search Amazon.in").fill(query)
        page.get_by_placeholder("Search Amazon.in").press("Enter")
        page.wait_for_timeout(4000)

        item_links = page.evaluate('''
            Array.from(document.querySelectorAll("a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"))
            .map(node => ({
                href: node.href,
                title: node.textContent.trim()
            }))
        ''')

        browser.close()

    return jsonify(item_links)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
