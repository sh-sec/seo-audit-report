from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(filename='api.log', level=logging.INFO)

def fetch_http_status(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"status": response.status_code, "success": True}
    except requests.RequestException as e:
        logging.error(f"Error fetching HTTP status for {url}: {str(e)}")
        return {"error": str(e), "success": False}

def fetch_title(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else None
        return {"title": title, "success": True}
    except requests.RequestException as e:
        logging.error(f"Error fetching title for {url}: {str(e)}")
        return {"error": str(e), "success": False}

def fetch_external_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        external_links = [
            {"href": link['href'], "text": link.get_text().strip()}
            for link in soup.find_all('a', href=True) if 'http' in link['href']
        ]
        return {"external_links": external_links, "success": True}
    except requests.RequestException as e:
        logging.error(f"Error fetching external links for {url}: {str(e)}")
        return {"error": str(e), "success": False}

@app.route('/seo-audit', methods=['POST'])
def generate_seo_audit_report():
    try:
        data = request.get_json()
        url = data.get('url', '')

        if not url:
            return jsonify({"error": "URL not provided"}), 400

        http_status = fetch_http_status(url)
        title_data = fetch_title(url)
        external_links_data = fetch_external_links(url)

        seo_audit_report = {
            "data": {
                "success": all(result["success"] for result in [http_status, title_data, external_links_data]),
                "result": {
                    "Input": {
                        "URL": url,
                        "Input type": "Domain"
                    },
                    "http": http_status,
                    "title": title_data,
                    "links_summary": {
                        "Total links": len(external_links_data["external_links"]),
                        "External links": len(external_links_data["external_links"]),
                        "Internal": 0,
                        "Nofollow count": 0,
                        "links": external_links_data["external_links"]
                    }
                }
            }
        }

        logging.info(f"SEO audit report generated successfully for {url}")
        return jsonify(seo_audit_report)

    except Exception as e:
        logging.error(f"Error in generating SEO audit report: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)