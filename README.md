# py2pyx
Cython supports both a number of Python and C types in it's type annotation system. This simple script uses Python3's type annotation system
to annotate functions with Python types. While this doesn't give the speed boasts from using C type's it plays easier with Python and can be 
done using code generation and simple inspection of Python3 code.

## Example Usage
```python3
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
```
This will generate a .pyx file which will have correctly typed Python code which can then be compiled with Cython's cythonize command. With no
human re-writting of code. 
```python3
# Generated Cython code
cpdef int add(int x, int y,):
        return x + y

cpdef int add3(int x, int y, z,):
        return x + y + z

cpdef int add4(list x,):
        return sum(x)

cpdef int add5(dict x,):
        count = 0
        for v in x.values():
            count += v
        return count


```
## Example Usage - Inline Type Detection
```python
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
```