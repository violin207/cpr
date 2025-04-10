from my_token import Token, Identifier, Integer, String, Float, Operator, Punctuation, Keyword
from io import TextIOWrapper
import sys
import argparse
from pathlib import Path


def handle_digit(f: TextIOWrapper, start: str) -> Token:
    str_value = start
    is_float = False
    while (char := f.read(1)):
        if (char.isdigit()):
            str_value += char
        elif (char == '.' and is_float == False):
            str_value += char
            is_float = True
        else:
            break

    if (is_float):
        return Float(str_value), char
    return Integer(str_value), char


def handle_identifier_and_keyword(f: TextIOWrapper, start: str) -> Token:
    str_value = start
    while (char := f.read(1)):
        if (char.isalpha() or char.isdigit() or char == '_'):
            str_value += char
        else:
            break

    if (Keyword.is_keyword(str_value)):
        return Keyword(str_value), char
    else:
        return Identifier(str_value), char


def handle_operator_and_punctutation(f: TextIOWrapper, start: str) -> Token:
    str_value = start
    char = f.read(1)

    if (start == '=' and char == '='):
        str_value += char
        char = f.read(1)
    elif (start == '>' and char == '='):
        str_value += char
        char = f.read(1)
    elif (start == '<' and char == '='):
        str_value += char
        char = f.read(1)
    elif (start == '+' and char == '+'):
        str_value += char
        char = f.read(1)
    elif (start == '-' and char == '-'):
        str_value += char
        char = f.read(1)
    elif (start == '&' and char == '&'):
        str_value += char
        char = f.read(1)
    elif (start == '|' and char == '|'):
        str_value += char
        char = f.read(1)

    if (Operator.is_operator(str_value)):
        return Operator(str_value), char
    elif (Punctuation.is_punctutaion(str_value)):
        return Punctuation(str_value), char
    else:
        raise Exception(str_value)


def handle_string(f: TextIOWrapper, start: str):
    str_value = start
    ending_op = start
    finished = False
    while (char := f.read(1)):
        if (char == '\\'):
            char += f.read(1)

        str_value += char
        if (char == ending_op):
            finished = True
            char = f.read(1)
            break

    if finished:
        return String(str_value), char
    else:
        raise Exception('Error when handling string.')


def parse(s):
    parser = argparse.ArgumentParser(s)
    parser.add_argument('-i', '--input_file', default='input.txt')
    parser.add_argument('-o', '--output_file', default=None)

    parsed_args = parser.parse_args()
    input_file = parsed_args.input_file
    output_file = parsed_args.output_file
    if output_file is None:
        output_file = f'{input_file}.out'
    
    return input_file, output_file


if __name__ == '__main__':
    input_filename, output_filename = parse(sys.argv[0])

    with open(Path('data', 'files', input_filename), 'r') as f:
        tokens: list[Token] = list()

        char = f.read(1)
        while (char != ''):
            if (char == '\n' or char == ' '):
                char = f.read(1)
            elif (char.isdigit()):
                token, char = handle_digit(f, char)
                tokens.append(token)
            elif (char.isalpha() or char == '_'):
                token, char = handle_identifier_and_keyword(f, char)
                tokens.append(token)
            elif (char == '"' or char == '\''):
                token, char = handle_string(f, char)
                tokens.append(token)
            else:
                token, char = handle_operator_and_punctutation(f, char)
                tokens.append(token)

    with open(Path('data', 'lex_out', output_filename), 'w') as f:
        f.write(', '.join(map(str, tokens)))
