from flask import Flask, request, jsonify
from flask_cors import CORS
from lexer import Lexer, Parser

app = Flask(__name__)
CORS(app)  # 允许跨域请求

lexer = Lexer()


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    词法 + 语法 分析 API 接口
    接收 JSON 格式的代码，返回词法分析结果、注释以及语法分析结果
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '缺少 code 参数'
            }), 400

        code = data['code']
        if not code.strip():
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            }), 400

        # 进行词法分析
        analysis_result = lexer.tokenize(code)
        tokens = analysis_result['tokens']
        comments = analysis_result['comments']

        # 语法分析（递归下降）
        parser = Parser(tokens)
        parse_result = parser.parse()

        return jsonify({
            'success': True,
            'tokens': tokens,
            'comments': comments,
            'parse': parse_result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/example', methods=['GET'])
def get_example_code():
    """
    获取示例代码（注意：示例里包含的很多语法不一定完全对应我们简化的文法，
    仅作前端填充示例；你可以替换为与目标文法一致的示例）
    """
    example_code = '''begin
a = 1;
b = a + 2 * (3 + 4);
c = -b + 5;
end
'''

    return jsonify({
        'success': True,
        'code': example_code
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
