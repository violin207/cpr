import re


class Token:
    token_str: str
    token_type: str
    token_value: int

    def __str__(self):
        return f"<'{self.token_str}', {self.token_type}>"

    @staticmethod
    def from_string(token_str: str):
        """Parse a token string in the format <'value', type> and return the appropriate Token object"""
        import re
        match = re.match(r"<'(.*)', (.*)>", token_str.strip())
        if not match:
            raise ValueError(f"Invalid token format: {token_str}")

        str_value, token_type = match.groups()

        if token_type == 'identifier':
            return Identifier(str_value)
        elif token_type == 'int':
            return Integer(str_value)
        elif token_type == 'str':
            return String(str_value)
        elif token_type == 'float':
            return Float(str_value)
        elif token_type == 'keyword':
            return Keyword(str_value)
        elif token_type == 'operator':
            return Operator(str_value)
        elif token_type == 'punctuation':
            return Punctuation(str_value)
        else:
            raise ValueError(f"Unknown token type: {token_type}")


class Identifier(Token):
    token_type = 'identifier'
    token_value = 0

    def __init__(self, str_value: str):
        self.token_str = str_value


class Integer(Token):
    token_type = 'int'
    token_value = 1

    def __init__(self, str_value: str):
        self.token_str = str_value


class String(Token):
    token_type = 'str'
    token_value = 2

    def __init__(self, str_value: str):
        self.token_str = str_value


class Float(Token):
    token_type = 'float'
    token_value = 3

    def __init__(self, str_value: str):
        self.token_str = str_value


class Keyword(Token):
    KEYWORD_DICT = {
        'int': 11,
        # 'main': 12,
        'char': 13,
        'for': 14,
        'if': 15,
        'else': 16,
        'return': 17,
        'float': 18,
        'and': 19,
        'or': 20,
        'not': 21,
        'while': 22
    }

    token_type = 'keyword'

    def __init__(self, str_value: str):
        self.token_str = str_value
        self.token_value = Keyword.KEYWORD_DICT[self.token_str]

    @staticmethod
    def is_keyword(str_value: str) -> bool:
        return str_value in Keyword.KEYWORD_DICT

    def is_type(self) -> bool:
        if self.token_value in [11, 13, 18]:
            return True
        return False


class Operator(Token):
    OPERATOR_DICT = {
        '=': 101,
        '==': 102,
        '>=': 103,
        '<=': 104,
        '>': 105,
        '<': 106,
        '+': 107,
        '-': 108,
        '*': 109,
        '/': 110,
        '++': 111,
        '--': 112,
        '&&': 113,
        '||': 114,
        '!': 115
    }
    token_type = 'operator'

    def __init__(self, str_value: str):
        self.token_str = str_value
        self.token_value = Operator.OPERATOR_DICT[self.token_str]

    @staticmethod
    def is_operator(str_value: str) -> bool:
        return str_value in Operator.OPERATOR_DICT


class Punctuation(Token):
    PUNCTUATION_DICT = {
        '{': 201,
        '}': 202,
        ',': 203,
        ';': 204,
        '(': 205,
        ')': 206,
        '[': 207,
        ']': 208
    }

    token_type = 'punctuation'

    def __init__(self, str_value: str):
        self.token_str = str_value
        self.token_value = Punctuation.PUNCTUATION_DICT[self.token_str]

    @staticmethod
    def is_punctutaion(str_value: str) -> bool:
        return str_value in Punctuation.PUNCTUATION_DICT


class EndOfFileToken(Token):
    token_str = ''
    token_type = ''
    token_value = -1


def str_to_token_value(s: str):
    if (Keyword.is_keyword(s)):
        return Keyword.KEYWORD_DICT[s]
    elif (Punctuation.is_punctutaion(s)):
        return Punctuation.PUNCTUATION_DICT[s]
    elif (Operator.is_operator(s)):
        return Operator.OPERATOR_DICT[s]
    else:
        raise Exception(
            f'Unknow value {s}. Cannot be converted to token value')


def read_tokens_from_file(filename) -> list[Token]:
    with open(filename, 'r') as f:
        content = f.read().strip()

    # This regex matches each token while handling commas inside strings
    token_pattern = re.compile(r'''<'(.*?)',\s*(\w+)>''')
    tokens = []

    # Find all matches in the content
    for match in token_pattern.finditer(content):
        try:
            token = Token.from_string(match.group(0))
            tokens.append(token)
        except ValueError as e:
            print(f"Warning: Could not parse token '{match.group(0)}': {e}")

    return tokens
