import requests

# API基础URL
API_BASE_URL = 'http://localhost:5000/api'


def test_analyze_api():
    """测试分析API"""
    print("测试分析API...")

    # 测试代码
    test_code = '''main() {
    int a = 100;
    if (a > 0) then
        begin
            a := a + 1;
        end
}'''

    try:
        response = requests.post(f'{API_BASE_URL}/analyze', json={'code': test_code})
        data = response.json()

        print(f"状态码: {response.status_code}")
        print(f"响应: {data}")

        if data['success']:
            print(f"分析成功，找到 {len(data['tokens'])} 个token")
            for i, token in enumerate(data['tokens'][:10]):  # 只显示前10个
                print(f"  {i + 1}. {token['value']} (种别码: {token['code']}, 类型: {token['type']})")
            if len(data['tokens']) > 10:
                print(f"  ... 还有 {len(data['tokens']) - 10} 个token")
    except Exception as e:
        print(f"测试失败: {e}")


def test_example_api():
    """测试示例代码API"""
    print("\n测试示例代码API...")

    try:
        response = requests.get(f'{API_BASE_URL}/example')
        data = response.json()

        print(f"状态码: {response.status_code}")

        if data['success']:
            print("获取示例代码成功")
            print(f"代码长度: {len(data['code'])} 字符")
            print("前200个字符:")
            print(data['code'][:200] + "...")
        else:
            print(f"获取失败: {data.get('error', '未知错误')}")
    except Exception as e:
        print(f"测试失败: {e}")


def test_error_cases():
    """测试错误情况"""
    print("\n测试错误情况...")

    # 测试空代码
    try:
        response = requests.post(f'{API_BASE_URL}/analyze', json={'code': ''})
        data = response.json()
        print(f"空代码测试 - 状态码: {response.status_code}, 响应: {data}")
    except Exception as e:
        print(f"空代码测试失败: {e}")

    # 测试无效字符
    invalid_code = 'int a = 100@;'
    try:
        response = requests.post(f'{API_BASE_URL}/analyze', json={'code': invalid_code})
        data = response.json()
        print(f"无效字符测试 - 状态码: {response.status_code}, 响应: {data}")
    except Exception as e:
        print(f"无效字符测试失败: {e}")


if __name__ == '__main__':
    print("=== 词法分析器API测试 ===\n")

    test_analyze_api()
    test_example_api()
    test_error_cases()

    print("\n=== 测试完成 ===")
