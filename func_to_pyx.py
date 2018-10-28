import inspect
from typing import List, Dict, Set, NewType


Long = NewType('Long', int)
Double = NewType('Double', float)
LongDouble = NewType('LongDouble', float)


class Func2Pyx:

    def __init__(self):
        self.all_args = set()
        self._mappings = {int: 'int', str: 'str', float: 'float', set: 'set', list: 'list'}

    def _get_from_mapping(self, arg_type):
        typing_types = [(List, 'list'), (Dict, 'dict'), (Set, 'set')]
        c_types = {'Long': 'long', 'Double': 'double', 'LongDouble': 'long double', 'Dict': 'dict', 'List': 'list'}
        if arg_type not in self._mappings:
            if callable(arg_type):
                arg_name = arg_type.__name__
                if arg_name in c_types:
                    return c_types[arg_name]
                return ''
            for t in typing_types:
                if issubclass(arg_type, t[0]):
                    return t[1]
            return ''
        return self._mappings.get(arg_type)

    def _get_annotations(self, target) -> str:
        code = ''
        args = []
        result = inspect.getfullargspec(target)
        name = target.__name__
        arguments = result.args
        annotations = result.annotations
        if 'return' in annotations:
            return_type = self._get_from_mapping(annotations['return'])
            annotations.pop('return')
        else:
            return_type = None
        for arg in arguments:
            if arg in annotations:
                value = annotations[arg]
                args.append('{} {},'.format(self._get_from_mapping(value), arg))
            else:
                args.append('{},'.format(arg))
            self.all_args.add(arg)
        if return_type:
            code += 'cpdef {return_type} {name}({args}):\n'.format(return_type=return_type, name=name,
                                                                        args=' '.join(args))
        else:
            code += 'cpdef {name}({args}):\n'.format(name=name, args=' '.join(args))
        return code

    def _get_function_body(self, target, code: str) -> str:
        lines = inspect.getsource(target)
        lines = lines.split('\n')
        for line in lines[1:]:
            code += '{}\n'.format(line)
        return code

    def pyfunc_to_pyx(self, target, output_file):
        code = self._get_annotations(target)
        code = self._get_function_body(target, code)
        self._save_file(code, output_file)

    def _save_file(self, code, output_file):
        with open(output_file, 'a') as fp:
            fp.write(code)


if __name__ == '__main__':

    def add(x: int, y: int) -> int:
        return x + y

    def add3(x: int, y: int, z) -> int:
        return x + y + z

    def add4(x: List[int]) -> int:
        return sum(x)

    def add5(x: Dict[str, int]) -> Long:
        count = 0
        for v in x.values():
            count += v
        return count

    def add6(x: Dict) -> Long:
        return 100

    f = Func2Pyx()
    f.pyfunc_to_pyx(add, 'blah.pyx')
    f.pyfunc_to_pyx(add3, 'blah.pyx')
    f.pyfunc_to_pyx(add4, 'blah.pyx')
    f.pyfunc_to_pyx(add5, 'blah.pyx')
    f.pyfunc_to_pyx(add6, 'blah.pyx')