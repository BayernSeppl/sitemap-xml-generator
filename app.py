#!/usr/bin/env python3
"""
Sitemap XML Generator - Crawlt Websites und erstellt XML-Sitemaps
"""

from flask import Flask, render_template, request, jsonify, send_file
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
from io import BytesIO
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SitemapGenerator:
    def __init__(self, base_url, max_pages=500):
        self.base_url = base_url if base_url.startswith('http') else f'https://{base_url}'
        self.base_domain = urlparse(self.base_url).netloc
        self.visited = set()
        self.urls = []
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.timeout = 10

    def is_valid_url(self, url):
        """Prüft ob URL zur gleichen Domain gehört"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.base_domain and parsed.scheme in ['http', 'https']
        except:
            return False

    def clean_url(self, url):
        """Entfernt Anker und Query-Parameter"""
        parsed = urlparse(url)
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean += f"?{parsed.query}"
        return clean

    def crawl(self, url=None):
        """Crawlt die Website rekursiv"""
        if url is None:
            url = self.base_url
        
        if len(self.visited) >= self.max_pages:
            return
        
        url = self.clean_url(url)
        
        if url in self.visited:
            return
        
        self.visited.add(url)
        logger.info(f"Crawling: {url} ({len(self.visited)}/{self.max_pages})")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Füge aktuelle URL hinzu
            self.urls.append({
                'url': url,
                'lastmod': datetime.now().strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.8' if url == self.base_url else '0.7'
            })
            
            # Finde alle Links
            for link in soup.find_all('a', href=True):
                href = urljoin(url, link['href'])
                
                if self.is_valid_url(href) and href not in self.visited:
                    if len(self.visited) < self.max_pages:
                        self.crawl(href)
        
        except requests.Timeout:
            logger.warning(f"Timeout: {url}")
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")

    def generate_xml(self):
        """Generiert XML-Sitemap"""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        for url_data in self.urls:
            xml += '  <url>\n'
            xml += f'    <loc>{url_data["url"]}</loc>\n'
            xml += f'    <lastmod>{url_data["lastmod"]}</lastmod>\n'
            xml += f'    <changefreq>{url_data["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{url_data["priority"]}</priority>\n'
            xml += '  </url>\n'
        
        xml += '</urlset>'
        return xml

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    """API-Endpoint zum Sitemap generieren"""
    data = request.get_json()
    website_url = data.get('website_url', '').strip()
    max_pages = int(data.get('max_pages', 500))
    
    if not website_url:
        return jsonify({'error': 'Website URL erforderlich'}), 400
    
    try:
        generator = SitemapGenerator(website_url, max_pages=max_pages)
        generator.crawl()
        
        if not generator.urls:
            return jsonify({'error': 'Keine URLs gefunden. Überprüfe die Website-URL.'}), 400
        
        xml_content = generator.generate_xml()
        
        return jsonify({
            'success': True,
            'xml': xml_content,
            'url_count': len(generator.urls),
            'urls': generator.urls
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': f'Fehler beim Crawlen: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download():
    """Download der Sitemap als XML-Datei"""
    data = request.get_json()
    xml_content = data.get('xml', '')
    
    if not xml_content:
        return jsonify({'error': 'Keine XML-Datei verfügbar'}), 400
    
    file_obj = BytesIO(xml_content.encode('utf-8'))
    return send_file(
        file_obj,
        mimetype='application/xml',
        as_attachment=True,
        download_name='sitemap.xml'
    )

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🗺️  Sitemap XML Generator")
    print("="*60)
    print("📍 Öffne: http://localhost:5001")
    print("="*60 + "\n")
    app.run(debug=False, host='127.0.0.1', port=5001)
