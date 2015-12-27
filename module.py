import argparse
from configobj import ConfigObj
from mathml_client import SnuggleTexClient
from preprocessor import PreProcessor
from language_generator import LanguageGenerator


class TexToES(object):

    def __init__(self, latex, cmathml, filename, verbose):
        self.latex = latex
        self.cmathml = cmathml
        self.filename = filename
        self.verbose = verbose

    def process_input(self):
        if self.filename:
            self.__process_file()
        elif self.latex:
            self.__process_latex()
        elif self.cmathml:
            self.__process_cmathml()

    def __process_file(self):
        pass

    def __process_latex(self):
        snuggletex = SnuggleTexClient()
        mathml_string = snuggletex.latex_to_mathml(self.latex)
        self.__input_logging('LaTeX sring', self.latex)
        verb_generated = self.__process_cmathml(mathml_string)
        self.__output_logging(verb_generated)
        return verb_generated

    def __process_cmathml(self, mathml_string=None):
        if not mathml_string:
            mathml_string = self.cmathml
        p = PreProcessor()
        self.__input_logging('CMathML string', mathml_string)
        stack_constructor = p.process(mathml_string)
        if self.verbose:
            print stack_constructor
        lg = LanguageGenerator()
        verb_generated = lg.generate_sub_language(stack_constructor, self.verbose)
        self.__output_logging(verb_generated)
        return verb_generated

    def __input_logging(self, msg, input):
        print "++++++++++ Processing %s ++++++++++" % msg
        print "%s received:\n\t%s\n" % (msg, input)

    def __output_logging(self, output):
        print "\nOutput\n\t%s" % output
        print "+++++++++++++++++++++++++++++++++++++++++++++"


def evidence_writer(tex_formula, mathml, verb_result):
    evidence_file = ConfigObj("evidencia.txt")
    total_of_evidences = len(evidence_file)
    evidence_file['ejemplo_' + str(total_of_evidences)] = {}
    evidence_file['ejemplo_' + str(total_of_evidences)]['tex'] = tex_formula
    evidence_file['ejemplo_' + str(total_of_evidences)]['mathml'] = mathml
    evidence_file['ejemplo_' + str(total_of_evidences)]['verb'] = verb_result
    evidence_file.write()


def check_txt(file_arg):
    value = str(file_arg)
    if not value.endswith('.txt'):
        msg = "%s is not a valid file, must end with .txt" % value
        raise argparse.ArgumentTypeError(msg)
    return value


def check_tex(tex_arg):
    value = str(tex_arg)
    if not (value.startswith('$') or value.startswith('$')):
        msg = "%s is not a tex string, must start and end with '$'" % value
        raise argparse.ArgumentTypeError(msg)
    return value[1:-1]


def check_arguments(args):
    args_as_list = [args.filename, args.latex, args.cmathml]
    if args_as_list.count(None) == 3:
        msg = "No arguments, -h for help"
        raise argparse.ArgumentTypeError(msg)
    if not args_as_list.count(None) == 2:
        msg = "More than one args are passed, -h for help"
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='textoes transform tex/mathml input into spanish')
    parser.add_argument('-f', '--filename', type=check_txt, required=False,
                        help="A txt file latex content inside $..$ to convert into ES.")
    parser.add_argument('--latex', type=check_tex, required=False,
                        help="LaTeX code to convert into ES")
    parser.add_argument('--cmathml', type=str, required=False,
                        help="ContentMathML code to convert into ES")
    parser.add_argument('--verbose', type=bool, required=False, default=False)
    args = parser.parse_args()
    check_arguments(args)
    tte = TexToES(
        filename=args.filename,
        latex=args.latex,
        cmathml=args.cmathml,
        verbose=args.verbose
    )
    tte.process_input()
