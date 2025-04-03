from my_token import read_tokens_from_file, Token, Identifier, Integer, String, Float, Operator, Punctuation, Keyword, str_to_token_value
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

    def match(self, type: int) -> bool:
        if (self.is_end()):
            return False

        cur = self.cur()
        ret = cur.token_value == type
        self.pt += 1
        return ret

    def match_op(self, op_list: list[int]) -> bool:
        if (self.is_end()):
            return False

        cur = self.cur()
        ret = any(cur.token_value == op for op in op_list)
        self.pt += 1
        return ret

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

        return False

    def LOGIC_EP(self) -> bool:
        tmp = self.pt
        if (self.LOGIC_EP_B() and self.LOGIC_EP_):
            return True

        self.pt = tmp
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
        if (self.MATH_EP()):
            return True

        self.pt = tmp
        return False

    def MATH_EP(self) -> bool:
        if (self.TD() and self.MATH_EP_()):
            return True

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
                assert (self.TYPE() and self.VAR_LIST()
                        and self.match(str_to_token_value(';')))
                return True
            print(f'Unexpected {cur.token_str}')
        print('Expected TYPE')
        return False

    def VAR_LIST(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                assert (self.VAR() and self.VAR_LIST_())
                return True
            print(f'Unexpected {cur.token_str}')
        print('Expected Identifier')
        return False

    def VAR_LIST_(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                assert (self.match(str_to_token_value(',')) and self.VAR()
                        and self.VAR_LIST_())
                return True
            elif (cur.token_value == str_to_token_value(';')):
                return True
            print(f'Unexpected {cur.token_str}')
        print('Expected , ;')
        return False

    def VAR(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                assert (self.match(Identifier.token_value) and self.VAR_())
                return True
            print(f'Unexpected {cur.token_str}')

        print('Expected Identifier')
        return False

    def VAR_(self) -> bool:
        if (self.is_end()):
            print('Unexpected ending')
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                assert self.INITIAL()
                return True
            elif (cur.token_value == str_to_token_value(';')):
                assert self.INITIAL()
                return True
            elif (cur.token_value == str_to_token_value('=')):
                assert self.INITIAL()
                return True
            elif (cur.token_value == str_to_token_value('[')):
                assert (self.match(str_to_token_value('['))
                        and self.match(Integer.token_value)
                        and self.match(str_to_token_value(']')))
                return True
            print(f'Unexpected {cur.token_str}')

        print('Expected either , ; = [')
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
                assert (self.match(str_to_token_value('=')) and self.EP())
                return True
            print(f'Unexpected {cur.token_str}')

        print('Expected either , ; =')
        return False

    def TYPE(self) -> bool:
        assert (self.match_type())  # It should always pass
        return True

    def cur(self) -> Token:
        return self.token_list[self.pt]

    def is_end(self) -> bool:
        return self.pt >= len(self.token_list)

    def match_type(self):
        if (self.is_end()):
            return False

        cur = self.cur()
        assert isinstance(cur, Keyword)
        ret = cur.is_type()
        self.pt += 1
        return ret

    def BLOCK_ST(self) -> bool:
        accept = False
        while (not accept):
            if self.match(str_to_token_value('return')):
                self.stack.push('return')

                if (self.EP()):
                    self.stack.push('EP')
                else:
                    print('Expected: EP')
                    return False
                
                if (self.match(str_to_token_value(';'))):
                    self.stack.push(';')
                else:
                    print('Expected: ;')
                    return False

            elif self.match(Identifier.token_value):
                self.stack.push('id')
                if self.match(str_to_token_value('=')):
                    self.stack.push('=')
                else:
                    print('Expected: =')
                    return False
                
                if self.EP():
                    self.stack.push('EP')
                else:
                    print('Expected: EP')
                    return False
                
                if (self.match(str_to_token_value(';'))):
                    self.stack.push(';')
                else:
                    print('Expected: ;')
                    return False

            elif self.match(str_to_token_value('while')):
                self.stack.push('while')
                
                if self.match(str_to_token_value('(')):
                    self.stack.push('(')
                else:
                    print('Expected: (')
                    return False
                
                if self.LOGIC_EP():
                    self.stack.push('LOGIC_EP')
                else:
                    print('Expected: LOGIC_EP')
                    return False
                
                if self.match(str_to_token_value(')')):
                    self.stack.push(')')
                else:
                    print('Expected: )')
                    return False
                
                if self.match(str_to_token_value('{')):
                    self.stack.push('{')
                else:
                    print('Expected: {')
                    return False

                if (self.BLOCK_ST()):
                    self.stack.push('BLOCK_ST')
                else:
                    print('Expected: BLOCK_ST')
                    return False

                if (self.match(str_to_token_value('}'))):
                    self.stack.push('}')
                else:
                    print('Expected: }')
                    return False

            elif (self.stack.top() == ';'): # Reduce 'RETURN_ST -> . return EP ;' and 'ASS_ST -> id = EP ;'
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

            elif (self.stack.top() == 'RETURN_ST'): # Reduce STATM -> RETURN_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'ASS_ST'): # Reduce STATM -> ASS_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'WHILE_ST'): # Reduce STATM -> WHILE_ST
                self.stack.pop()
                self.stack.push('STATM')

            elif (self.stack.top() == 'STATM'): # Reduce 'BLOCK_ST -> BLOCK_ST STATM' and 'BLOCK_ST -> STATM'
                self.stack.pop()
                if (not self.stack.is_empty()
                        and self.stack.top() == 'BLOCK_ST'):
                    self.stack.pop()
                    self.stack.push('BLOCK_ST')
                else:
                    self.stack.push('BLOCK_ST')

            elif self.stack.top() == 'BLOCK_ST': # Reduce 'S -> BLOCK_ST
                self.stack.pop()
                self.stack.push('S')

            elif (self.stack.top() == 'S'): # Accept
                self.stack.pop()
                accept = True
            else:
                # Do LL(1) Top-Down here
                if (self.is_end()):
                    print('Unexpected ending.')
                    return False
                cur = self.cur()
                if (isinstance(cur, Keyword) and cur.is_type()):
                    if (not self.DECLA()):
                        return False
                if (cur.token_value == str_to_token_value('if')):
                    if (not self.IF_ST()):
                        return False
                elif (cur.token_value == str_to_token_value('for')):
                    if (not self.FOR_ST()):
                        return False
                else:
                    print('Error happens')
                    return False
        return True

    def IF_ST(self) -> bool:
        if not self.match(str_to_token_value('if')):
            return False
        if not self.match(str_to_token_value('(')):
            return False
        if not self.LOGIC_EP():
            return False
        if not self.match(str_to_token_value('{')):
            return False
        if not self.BLOCK_ST():
            return False
        if not self.match(str_to_token_value('}')):
            return False
        if not self.ELSE_ST():
            return False

    def ELSE_ST(self) -> bool:
        if (self.match(str_to_token_value('{'))):
            if (not self.BLOCK_ST()):
                return False
            if (not self.match(str_to_token_value('}'))):
                return False
        return True


    def FOR_ST(self) -> bool:
        if not self.match(str_to_token_value('for')):
            return False
        if not self.match(str_to_token_value('(')):
            return False
        if not self.VAR():
            return False
        if not self.match(str_to_token_value(';')):
            return False
        if not self.LOGIC_EP():
            return False
        if not self.match(str_to_token_value(';')):
            return False
        if not self.ASS_ST():
            return False
        if not self.match(str_to_token_value(')')):
            return False
        if not self.match(str_to_token_value('{')):
            return False
        if not self.BLOCK_ST():
            return False
        if not self.match(str_to_token_value('}')):
            return False

    def ASS_ST(self) -> bool:
        if not self.match(Identifier.token_value):
            return False
        if not self.match(str_to_token_value('=')):
            return False
        if not self.EP():
            return False



if __name__ == '__main__':
    from pathlib import Path
    tokens = read_tokens_from_file(Path('output', 'output7.txt'))
    parser = Parser(0, tokens)
    print(parser.DECLA(), parser.pt)
    # current_stat = STATE.START
    # idx = 0
    # tokens_size = len(tokens)

    # while (idx < tokens_size - 1):
    #     token = tokens[idx]
    #     if (current_stat == STATE.START):
    #         if (type(token) is not Keyword):
    #             raise Exception(token)
    #         if (not token.is_type()):
    #             raise Exception(token)
    #     pass
