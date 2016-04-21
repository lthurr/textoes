# coding=utf-8
import glob
from collections import defaultdict
import csv
import re
import os
from nltk.tag.stanford import StanfordPOSTagger

number_names = ['cero', 'uno', r'\bdos\b', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'un tercio', 'sexta', 'sextoava', 'un sexto', 'cuarta', 'un medio', 'cubo']
constant_names = ['equis', 'i griega', 'efe', r'\bx\b', r'\bexis\b', r'\bce\b', r'\bc\b', r'\bb\b', r'\bbe\b', r'\bye\b']

bracket_rules = defaultdict(lambda : defaultdict(list))
bracket_rules.update({
    'n1e1': {'r1': [(1, 2), (1, 3), (1, 4)], 'r2': [(2,3), (1, 3)], 'r3': []},
    'n1e2': {'r1': [(2, 3)], 'r2': [(1, 2)], 'r3': [(1, 2), (1, 3)]},
    'n1e3': {'r1': [(1, 2), (1, 3)], 'r2': [(1, 2), (1, 3)], 'r3': [(3, 4), (1, 2)]},

    'n1e5': {'r1': [(1, 2)], 'r2': [(1, 2), (3, 4)], 'r3': []}
})


class LanguageModel(object):

    def __init__(self, corpus_path='corpus/'):
        self.corpus_path = corpus_path
        model_data = os.path.join(os.getcwd(), "corpus", "model", "spanish.tagger")
        jar_file = os.path.join(os.getcwd(), "corpus", "model", "stanford-postagger.jar")
        self.spanish_postagger = StanfordPOSTagger(model_data, jar_file)

    def __analizing_csv_file(self, filename):
        self.csv_file = filename.split('\\')[-1].replace('.csv', '').lower()

    def __clean_response(self, response, response_i):
        pattern = r'[0-9]|' + '|'.join(number_names + constant_names)
        response = response.replace('"', '')
        response = response.strip()
        response = response.replace('.', '')
        response = response.replace('( ', '(').replace(' )', ')')
        response = response.replace('á', 'a').replace('à', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        response = response.lower()
        response = response.replace(',', '')
        response = response.replace('$term$', '$TERM$')
        if response.count(' ') == 0:  # No es una respuesta valida, quiero omitirla
            return ''
        response = re.sub(pattern, '$TERM$', response)
        response = self.put_brackets(response, bracket_rules[self.csv_file][response_i])
        return response

    def put_brackets(self, str, rules):
        print str
        str = str.replace('(', '').replace(')', '').replace('parentesis', '')
        words = str.split()
        indexes = [i for i, j in enumerate(words) if '$TERM$' in j]
        for rule in rules:
            begin, end = rule
            first, last = indexes[begin-1], indexes[end-1]
            words[first] = '(' + words[first]
            words[last] = words[last] + ')'
        words[0], words[-1] = '(' + words[0], words[-1] + ')'
        return ' '.join(words)

    def _get_multiple_responses(self, str, response_i):
        str = str.strip('\n')
        str = str.replace('\n\n', '\n')
        str = str.replace('  ', ' ')
        responses = str.split('\n')
        result = list()
        for resp in responses:
            result.append(self.__clean_response(resp, response_i))
        return result

    def _parse_csv_row(self, row):
        response_1, response_2, response_3 = row[1:4]
        if response_1.startswith('¿Cómo la es'):
            return {'r1': [''], 'r2': [''], 'r3': ['']}
        return {
            'r1': self._get_multiple_responses(response_1, 'r1'),
            'r2': self._get_multiple_responses(response_2, 'r2'),
            'r3': self._get_multiple_responses(response_3, 'r3')
        }

    def prepare_corpus(self):
        csv_files = glob.glob(self.corpus_path + '*.csv')
        corpus_file = self.corpus_path + 'corpus.txt'
        with open(corpus_file, 'w') as corpus:
            for file in csv_files:
                responses = defaultdict(list)
                for row in csv.reader(open(file)):
                    self.__analizing_csv_file(file)
                    r1, r2, r3 = self._parse_csv_row(row).values()
                    responses['r1'] += r1
                    responses['r2'] += r2
                    responses['r3'] += r3
                corpus.write(self.csv_file + 'r1')
                corpus.write('\n'.join(filter(lambda x: x != '', responses['r1'])) + '\n')
                corpus.write(self.csv_file + 'r2')
                corpus.write('\n'.join(filter(lambda x: x != '', responses['r2'])) + '\n')
                corpus.write(self.csv_file + 'r3')
                corpus.write('\n'.join(filter(lambda x: x != '', responses['r3'])) + '\n')

    def evaluate_transcription(self, transcription):
        if not os.path.exists(os.path.join(os.getcwd(), "corpus", "corpus.txt")):
            self.prepare_corpus()
        pass


a = LanguageModel()
a.prepare_corpus()