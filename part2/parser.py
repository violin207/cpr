from my_token import read_tokens_from_file, Token, Identifier, Integer, String, Float, Operator, Punctuation, Keyword
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
    def __init__(self, pt: int, token_list: list[Token]):
        self.pt = pt
        self.token_list = token_list

    def match(self, type: int) -> bool:
        if (self.token_list[self.pt].token_value == type):
            self.pt += 1
            return True
        return False

    def ep(self) -> bool:
        tmp = self.pt
        if (self.logic_ep()):
            return True
        
        self.pt = tmp
        if (self.math_ep()):
            return True
        
        self.pt = tmp        
        if (self.match(String.token_value)):
            return True
        
        return False

    def logic_ep(self) -> bool:
        pass

    def math_ep(self) -> bool:
        pass



if __name__ == '__main__':
    tokens = read_tokens_from_file('output.txt')
    current_stat = STATE.START
    idx = 0
    tokens_size = len(tokens)

    while (idx < tokens_size -1):
        token = tokens[idx]
        if (current_stat == STATE.START):
            if (type(token) is not Keyword):
                raise Exception(token)
            if (not token.is_type()):
                raise Exception(token)
        pass