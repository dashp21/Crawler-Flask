import scrapy
import io
import json
from PyPDF2 import PdfReader
from flask import Flask
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

@app.route('/')
class PdfCrawler(scrapy.Spider):
    name = 'pdf_crawler'
    start_urls = [
        'https://iwgdfguidelines.org/wp-content/uploads/2020/12/Brazilian-Portuguese-translation-IWGDF-Guidelines-2019.pdf',
        'https://portal.unicap.br/documents/475032/672293/ebook+Livro+pe+diabetico-2020.pdf/36b829a4-e588-cee9-e4ea-89cf8cf50fc6?t=1608742383653#:~:text=Segundo%20o%20Minist%C3%A9rio%20da%20Sa%C3%BAde,diabetes%20(BRASIL%2C%202016)'
    ]
    output_file = "resultados.json"
    results = []
    sia = SentimentIntensityAnalyzer()
    keywords = ["pé diabético", "neuropatia diabética", "úlcera diabética", "amputação", "neuropatia periférica", "circulação sanguínea", "tratamento", "diagnóstico", "prevenção", "complicações", "diabetes mellitus" , "cuidados", "terapia", "monitoramento"]

    def parse(self, response):
        with io.BytesIO(response.body) as data:
            reader = PdfReader(data)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                lines = text.split('\n')
                for j, line in enumerate(lines):
                    if self._contains_keywords(line):
                        result = {
                            'page_number': i + 1,
                            'position': j,
                            'context': lines[j-2:j+2],
                            'text': line.strip(),
                            'sentiment_score': self.sia.polarity_scores(line)['compound']
                        }
                        self.results.append(result)

        with open(self.output_file, "w",encoding="utf-8") as f:
            json.dump(self.results, f, indent=4, ensure_ascii=False)

        self.log(f'Informações salvas em {self.output_file}')

    def _contains_keywords(self, text):
        return any(word in text.lower() for word in self.keywords)
    

    if __name__ == '__main__':
        app.run()
    
