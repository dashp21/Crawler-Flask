import io
import json
import os
import requests

from PyPDF2 import PdfReader
from flask import Flask, jsonify

from nltk.sentiment import SentimentIntensityAnalyzer


app = Flask(__name__)
sia = SentimentIntensityAnalyzer()
keywords = ["pé diabético", "neuropatia diabética", "úlcera diabética", "amputação", "neuropatia periférica", "circulação sanguínea", "tratamento", "diagnóstico", "prevenção", "complicações", "diabetes mellitus", "cuidados", "terapia", "monitoramento"]


@app.route('/results')
def results():
    output_file = "resultados.json"
    results = []

    for url in ["https://iwgdfguidelines.org/wp-content/uploads/2020/12/Brazilian-Portuguese-translation-IWGDF-Guidelines-2019.pdf",
                "https://portal.unicap.br/documents/475032/672293/ebook+Livro+pe+diabetico-2020.pdf/36b829a4-e588-cee9-e4ea-89cf8cf50fc6?t=1608742383653#:~:text=Segundo%20o%20Minist%C3%A9rio%20da%20Sa%C3%BAde,diabetes%20(BRASIL%2C%202016)"]:
        response = requests.get(url)

        with io.BytesIO(response.content) as data:
            reader = PdfReader(data)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                lines = text.split('\n')
                for j, line in enumerate(lines):
                    if _contains_keywords(line):
                        result = {
                            'page_number': i + 1,
                            'position': j,
                            'context': lines[j-2:j+2],
                            'text': line.strip(),
                            'sentiment_score': sia.polarity_scores(line)['compound']
                        }
                        results.append(result)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return jsonify(results)


def _contains_keywords(text):
    return any(word in text.lower() for word in keywords)


if __name__ == '__main__':
    app.run()
