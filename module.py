from configobj import ConfigObj
from mathml_client import SnuggleTexClient
from preprocessor import PreProcessor
from language_generator import LanguageGenerator

mathml_string = ""
mathml_string = mathml_string.replace('\n', '').replace('ci ', 'ci&').replace(' ', '').replace('ci&', 'ci ')
tex_form = "x^{ab}"


def evidence_writer(tex_formula, mathml, verb_result):
    evidence_file = ConfigObj("evidencia.txt")
    total_of_evidences = len(evidence_file)
    evidence_file['ejemplo_' + str(total_of_evidences)] = {}
    evidence_file['ejemplo_' + str(total_of_evidences)]['tex'] = tex_formula
    evidence_file['ejemplo_' + str(total_of_evidences)]['mathml'] = mathml
    evidence_file['ejemplo_' + str(total_of_evidences)]['verb'] = verb_result
    evidence_file.write()


def verbalizer(mathml, logging=False):
    p = PreProcessor()
    stack_constructor = p.process(mathml)
    if logging:
        print stack_constructor
    lg = LanguageGenerator()
    verb_generated = lg.generate_sub_language(stack_constructor, logging)
    return verb_generated


if __name__ == '__main__':
    snuggletex = SnuggleTexClient()
    print tex_form
    string = snuggletex.latex_to_mathml(tex_form)
    verb_generated = verbalizer(string, False)
    print verb_generated
    #evidence_writer(tex_form, string, verb_generated)
