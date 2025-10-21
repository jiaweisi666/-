import re

class Lexer:
    def __init__(self):
        self.keywords = {
            'begin': 1, 'if': 2, 'then': 3, 'while': 4, 'do': 5, 'end': 6,
            'main': 7, 'int': 8, 'float': 9, 'for': 10, 'else': 11,
            'double': 12, 'char': 13, 'break': 14, 'continue': 15
        }
        self.operators = {
            '+': 18, '-': 19, '*': 20, '/': 21, '%': 22, ':=': 23, '<': 24,
            '<>': 25, '<=': 26, '>': 27, '>=': 28, '=': 29, '==': 30, ';': 31,
            '(': 32, ')': 33, '{': 34, '}': 35, '#': 36, '++': 37, '--': 38
        }
        self.id_code = 16
        self.num_code = 17

    def tokenize(self, code):
        tokens = []
        comments = []
        position = 0
        n = len(code)

        while position < n:
            if code[position].isspace():
                position += 1
                continue

            # 多行注释
            if code[position:position+2] == '/*':
                start = position
                end = code.find('*/', start + 2)
                if end == -1:
                    raise ValueError(f"Unclosed multi-line comment starting at position {start}")
                end += 2
                comments.append({
                    'value': code[start:end],
                    'type': 'multi_line_comment',
                    'start': start,
                    'end': end
                })
                position = end
                continue

            # 单行注释
            if code[position:position+2] == '//':
                start = position
                end = code.find('\n', start + 2)
                if end == -1:
                    end = n
                comments.append({
                    'value': code[start:end],
                    'type': 'single_line_comment',
                    'start': start,
                    'end': end
                })
                position = end
                continue

            # 标识符或关键字
            if code[position].isalpha() or code[position] == '_':
                start = position
                while position < n and (code[position].isalnum() or code[position] == '_'):
                    position += 1
                word = code[start:position]
                token_type = 'keyword' if word in self.keywords else 'identifier'
                tokens.append({
                    'value': word,
                    'code': self.keywords.get(word, self.id_code),
                    'type': token_type,
                    'start': start,
                    'end': position
                })
                continue

            # 数字 (包括浮点数)
            if code[position].isdigit():
                start = position
                while position < n and code[position].isdigit():
                    position += 1
                if position < n and code[position] == '.':
                    if position + 1 < n and code[position + 1].isdigit():
                        position += 1
                        while position < n and code[position].isdigit():
                            position += 1
                num = code[start:position]
                tokens.append({
                    'value': num,
                    'code': self.num_code,
                    'type': 'number',
                    'start': start,
                    'end': position
                })
                continue

            # 运算符和界符
            start = position
            matched_op = None
            for op_len in [2, 1]:
                if position + op_len <= n:
                    op_candidate = code[position:position + op_len]
                    if op_candidate in self.operators:
                        matched_op = op_candidate
                        break
            
            if matched_op:
                position += len(matched_op)
                tokens.append({
                    'value': matched_op,
                    'code': self.operators[matched_op],
                    'type': 'operator',
                    'start': start,
                    'end': position
                })
                continue

            raise ValueError(f"Unknown character: {code[position]} at position {position}")

        return {'tokens': tokens, 'comments': comments}
