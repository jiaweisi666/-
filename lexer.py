import re

class Lexer:
    def __init__(self):
        # 关键字及其对应的种别码
        self.keywords = {
            'begin': 1, 'if': 2, 'then': 3, 'while': 4, 'do': 5, 'end': 6,
            'main': 7, 'int': 8, 'float': 9, 'for': 10, 'else': 11,
            'double': 12, 'char': 13, 'break': 14, 'continue': 15
        }

        # 运算符和界符及其对应的对应的种别码
        self.operators = {
            '+': 18, '-': 19, '*': 20, '/': 21, '%': 22, ':=': 23, '<': 24,
            '<>': 25, '<=': 26, '>': 27, '>=': 28, '=': 29, '==': 30, ';': 31,
            '(': 32, ')': 33, '{': 34, '}': 35, '#': 36, '++': 37, '--': 38
        }

        # 标识符种别码
        self.id_code = 16

        # 数字种别码
        self.num_code = 17

    def tokenize(self, code):
        """
        对代码进行词法分析，返回token列表和注释列表
        """
        tokens = []
        comments = []
        position = 0
        n = len(code)

        while position < n:
            # 跳过空白字符
            if code[position].isspace():
                position += 1
                continue

            # 检查是否为多行注释 /* */
            if code[position:position+2] == '/*':
                comment_start = position
                comment_end = code.find('*/', position + 2)
                if comment_end != -1:
                    comment_content = code[comment_start : comment_end + 2]
                    comments.append({
                        'value': comment_content,
                        'type': 'multi_line_comment',
                        'start': comment_start,
                        'end': comment_end + 2
                    })
                    position = comment_end + 2
                    continue
                else:
                    raise ValueError(f"未闭合的多行注释从位置 {position} 开始")

            # 检查是否为单行注释 //
            if code[position:position+2] == '//':
                comment_start = position
                comment_end = code.find('\n', position + 2)
                if comment_end == -1:
                    comment_end = n # 到文件末尾
                comment_content = code[comment_start : comment_end]
                comments.append({
                    'value': comment_content,
                    'type': 'single_line_comment',
                    'start': comment_start,
                    'end': comment_end
                })
                position = comment_end
                continue

            # 检查是否为标识符或关键字
            if code[position].isalpha() or code[position] == '_':
                start = position
                while position < n and (code[position].isalnum() or code[position] == '_'):
                    position += 1
                word = code[start:position]
                if word in self.keywords:
                    tokens.append({
                        'value': word,
                        'code': self.keywords[word],
                        'type': 'keyword'
                    })
                else:
                    tokens.append({
                        'value': word,
                        'code': self.id_code,
                        'type': 'identifier'
                    })
                continue

            # 检查是否为数字
            if code[position].isdigit():
                start = position
                while position < n and code[position].isdigit():
                    position += 1
                # 检查是否包含小数点（浮点数）
                if position < n and code[position] == '.':
                    if position + 1 < n and code[position + 1].isdigit():
                        position += 1 # consume the dot
                        while position < n and code[position].isdigit():
                            position += 1
                
                num = code[start:position]
                tokens.append({
                    'value': num,
                    'code': self.num_code,
                    'type': 'number'
                })
                continue

            # 检查是否为运算符或界符
            # 优先检查双字符运算符
            matched_op = None
            for op_len in [2, 1]: # 优先匹配长运算符
                if position + op_len <= n and code[position:position + op_len] in self.operators:
                    matched_op = code[position:position + op_len]
                    break
            
            if matched_op:
                tokens.append({
                    'value': matched_op,
                    'code': self.operators[matched_op],
                    'type': 'operator'
                })
                position += len(matched_op)
                continue

            # 如果以上都不是，抛出错误
            raise ValueError(f"未知字符: {code[position]} 在位置 {position}")

        return {'tokens': tokens, 'comments': comments}
