import inspect
from typing import List, Dict, Set, Any


class Func2Pyx:

    def __init__(self, output_file):
        self.output_file = output_file
        self._mappings = {int: 'int', str: 'str', float: 'float'}

    def _get_from_mapping(self, arg_type):
        if arg_type not in self._mappings:
            if issubclass(arg_type, List):
                return 'list'
            if issubclass(arg_type, Dict):
                return 'dict'
            if issubclass(arg_type, Set):
                return 'set'
            if issubclass(arg_type, Any):
                return ''
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

    def pyfunc_to_pyx(self, target):
        code = self._get_annotations(target)
        code = self._get_function_body(target, code)
        self._save_file(code)

    def _save_file(self, code):
        with open(self.output_file, 'a') as fp:
            fp.write(code)


if __name__ == '__main__':
    def add(x: int, y: int) -> int:
        return x + y

    def add3(x: int, y: int, z) -> int:
        return x + y + z

    def add4(x: List[int]) -> int:
        return sum(x)

    def add5(x: Dict[str, int]) -> int:
        count = 0
        for v in x.values():
            count += v
        return count

    f = Func2Pyx('blah.pyx')
    f.pyfunc_to_pyx(add)

    f.pyfunc_to_pyx(add4)
    f.pyfunc_to_pyx(add5)