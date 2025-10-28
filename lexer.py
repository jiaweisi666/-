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
            if code[position:position + 2] == '/*':
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
            if code[position:position + 2] == '//':
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

            # 运算符和界符（优先两字符运算符）
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

            # 未知字符
            raise ValueError(f"Unknown character: {code[position]} at position {position}")

        # 在 tokens 末尾添加一个 EOF 伪标记，方便语法分析判断结束
        tokens.append({'value': 'EOF', 'code': 0, 'type': 'eof', 'start': n, 'end': n})
        return {'tokens': tokens, 'comments': comments}


class Parser:
    """
    递归下降解析器，基于用户给定文法：
    <程序>→begin <语句串>end
    <语句串>→<语句>{;<语句>}
    <语句>→<赋值语句>
    <赋值语句>→ID = <表达式>
    <表达式>∷=[+|-] <项>{(+|-) <项>}
    <项>∷=<因子>{(*|/) <因子>}
    <因子>∷= id|num| '(' <表达式> ')'
    """

    def __init__(self, tokens):
        # tokens 是来自 Lexer 的列表，最后有 'EOF'
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if self.tokens else {'value': 'EOF', 'type': 'eof'}

    def _advance(self):
        if self.pos + 1 < len(self.tokens):
            self.pos += 1
            self.current = self.tokens[self.pos]
        else:
            self.current = {'value': 'EOF', 'type': 'eof'}

    def _expect(self, kind=None, value=None):
        """
        检查当前 token 是否满足期望（可根据 type 或 value），否则抛出错误
        """
        cur = self.current
        if kind and cur.get('type') != kind:
            raise SyntaxError(
                f"Expected token type '{kind}' but got '{cur.get('type')}' (value='{cur.get('value')}') at pos {self.pos}")
        if value and cur.get('value') != value:
            raise SyntaxError(f"Expected token value '{value}' but got '{cur.get('value')}' at pos {self.pos}")
        self._advance()

    def parse(self):
        """
        外部调用入口，返回结构化结果：
        {'success': True} 或 {'success': False, 'error': '...', 'pos': n}
        """
        try:
            self.pos = 0
            self.current = self.tokens[self.pos] if self.tokens else {'value': 'EOF', 'type': 'eof'}
            self._parse_program()
            # 最后应为 EOF
            if self.current.get('type') != 'eof' and self.current.get('value') != 'EOF':
                raise SyntaxError(f"Extra tokens after end at pos {self.pos}, token={self.current}")
            return {'success': True}
        except SyntaxError as e:
            return {'success': False, 'error': str(e), 'pos': self.pos}
        except Exception as e:
            return {'success': False, 'error': str(e), 'pos': self.pos}

    # ---------------- grammar methods ----------------
    def _parse_program(self):
        # <程序> → begin <语句串> end
        if self.current.get('value') == 'begin' and self.current.get('type') in ('keyword', 'identifier'):
            # 'begin' is stored as keyword but type might be 'keyword'; check value
            self._advance()
        elif self.current.get('value') == 'begin':
            self._advance()
        else:
            raise SyntaxError(f"Program must start with 'begin' at pos {self.pos}, got '{self.current.get('value')}'")
        self._parse_stmt_list()
        if self.current.get('value') == 'end':
            self._advance()
        else:
            raise SyntaxError(f"Expected 'end' at pos {self.pos}, got '{self.current.get('value')}'")

    def _parse_stmt_list(self):
        # <语句串>→<语句>{;<语句>}
        self._parse_stmt()
        while self.current.get('value') == ';':
            self._advance() # 消耗分号
            # 允许在 end 前有可选的尾随分号
            if self.current.get('value') == 'end':
                break # 如果是 end，说明语句列表结束，跳出循环
            self._parse_stmt()

    def _parse_stmt(self):
        # <语句> → <赋值语句>
        self._parse_assignment()

    def _parse_assignment(self):
        # <赋值语句> → ID = <表达式>
        if self.current.get('type') == 'identifier':
            # consume ID
            self._advance()
            if self.current.get('value') == '=':
                self._advance()
                self._parse_expression()
            else:
                raise SyntaxError(f"Expected '=' after identifier at pos {self.pos}, got '{self.current.get('value')}'")
        else:
            raise SyntaxError(f"Expected identifier at pos {self.pos}, got '{self.current.get('value')}'")

    def _parse_expression(self):
        # <表达式>∷=[+|-] <项>{(+|-) <项>}
        if self.current.get('value') in ('+', '-'):
            # unary + or -
            self._advance()
        self._parse_term()
        while self.current.get('value') in ('+', '-'):
            self._advance()
            self._parse_term()

    def _parse_term(self):
        # <项>∷=<因子>{(*|/) <因子>}
        self._parse_factor()
        while self.current.get('value') in ('*', '/'):
            self._advance()
            self._parse_factor()

    def _parse_factor(self):
        # <因子>∷= id|num| '(' <表达式> ')'
        if self.current.get('type') == 'identifier' or self.current.get('type') == 'number':
            self._advance()
        elif self.current.get('value') == '(':
            self._advance()
            self._parse_expression()
            if self.current.get('value') == ')':
                self._advance()
            else:
                raise SyntaxError(f"Missing ')' at pos {self.pos}, got '{self.current.get('value')}'")
        else:
            raise SyntaxError(f"Unexpected token in factor at pos {self.pos}: '{self.current.get('value')}'")
