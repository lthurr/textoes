# coding=utf-8
import glob
from collections import defaultdict
import csv
import re
import os
#from nltk.tag.stanford import StanfordPOSTagger

number_names = ['cero', 'uno', r'\bdos\b', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'un tercio', 'sexta', 'sextoava', 'un sexto', 'cuarta', 'un medio', 'cubo', 'cuadrado']
constant_names = ['equis', 'i griega', 'efe', r'\bx\b', r'\bexis\b', r'\bce\b', r'\bc\b', r'\bb\b', r'\bbe\b', r'\bye\b',r'\bi\b', r'\bp\b', r'\bpe\b', r'\br\b', r'\bere\b']
set_names = [r'\blos enteros\b', r'\bz\b', r'\bzeta\b', r'\blos numeros enteros\b', r'\bnumeros enteros\b', r'\benteros\b', r'\bconjunto vacio\b', r'\bvacio\b']

bracket_rules = {
    'n1e1': {'r1': [(1, 2), (1, 3), (1, 4)], 'r2': [(2, 3), (1, 3)], 'r3': []},
    'n1e2': {'r1': [(2, 3)], 'r2': [(1, 2)], 'r3': [(1, 2), (1, 3)]},
    'n1e3': {'r1': [(1, 2), (1, 3)], 'r2': [(1, 2), (1, 3)], 'r3': [(3, 4), (1, 2)]},
    'n1e4': {'r1': [], 'r2': [], 'r3': [(2, 3)]},
    'n1e5': {'r1': [(1, 2)], 'r2': [(1, 2), (3, 4)], 'r3': []},
    'n2e1': {'r1': [(1, 2)], 'r2': [(1, 2)], 'r3': []},
    'n2e4': {'r1': [], 'r2': [(1, 2)], 'r3': [(2, 3)]}
}


class LanguageModel(object):

    def __init__(self, corpus_path='corpus/'):
        self.corpus_path = corpus_path
        self.parsed_responses_file = os.path.join(self.corpus_path, 'parsed_responses.txt')
        self.corpus_file = os.path.join(self.corpus_path, 'corpus.txt')
        self.summarized_corpus = os.path.join(self.corpus_path, 'summarized_corpus.txt')
        # model_data = os.path.join(os.getcwd(), "corpus", "model", "spanish.tagger")
        # jar_file = os.path.join(os.getcwd(), "corpus", "model", "stanford-postagger.jar")
        # self.spanish_postagger = StanfordPOSTagger(model_data, jar_file)

    def __analizing_csv_file(self, filename):
        self.csv_file = filename.split('\\')[-1].replace('.csv', '').lower()

    def __clean_response(self, response, response_i):
        pattern = r'[0-9]|' + '|'.join(number_names + constant_names + set_names)
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
        result = str.split()
        if rules and rules != [(-1, -1)]:
            str = str.replace('(', '').replace(')', '').replace('parentesis', '')
            words = str.split()
            indexes = [i for i, j in enumerate(words) if '$TERM$' in j]
            for rule in rules:
                begin, end = rule
                first, last = indexes[begin-1], indexes[end-1]
                words[first] = '(' + words[first]
                words[last] = words[last] + ')'
            words[0], words[-1] = '(' + words[0], words[-1] + ')'
            result = words
        if not result[0].startswith('(') and not result[-1].endswith(')'):
            result[0], result[-1] = '(' + result[0], result[-1] + ')'
        return ' '.join(result)

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
        csv_files = filter(lambda x: x.split('\\')[1].lower()[:-4] in bracket_rules.keys(), csv_files)
        with open(self.parsed_responses_file, 'w') as parsed_responses:
            for file in csv_files:
                responses = defaultdict(list)
                for row in csv.reader(open(file)):
                    self.__analizing_csv_file(file)
                    r1, r2, r3 = self._parse_csv_row(row).values()
                    responses['r1'] += r1
                    responses['r2'] += r2
                    responses['r3'] += r3
                parsed_responses.write('\n'.join(filter(lambda x: x != '', responses['r1'])) + '\n')
                parsed_responses.write('\n'.join(filter(lambda x: x != '', responses['r2'])) + '\n')
                parsed_responses.write('\n'.join(filter(lambda x: x != '', responses['r3'])) + '\n')

    def parse_corpus(self):
        with open(self.corpus_file, 'w') as corpus:
            parsed_responses = open(self.parsed_responses_file, 'r')
            terms = list()
            for line in parsed_responses.readlines():
                while line.rfind('(') != -1:
                    i = line.rfind('(')
                    j = line.find(')', i) + 1
                    terms.append(line[i: j])
                    line = line[:i] + '$TERM$' + line[j:]
            corpus.write('\n'.join(sorted(terms)))

    def summarize_corpus(self):
        corpus = open(self.corpus_file).readlines()
        summarized_data = defaultdict(int)
        with open(self.summarized_corpus, 'w') as s_corpus:
            for line in corpus:
                summarized_data[line] += 1
            s_corpus.write('\n'.join(["%s,%s" % (y, x.strip('\n')) for x, y in summarized_data.iteritems() ]))#if int(y)>5]))


    def __get_terms_from_transcription(self, transcription):
        result = []
        while transcription.rfind('(') != -1:
            i = transcription.rfind('(')
            j = transcription.find(')', i) + 1
            result.append(transcription[i: j])
            transcription = transcription[:i] + '$TERM$' + transcription[j:]
        return result

    def evaluate_transcription(self, transcription):
        if not os.path.exists(os.path.join(os.getcwd(), "corpus", "corpus.txt")):
            self.prepare_corpus()
            self.parse_corpus()
            self.summarize_corpus()
        corpus = open(self.corpus_file).readlines()
        terms = self.__get_terms_from_transcription(transcription)
        evaluation = 1.0
        for term in terms:
            evaluation *= corpus.count(term+'\n')/float(len(corpus))
        return evaluation * 4000000