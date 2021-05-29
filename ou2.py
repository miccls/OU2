"""
Solutions to module 2 - A calculator
Student: Martin Svärdsjö
Mail: martincsvardsjo@gmail.com
Reviewed by: Oskar Tegby
Reviewed date: 7 - 4 - 2021
"""


from tokenize import TokenError
from p2tokenizer import TokenizeWrapper
import math
import statistics
import sys
sys.path.append(
    '/Users/martinsvardsjo/Desktop/Kod/Python/Prog II/OU1')
import ou1


class SyntaxError(Exception):
    def __init__(self, arg):
        self.arg = arg

        

class Calculator:
    '''Using a class to extend scope of 
    some variables to the methods of controlling 
    the calculator instead of storing them globally
    or making new ones every time a metod runs.
    '''

    funcs = {
        'sin' : math.sin,
        'cos' : math.cos,
        'tan' : math.tan,
        'log' : lambda x: math.log(x, 10),
        'log2' : lambda x: math.log(x, 2),
        'ln' : lambda x: math.log(x, math.e),
        'fib' : ou1.fib_mem,
        'fac' : math.factorial,
        'exp' : math.exp,
    }

    # Special functions that take a list
    list_funcs = {
        'mean' : statistics.mean,
        'min' : min,
        'max' : max,
        'sum' : sum
    }

    def __init__(self):
        # Will also be used to store personal variables
        self.consts = {
            'PI' : math.pi,
            'E' : math.e,
            'ans' : 0
        }
        # Available commands.
        self.commands = {
            'quit' : lambda wtok: False,
            'file' : self.readFromFile,
            'vars' : self.displayVars,
        }


    def expression(self, wtok):
        '''Defining mathematical expressions'''
        result = self.term(wtok)
        end = False if wtok.get_current() in ['+', '-'] else True

        while not end:
            if wtok.get_current() == '+':
                wtok.next()
                result = result + self.term(wtok)
            elif wtok.get_current() == '-':
                wtok.next()
                result = result - self.term(wtok)
            else:
                end = True
        
        return result

    def assignVar(self, wtok):
        '''Assigns value to a variable,
        unnecessary to check if name
        as it would not have reached this code
        if not'''
        name = wtok.get_previous()
        wtok.next()
        self.consts[name] = self.expression(wtok)
        return self.consts[name]


    def displayVars(self, wtok):
        '''Taking wtok just to be able to
        step to the next.
        '''
        for key, value in self.consts.items():
            print('\t', key, ': ', value)
        wtok.next()
        # Keep running the calculator
        return True

    def term(self, wtok):
        '''Defining mathematical terms'''
        result = self.factor(wtok)
        while wtok.get_current() in ['*', '/']:
            if wtok.get_current() == '*':
                wtok.next()
                result = result * self.factor(wtok)
            elif wtok.get_current() == '/':
                wtok.next()
                try:
                    result = result / self.factor(wtok)
                except ZeroDivisionError:
                    # To catch accidental division by zero
                    raise SyntaxError('Illegal division by zero')
        return result


    def resultFromName(self, wtok):
        '''Gets desired result from a 
        variable or function in given line.
        '''
        if wtok.get_current() in self.funcs:
                func = self.funcs[wtok.get_current()]
                wtok.next()
                result = func(float(self.expression(wtok)))
            # Handling constants
        elif wtok.get_current() in self.list_funcs:
            func = self.list_funcs[wtok.get_current()]
            wtok.next()
            result = func(self.makeList(wtok))
        
        elif wtok.get_current() in self.consts:
            result = self.consts[wtok.get_current()]
            wtok.next()
        else:
            wtok.next()
            if wtok.get_current() == '=':
                result = self.assignVar(wtok)
            else:
                raise SyntaxError('Unrecognized function or variable')
        return result

    def makeList(self, wtok):
        if wtok.get_current() == '(':
            wtok.next()
            returnList = [float(wtok.get_current())]
            wtok.next()
            while wtok.get_current() == ',':
                wtok.next()
                returnList.append(float(wtok.get_current()))
                wtok.next()
        else:
            raise SyntaxError('Expected argument')
        # Skip over ending parenthesis
        wtok.next()
        return returnList

    def factor(self, wtok):
        '''Defining a mathematical factor'''
        if wtok.get_current() == '(':
            wtok.next()
            result = self.expression(wtok)
            if wtok.get_current() == ')':
                wtok.next()
            else:
                raise SyntaxError("Expected ')'")
        elif wtok.is_number():
            result = float(wtok.get_current())
            wtok.next()
        # Efter låt gå in här om det är ett namn.
        # Avgör vilken typ av namn och om inget passar -> raise Error.
        # Unrecognized variable or function.
        elif wtok.is_name():
            result = self.resultFromName(wtok)

        elif wtok.get_current() in ['+', '-']:
            # If expression started by a sign, multiply sign
            # by following factor.
            sign = wtok.get_current()
            wtok.next()
            result = int(sign + '1')*self.factor(wtok)

        else:
            raise SyntaxError('Expected number or (')
        return result

    def readFromFile(self, wtok):
        wtok.next()
        file_path = ''
        while wtok.has_next():
            file_path += wtok.get_current()
            wtok.next()
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            # Using recursion here.
            status = self.process_line(line)
        # In order to be able to quit from text file
        return status

    def process_line(self, line):
        '''Processes an input line and
        determines what factors, terms, expressions 
        and commands it contains'''
        wtok = TokenizeWrapper(line)
        try:
            if wtok.get_current() in self.commands:
                return self.commands[wtok.get_current()](wtok)

            else:
                result = self.expression(wtok)
                if wtok.is_at_end():
                    print('Result: ', result)
                    self.consts['ans'] = result
                else:
                    raise SyntaxError('Unexpected token')

        except SyntaxError as se:
            print("*** Syntax: ", se.arg)
            print(f"Error ocurred at '{wtok.get_current()}'" +
                f" just after '{wtok.get_previous()}'")

        except TokenError:
            print('*** Syntax: Unbalanced parentheses')
        # Saving last calculated result.

        except ValueError as e:
            print(e)

        return True


def main():
    print("Calculator version 0.1")
    cl = Calculator()
    while True:
        line = input("Input : ")
        status = cl.process_line(line)
        if not status:
            break

    print('Bye!')


if __name__ == "__main__":
    main()