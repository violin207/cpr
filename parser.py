from my_token import read_tokens_from_file, Token, Identifier, Integer, String, Float, Operator, Punctuation, Keyword, str_to_token_value, EndOfFileToken
from enum import Enum


class STATE(Enum):
    START = 1
    DECLA = 2
    FUNC_DEF = 3
    BLOCK_ST = 4
    ASS_ST = 5
    EP = 6
    IF_ST = 7
    WHILE_ST = 8
    FOR_ST = 9
    LOGC_EP = 10


class ParserStack():

    def __init__(self):
        self._stack = list()

    def is_empty(self):
        return len(self._stack) == 0

    def pop(self):
        return self._stack.pop()

    def top(self):
        if (self.is_empty()):
            return False  # Some handling so life is easier on if-condition
        return self._stack[len(self._stack) - 1]

    def push(self, x):
        self._stack.append(x)


class Parser():
    OP1 = [Operator.OPERATOR_DICT[x] for x in ['+', '-']]
    OP2 = [Operator.OPERATOR_DICT[x] for x in ['*', '/']]
    OP_OR = [Operator.OPERATOR_DICT['||'], Keyword.KEYWORD_DICT['or']]
    OP_AND = [Operator.OPERATOR_DICT['&&'], Keyword.KEYWORD_DICT['and']]
    OP_NOT = [Operator.OPERATOR_DICT['!'], Keyword.KEYWORD_DICT['not']]

    def __init__(self, pt: int, token_list: list[Token]):
        self.pt = pt
        self.token_list = token_list
        self.stack = ParserStack()

    def debug_print(self, expected: str | list[str]):
        if (self.is_end()):
            if (len(self.token_list) >= 1):
                print(
                    f'Parsing Error. {self.token_list[len(self.token_list)-1]} ^ Expected: {expected}'
                )
            else:
                print(f'Parsing Error. While the # of tokens is 0.')
        else:
            cur = self.cur()
            if (self.pt == 0):
                print(f'Parsing Error. ^ {cur} ... Expected: {expected}')
            else:
                print(
                    f'Parsing Error. {self.token_list[self.pt-1]} ^ {cur} ... Expected: {expected}'
                )

    def match(self, type: int) -> bool:
        if (self.is_end()):
            return False

        cur = self.cur()
        ret = cur.token_value == type
        if (ret):
            self.pt += 1  # NOTE For simplicity, move the pointer only if matched
        return ret

    def match_op(self, op_list: list[int]) -> bool:
        if (self.is_end()):
            return False

        cur = self.cur()
        ret = any(cur.token_value == op for op in op_list)
        if (ret):
            self.pt += 1  # NOTE For simplicity, move the pointer only if matched
        return ret

    # Recursive descent parse:

    def EP(self) -> bool:
        tmp = self.pt
        if (self.LOGIC_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.match(String.token_value)):
            return True

        self.pt = tmp
        self.debug_print('EP | MATH_EP | str')

        return False

    def LOGIC_EP(self) -> bool:
        tmp = self.pt
        if (self.LOGIC_EP_B() and self.LOGIC_EP_):
            return True

        self.pt = tmp
        self.debug_print('LOGIC_EP_B')

        return False

    def LOGIC_EP_(self) -> bool:
        tmp = self.pt
        if (self.match_op(self.OP_OR) and self.LOGIC_EP_B()
                and self.LOGIC_EP_()):
            return True

        self.pt = tmp
        return True

    def LOGIC_EP_B(self) -> bool:
        tmp = self.pt
        if (self.LOGIC_EP_C() and self.LOGIC_EP_B_()):
            return True

        self.pt = tmp
        self.debug_print('LOGIC_EP_C')

        return False

    def LOGIC_EP_B_(self) -> bool:
        tmp = self.pt
        if (self.match_op(self.OP_AND) and self.LOGIC_EP_C()
                and self.LOGIC_EP_B_()):
            return True

        self.pt = tmp
        return True

    def LOGIC_EP_C(self) -> bool:
        tmp = self.pt
        if (self.match_op(self.OP_NOT) and self.LOGIC_EP_C()):
            return True

        self.pt = tmp
        if (self.LOGIC_EP_D()):
            return True

        self.pt = tmp
        self.debug_print(f'{self.OP_NOT} | LOGIC_EP_D')

        return False

    def LOGIC_EP_D(self) -> bool:
        tmp = self.pt
        if (self.match(Punctuation.PUNCTUATION_DICT['(']) and self.LOGIC_EP()
                and self.match(Punctuation.PUNCTUATION_DICT[')'])):
            return True

        self.pt = tmp
        if (self.LOGIC_EP_E()):
            return True

        self.pt = tmp
        self.debug_print('( | LOGIC_EP_E')

        return False

    def LOGIC_EP_E(self) -> bool:
        tmp = self.pt
        if (self.MATH_EP() and self.match(Operator.OPERATOR_DICT['>'])
                and self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP() and self.match(Operator.OPERATOR_DICT['<'])
                and self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP() and self.match(Operator.OPERATOR_DICT['>='])
                and self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP() and self.match(Operator.OPERATOR_DICT['<='])
                and self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP() and self.match(Operator.OPERATOR_DICT['=='])
                and self.MATH_EP()):
            return True

        self.pt = tmp
        if (self.MATH_EP()):
            return True

        self.pt = tmp
        self.debug_print('MATH_EP')

        return False

    def MATH_EP(self) -> bool:
        tmp = self.pt
        if (self.TD() and self.MATH_EP_()):
            return True

        self.pt = tmp
        self.debug_print('TD')

        return False

    def MATH_EP_(self) -> bool:
        tmp = self.pt
        if (self.match_op(self.OP1) and self.TD() and self.MATH_EP_()):
            return True

        self.pt = tmp
        return True

    def TD(self) -> bool:
        tmp = self.pt
        if (self.TERM() and self.TD_()):
            return True

        self.pt = tmp
        self.debug_print('TERM')

        return False

    def TD_(self) -> bool:
        tmp = self.pt
        if (self.match_op(self.OP2) and self.TERM() and self.TD_()):
            return True

        self.pt = tmp
        return True

    def TERM(self) -> bool:
        tmp = self.pt
        if (self.match(Identifier.token_value)):
            return True

        self.pt = tmp
        if (self.match(Integer.token_value)):
            return True

        self.pt = tmp
        if (self.match(Float.token_value)):
            return True

        self.pt = tmp
        if (self.match(Punctuation.PUNCTUATION_DICT['(']) and self.MATH_EP()
                and self.match(Punctuation.PUNCTUATION_DICT[')'])):
            return True

        self.pt = tmp
        self.debug_print('id | intc | real | (')

        return False

    # Another approach starts here
    """
    DECLA → TYPE VAR_LIST ;
    VAR_LIST → VAR VAR_LIST'
    VAR_LIST' → , VAR VAR_LIST' | ɛ
    VAR → id VAR'
    VAR' → INITIAL | [ intc ]
    INITIAL → = EP | ɛ
    """

    def DECLA(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending.')
        else:
            cur = self.cur()
            if (isinstance(cur, Keyword) and cur.is_type()):
                if not self.TYPE():
                    return False
                if not self.VAR_LIST():
                    return False
                if not self.match(str_to_token_value(';')):
                    self.debug_print(';')
                    return False
                return True
        return False

    def VAR_LIST(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                if not self.VAR():
                    return False
                if not self.VAR_LIST_():
                    return False
                return True
            else:
                self.debug_print('id')
        return False

    def VAR_LIST_(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                if not self.match(str_to_token_value(',')):
                    return False
                if not self.VAR():
                    return False
                if not self.VAR_LIST_():
                    return False
                return True
            elif (cur.token_value == str_to_token_value(';')):
                return True
            else:
                self.debug_print(', | ;')
        return False

    def VAR(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                if not self.match(Identifier.token_value):
                    # self.debug_print('id')
                    return False
                if not self.VAR_():
                    return False
                return True
            else:
                self.debug_print('id')
        return False

    def VAR_(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                if not (self.INITIAL()):
                    return False
                return True
            elif (cur.token_value == str_to_token_value(';')):
                if not (self.INITIAL()):
                    return False
                return True
            elif (cur.token_value == str_to_token_value('=')):
                if not (self.INITIAL()):
                    return False
                return True
            elif (cur.token_value == str_to_token_value('[')):
                if not (self.match(str_to_token_value('['))):
                    return False
                if not self.match(Integer.token_value):
                    return False
                if not self.match(str_to_token_value(']')):
                    self.debug_print(']')
                    return False
                return True
            else:
                self.debug_print(', | ; | = | [')

        return False

    def INITIAL(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                return True
            elif (cur.token_value == str_to_token_value(';')):
                return True
            elif (cur.token_value == str_to_token_value('=')):
                if not self.match(str_to_token_value('=')):
                    return False
                if not self.EP():
                    return False
                return True
            else:
                self.debug_print(', | ; | =')
        return False

    def TYPE(self) -> bool:
        assert (self.match_type())  # It should always pass
        return True

    def cur(self) -> Token:
        if (self.is_end()):
            return EndOfFileToken()
        return self.token_list[self.pt]

    def is_end(self) -> bool:
        return self.pt >= len(self.token_list)

    def match_type(self):
        if (self.is_end()):
            return False

        cur = self.cur()
        if not isinstance(cur, Keyword):
            return False

        ret = cur.is_type()

        if ret:
            self.pt += 1
        return ret

    def BLOCK_ST(self) -> bool:
        accept = False
        while (not accept):
            cur = self.cur()
            if self.match(str_to_token_value('return')):
                self.stack.push('return')

                if (self.EP()):
                    self.stack.push('EP')
                else:
                    # print('Expected: EP')
                    return False

                if (self.match(str_to_token_value(';'))):
                    self.stack.push(';')
                else:
                    self.debug_print(';')
                    return False

            elif self.match(Identifier.token_value):
                self.stack.push('id')
                if self.match(str_to_token_value('=')):
                    self.stack.push('=')
                else:
                    self.debug_print('=')
                    return False

                if self.EP():
                    self.stack.push('EP')
                else:
                    # print('Expected: EP')
                    return False

                if (self.match(str_to_token_value(';'))):
                    self.stack.push(';')
                else:
                    self.debug_print(';')
                    return False

            elif self.match(str_to_token_value('while')):
                self.stack.push('while')

                if self.match(str_to_token_value('(')):
                    self.stack.push('(')
                else:
                    self.debug_print('(')
                    return False

                if self.EP():
                    self.stack.push('EP')
                else:
                    print('Expected: EP')
                    return False

                if self.match(str_to_token_value(')')):
                    self.stack.push(')')
                else:
                    self.debug_print(')')
                    return False

                if self.match(str_to_token_value('{')):
                    self.stack.push('{')
                else:
                    self.debug_print('{')
                    return False

                if (self.BLOCK_ST()):
                    self.stack.push('BLOCK_ST')
                else:
                    # print('Expected: BLOCK_ST')
                    return False

                if (self.match(str_to_token_value('}'))):
                    self.stack.push('}')
                else:
                    self.debug_print('}')
                    return False
            # Do LL(1) Top-Down here
            elif (isinstance(cur, Keyword) and cur.is_type()):
                if (not self.DECLA()):
                    return False
                self.stack.push('DECLA')
            elif (cur.token_value == str_to_token_value('if')):
                if (not self.IF_ST()):
                    return False
                self.stack.push('IF_ST')
            elif (cur.token_value == str_to_token_value('for')):
                if (not self.FOR_ST()):
                    return False
                self.stack.push('FOR_ST')

            elif (self.stack.top() == ';'):
                # Reduce 'RETURN_ST -> . return EP ;' and 'ASS_ST -> id = EP ;'
                self.stack.pop()
                if (self.stack.top() == 'EP'):
                    self.stack.pop()
                    if (self.stack.top() == 'return'):
                        self.stack.pop()
                        self.stack.push('RETURN_ST')
                    elif (self.stack.top() == '='):
                        self.stack.pop()
                        if (self.stack.top() == 'id'):
                            self.stack.pop()
                            self.stack.push('ASS_ST')

            elif (self.stack.top() == 'RETURN_ST'
                  ):  # Reduce STATM -> RETURN_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'ASS_ST'):  # Reduce STATM -> ASS_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'DECLA'):  # Reduce STATM -> DECLA
                self.stack.pop()
                self.stack.push('STATM')
            elif (self.stack.top() == 'IF_ST'):  # Reduce STATM -> IF_ST
                self.stack.pop()
                self.stack.push('STATM')
            elif (self.stack.top() == 'FOR_ST'):  # Reduce STATM -> FOR_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'WHILE_ST'):  # Reduce STATM -> WHILE_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (
                    self.stack.top() == 'STATM'
            ):  # Reduce 'BLOCK_ST -> BLOCK_ST STATM' and 'BLOCK_ST -> STATM'
                self.stack.pop()
                if (not self.stack.is_empty()
                        and self.stack.top() == 'BLOCK_ST'):
                    self.stack.pop()
                    self.stack.push('BLOCK_ST')
                else:
                    self.stack.push('BLOCK_ST')

            elif self.stack.top() == 'BLOCK_ST':  # Reduce 'S -> BLOCK_ST
                self.stack.pop()
                self.stack.push('S')

            elif (self.stack.top() == 'S'):  # Accept
                self.stack.pop()
                accept = True
            else:
                print(
                    'Error happens in Bottom-Up parsing. Failed to reduce or shift with current state.'
                )
                print('Stack: ')
                while (not self.stack.is_empty()):
                    print(self.stack.pop())

                self.debug_print('BLOCK_ST')
                return False

        return True

    def IF_ST(self) -> bool:
        if not self.match(str_to_token_value('if')):
            self.debug_print('if')
            return False
        if not self.match(str_to_token_value('(')):
            self.debug_print('(')
            return False
        if not self.EP():
            # self.debug_print('EP')
            return False
        if not self.match(str_to_token_value(')')):
            self.debug_print(')')
            return False
        if not self.match(str_to_token_value('{')):
            self.debug_print('{')
            return False
        if not self.BLOCK_ST():
            # self.debug_print('BLOCK_ST')
            return False
        if not self.match(str_to_token_value('}')):
            self.debug_print('}')
            return False
        if not self.ELSE_ST():
            # self.debug_print('ELSE_ST')
            return False
        return True

    def ELSE_ST(self) -> bool:
        if (not self.match(str_to_token_value('else'))):
            return True
        else:
            if (not self.match(str_to_token_value('{'))):
                self.debug_print('{')
                return False
            if (not self.BLOCK_ST()):
                # self.debug_print('BLOCK_ST')
                return False
            if (not self.match(str_to_token_value('}'))):
                self.debug_print('}')
                return False
            return True
        return True

    def FOR_ST(self) -> bool:
        if not self.match(str_to_token_value('for')):
            self.debug_print('for')
            return False
        if not self.match(str_to_token_value('(')):
            self.debug_print('(')
            return False
        if not self.VAR():
            # self.debug_print('VAR')
            return False
        if not self.match(str_to_token_value(';')):
            self.debug_print(';')
            return False
        if not self.EP():
            # self.debug_print('EP')
            return False
        if not self.match(str_to_token_value(';')):
            self.debug_print(';')
            return False
        if not self.ASS_ST():
            # self.debug_print('ASS_ST')
            return False
        if not self.match(str_to_token_value(')')):
            self.debug_print(')')
            return False
        if not self.match(str_to_token_value('{')):
            self.debug_print('{')
            return False
        if not self.BLOCK_ST():
            # self.debug_print('BLOCK_ST')
            return False
        if not self.match(str_to_token_value('}')):
            self.debug_print('}')
            return False
        return True

    def ASS_ST(self) -> bool:
        if not self.match(Identifier.token_value):
            self.debug_print('id')
            return False
        if not self.match(str_to_token_value('=')):
            self.debug_print('=')
            return False
        if not self.EP():
            return False
        return True

    # LAST PART
    def START(self) -> bool:
        tmp = self.pt
        if (self.EX_DECLA() and self.START_()):
            return True

        self.pt = tmp
        self.debug_print('EX_DECLA')
        return False

    def START_(self) -> bool:
        tmp = self.pt
        if (self.EX_DECLA() and self.START_()):
            return True

        self.pt = tmp
        return True

    def EX_DECLA(self) -> bool:
        tmp = self.pt
        if (self.DECLA()):
            return True

        self.pt = tmp
        if (self.FUNC_DEF()):
            return True

        self.pt = tmp
        self.debug_print('DECLA | FUNC_DEF')

        return False

    def FUNC_DEF(self) -> bool:
        tmp = self.pt
        if (self.match_type() and self.match(Identifier.token_value)
                and self.match(str_to_token_value('('))
                and self.match(str_to_token_value(')'))
                and self.match(str_to_token_value('{')) and self.BLOCK_ST()
                and self.match(str_to_token_value('}'))):
            return True

        self.pt = tmp
        self.debug_print('TYPE')

        return False


if __name__ == '__main__':
    from pathlib import Path

    def func1():
        tokens = read_tokens_from_file(Path('output', 'output7.txt'))
        parser = Parser(0, tokens)
        print(parser.DECLA(), parser.pt)

    def func2():
        tokens = read_tokens_from_file(Path('output', 'output8.txt'))
        parser = Parser(0, tokens)
        print(parser.BLOCK_ST())

    def func3():
        tokens = read_tokens_from_file(Path('output', 'output9.txt'))
        parser = Parser(0, tokens)
        print(parser.DECLA())

    def func4():
        tokens = read_tokens_from_file(Path('output', 'output11.txt'))
        parser = Parser(0, tokens)
        print(parser.BLOCK_ST())

    def func5():
        tokens = read_tokens_from_file(Path('output', 'output.txt'))
        parser = Parser(0, tokens)
        print(parser.START())

    func5()
