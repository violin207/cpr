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


class Parser():
    OP1 = [Operator.OPERATOR_DICT[x] for x in ['+', '-']]
    OP2 = [Operator.OPERATOR_DICT[x] for x in ['*', '/']]
    OP_OR = [Operator.OPERATOR_DICT['||'], Keyword.KEYWORD_DICT['or']]
    OP_AND = [Operator.OPERATOR_DICT['&&'], Keyword.KEYWORD_DICT['and']]
    OP_NOT = [Operator.OPERATOR_DICT['!'], Keyword.KEYWORD_DICT['not']]

    def __init__(self, pt: int, token_list: list[Token]):
        self.pt = pt
        self.token_list = token_list

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
            return False
        else:
            cur = self.cur()
            if (isinstance(cur, Keyword) and cur.is_type()):
                assert (self.TYPE() and self.VAR_LIST()
                        and self.match(str_to_token_value(';')))
                return True

        return False

    def VAR_LIST(self) -> bool:
        if (self.is_end()):
            return False
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                assert (self.VAR() and self.VAR_LIST_())
                return True
        return False

    def VAR_LIST_(self) -> bool:
        if (self.is_end()):
            return False
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                assert (self.match(str_to_token_value(',')) and self.VAR()
                        and self.VAR_LIST_())
                return True
            elif (cur.token_value == str_to_token_value(';')):
                return True
        return False

    def VAR(self) -> bool:
        if (self.is_end()):
            return False
        else:
            cur = self.cur()
            if (cur.token_value == Identifier.token_value):
                assert (self.match(Identifier.token_value) and self.VAR_())
                return True
        return False

    def VAR_(self) -> bool:
        if (self.is_end()):
            return False
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

        return False

    def INITIAL(self) -> bool:
        if (self.is_end()):
            return False
        else:
            cur = self.cur()
            if (cur.token_value == str_to_token_value(',')):
                return True
            elif (cur.token_value == str_to_token_value(';')):
                return True
            elif (cur.token_value == str_to_token_value('=')):
                assert (self.match(str_to_token_value('=')) and self.EP())
                return True

        return False

    def TYPE(self) -> bool:
        assert (self.match_type())
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


if __name__ == '__main__':
    tokens = read_tokens_from_file('output.txt')
    parser = Parser(0, tokens)
    print(parser.EP(), parser.pt, parser.token_list[parser.pt])
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
