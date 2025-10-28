from flask import Flask, request, jsonify
from flask_cors import CORS
from lexer import Lexerapp.py

app = Flask(__name__)
CORS(app)  # 允许跨域请求

lexer = Lexer()


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    词法分析API接口
    接收JSON格式的代码，返回词法分析结果和注释
    """
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': '缺少代码参数'
            }), 400

        code = data['code']
        if not code.strip():
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            }), 400

        # 进行词法分析
        analysis_result = lexer.tokenize(code)

        return jsonify({
            'success': True,
            'tokens': analysis_result['tokens'],
            'comments': analysis_result['comments']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/example', methods=['GET'])
def get_example_code():
    """
    获取示例代码
    """
    example_code = '''/*
这是一个测试程序
用于测试词法分析器
*/
main() {
    int a = 100;
    int b = 20;  // 这是单行注释
    if (a < b) then
        begin
            a := a + 1;
            b := b * 2;
        end
    else
        begin
            a := a - 1;
            b := b / 2;
        end
    while (a > 0) do
        begin
            a := a - 1;
            if (a == 0) break;
        end
    for (int i = 0; i < 10; i++)
        begin
            print(i);
            if (i > 5) continue;
        end
}'''

    return jsonify({
        'success': True,
        'code': example_code
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
