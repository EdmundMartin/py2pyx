from collections import defaultdict
from typing import Any, List
import sys

from func_to_pyx import Func2Pyx

stored_values = defaultdict(lambda: [])


class VariableRecord:

    def __init__(self, variable_name: str):
        self.var_name = variable_name
        self.var_values = []

    def set_value(self, line_no: int, value: Any):
        self.var_values.append((line_no, value))


def traceit(frame, event, arg):
    if event == 'line':
        values = frame.f_locals.items()
        for var in values:
            stored_values[var[0]].append(var[1])
    return traceit


def no_trace(*args, **kwargs): pass


def determine_int_ctype(k, values: List[int]):
    if all(i < 32_767 and i > -32_767 for i in values):
        return '        cdef int {}\n'.format(k)
    return '        cdef long {}\n'.format(k)


def determine_float_ctype(k, values):
    if all(i >= -3.4E+38 and i <= -3.4E+38  for i in values):
        return '        cdef float {}\n'.format(k)
    if all(i >= -1.7E+308 and i <= +1.7E+308 for i in values):
        return '        cdef double {}\n'.format(k)
    else:
        return '        cdef long double {}\n'.format(k)


def typed_values(results: dict) -> List[str]:
    cdef_lines = []
    for k, v in results.items():
        if all(type(i) is int for i in v):
            cdef_lines.append(determine_int_ctype(k, v))
        if all(type(i) is float for i in v):
            cdef_lines.append(determine_float_ctype(k, v))
    return cdef_lines


def py2cy(output_file, func, *args, **kwargs):
    sys.settrace(traceit)
    func(*args, **kwargs)
    sys.settrace(no_trace)
    global stored_values
    values = stored_values
    annotator = Func2Pyx()
    annotations = annotator._get_annotations(func)
    for arg in annotator.all_args:
        values.pop(arg)
    value_with_types = typed_values(values)
    for val in value_with_types:
        annotations += val
    full_func = annotator._get_function_body(func, annotations)
    with open(output_file, 'a') as out_file:
        out_file.write(full_func)
    stored_values = defaultdict(lambda: [])


if __name__ == '__main__':
    def addit(x: int, y: int):
        z = 12
        return x + y + z

    def floater(x: float, y: float):
        g = 12.57
        h = 12.67
        return x + g, y + h
    py2cy('blah.pyx', addit, 10, 12)
    py2cy('blah.pyx', floater, 10.1, 12.12)