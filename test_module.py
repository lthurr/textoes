import unittest
from configobj import ConfigObj
from module import verbalizer
from mathml_client import SnuggleTexClient


class KnownGood(unittest.TestCase):

    def __init__(self, example_id, input, output):
        super(KnownGood, self).__init__()
        self.input = input
        self.output = output
        self.example_id = example_id

    def runTest(self):
        self.__name__ = 'test_example_%d' % self.example_id
        self.assertEqual(verbalizer(self.input), self.output)


def suite():
    suite = unittest.TestSuite()
    evidence_file = ConfigObj("evidencia.txt")
    total_evidences = len(evidence_file)
    for i in range(total_evidences):
        ejemplo = 'ejemplo_%d' % i
        mathml = evidence_file[ejemplo]['mathml']
        verbalized_text = evidence_file[ejemplo]['verb']
        suite.addTest(KnownGood(i, mathml, verbalized_text))
    return suite


def tex_suite():
    suite = unittest.TestSuite()
    evidence_file = ConfigObj("evidencia.txt")
    total_evidences = len(evidence_file)
    snuggletex = SnuggleTexClient()
    for i in range(total_evidences):
        ejemplo = 'ejemplo_%d' % i
        tex_form = evidence_file[ejemplo]['tex']
        print tex_form
        try:
            mathml = snuggletex.latex_to_mathml(tex_form)
            verbalized_text = evidence_file[ejemplo]['verb']
            suite.addTest(KnownGood(i, mathml, verbalized_text))
        except AttributeError:
            print "Error: " + str(tex_form)
            continue
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())