from configobj import ConfigObj
from os import path


class LanguageGenerator(object):

    def generate_sub_language(self, stack, logging=False):
        self.replace_constants(stack)
        while 'apply' in stack:
            i, j, temp_stack, operator, arity, key_op = self.get_operator(stack)
            stack = stack[:i] + [self.replace_values(key_op, operator, arity, temp_stack[2:])] + stack[j+1:]
            if logging:
                print stack
        assert len(stack) == 1
        return stack[0]

    def get_operator(self, stack):
        i = self.rindex(stack, 'apply')
        j = stack.index('end-apply', i)
        temp_stack = stack[i:j]
        key_op = temp_stack[1]
        config = self.get_language_template()
        operator = config['template'][key_op]
        arity = len(temp_stack) - 2
        return i, j, temp_stack, operator, arity, key_op

    @staticmethod
    def rindex(list_o, elem):
        return len(list_o) - list(reversed(list_o)).index(elem) - 1

    @staticmethod
    def prepare_operator(key_op, operator, values):
        arity = len(values)
        if key_op == 'sum' or key_op == 'product':
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
        elif key_op == 'max' or key_op == 'min':
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
            i = values.index('bvar')
            operator = operator.replace('$bvar$', values[i+1])
            values.remove(values[i+1])
            values.remove('bvar')
            i = values.index('condition')
            operator = operator.replace('$condition$', values[i+1])
            values.remove(values[i+1])
            values.remove('condition')
            arity -= 4
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
            return '(' + result.replace("$OP1$", '').replace("$OP2$", values[0]) + ')'
        elif arity == 2:
            return '(' + result.replace("$OP1$", values[0]).replace("$OP2$", values[1]) + ')'
        elif arity >= 3:
            new_operator = result.replace("$OP1$", values[0]).replace("$OP2$", operator)
            return self.replace_values(key_op, new_operator, arity - 1, values[1:])

    def replace_constants(self, stack):
        config = self.get_language_template()
        for constant in ['integers', 'emptyset']:
            if constant in stack:
                c_tr = config['template'][constant]
                i = stack.index(constant)
                stack.insert(i, c_tr)
                stack.remove(constant)

    @staticmethod
    def get_language_template():
        location_file = path.join(path.dirname(__file__), 'language.template')
        return ConfigObj(location_file)