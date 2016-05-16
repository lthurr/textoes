from configobj import ConfigObj
from os import path
import re


class LanguageGenerator(object):

    def generate_sub_language(self, stack, logging=False):
        self.replace_constants(stack)
        self.reorganize(stack)
        while 'apply' in stack:
            i, j, temp_stack, operator, arity, key_op = self.get_operator(stack)
            stack = stack[:i] + [self.replace_values(key_op, operator, arity, temp_stack[2:])] + stack[j+1:]
            if logging:
                print stack
        assert len(stack) == 1
        return stack[0]

    def reorganize(self, stack):
        if 'inverse' in stack:
            i = stack.index('inverse')
            stack[i-1], stack[i] = stack[i], stack[i-1]
            j = stack.index('function')
            i = stack.index('end-apply', j)
            stack[i + 1], stack[i] = stack[i], stack[i + 1]

    def get_operator(self, stack):
        i = self.__rindex(stack, 'apply')
        j = stack.index('end-apply', i)
        temp_stack = stack[i:j]
        key_op = temp_stack[1]
        if key_op not in self.get_valids_operators_from_template():
            raise NotImplementedError('%s is not implemented' % key_op)
        config = self.get_language_template()
        operator = config['template'][key_op]
        arity = len(temp_stack) - 2
        if isinstance(operator, list):
            for op in operator:
                if op.count('$')/2 == arity:
                    operator = op
                    break
        return i, j, temp_stack, operator, arity, key_op

    @staticmethod
    def __rindex(list_o, elem):
        return len(list_o) - list(reversed(list_o)).index(elem) - 1

    @staticmethod
    def prepare_operator(key_op, operator, values):
        arity = len(values)
        if key_op in ['sum', 'product']:
            i = values.index('bvar')
            operator = operator.replace('$bvar$', values[i+1])
            values.remove(values[i+1])
            values.remove('bvar')
            if 'lowlimit' in values:
                i = values.index('lowlimit')
                operator = operator.replace('$lowlimit$', values[i+1])
                values.remove(values[i+1])
                values.remove('lowlimit')
                i = values.index('uplimit')
                operator = operator.replace('$uplimit$', values[i+1])
                values.remove(values[i+1])
                values.remove('uplimit')
                arity -= 6
            elif 'condition' in values:
                i = values.index('condition')
                operator = operator.replace('')
                # TODO Fix here
        elif key_op in ['max', 'min']:
            values = [' '.join(values)]
            arity = 1
        elif key_op == 'limit':
            i = values.index('bvar')
            operator = operator.replace('$bvar$', values[i+1])
            values.remove(values[i+1])
            values.remove('bvar')
            i = values.index('lowlimit')
            operator = operator.replace('$lowlimit$', values[i+1])
            values.remove(values[i+1])
            values.remove('lowlimit')
            arity -= 4
        elif key_op == 'log':
            if 'logbase' in values:
                i = values.index('logbase')
                operator = operator.replace('$base$', 'base ' + values[i+1])
                values.remove(values[i+1])
                values.remove('logbase')
                arity -= 2
            else:
                operator = operator.replace('$base$ ', '')
        elif key_op == 'set':
            if 'bvar' in values:
                operator = operator[0]
                i = values.index('bvar')
                operator = operator.replace('$bvar$', values[i+1])
                values.remove(values[i+1])
                values.remove('bvar')
                i = values.index('condition')
                operator = operator.replace('$condition$', values[i+1])
                values.remove(values[i+1])
                values.remove('condition')
                arity -= 4
            else:
                operator = operator[1]
                values = [', '.join(values)]
                arity = 1
        elif key_op == 'root':
            if 'degree' in values:
                i = values.index('degree')
                operator = operator.replace('$degree$', values[i+1])
                values.remove(values[i+1])
                values.remove('degree')
                arity -= 2
            else:
                operator = operator.replace('$degree$', 'cuadrada')
        return operator, values, arity

    def replace_values(self, key_op, operator, arity, values):
        assert arity == len(values), "There is more values to unpack"
        result, values, arity = self.prepare_operator(key_op, operator, values)
        if arity == 1:
            return '(' + result.replace("$VAR$", values[0]) + ')'
        elif arity == 2:
            result = re.sub(r'(\$VAR\$)', values[0], result, count=1)
            result = re.sub(r'(\$VAR\$)', values[1], result, count=1)
            return '(' + result + ')'
        elif arity >= 3:
            result = re.sub(r'(\$VAR\$)', values[0], result, count=1)
            new_operator = re.sub(r'(\$VAR\$)', operator, result, count=1)
            return self.replace_values(key_op, new_operator, arity - 1, values[1:])

    def replace_constants(self, stack):
        config = self.get_language_template()
        for constant in ['INTEGERS', 'emptyset', 'imaginaryi']:
            if constant in stack:
                c_tr = config['template'][constant.lower()]
                i = stack.index(constant)
                stack.insert(i, c_tr)
                stack.remove(constant)

    @staticmethod
    def get_language_template():
        location_file = path.join(path.dirname(__file__), 'language.template')
        return ConfigObj(location_file)

    def get_valids_operators_from_template(self):
        config = self.get_language_template()
        return config['template'].keys()
