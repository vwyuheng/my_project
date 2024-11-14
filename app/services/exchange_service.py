import requests
from datetime import datetime, timedelta
import json
import re


def get_offshore_rate():
    """获取离岸人民币汇率"""
    url = "https://hq.sinajs.cn/list=fx_susdcnh"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://finance.sina.com.cn"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5000)
        response.raise_for_status()

        # 解析响应文本
        text = response.text
        match = re.search(r'"([^"]+)"', text)
        if match:
            data = match.group(1).split(",")
            if len(data) >= 8:  # 确保有足够的数据
                rate = float(data[7])  # 使用收盘价
                return {
                    'success': True,
                    'rate': round(rate, 4),
                    'date': datetime.now().strftime("%Y-%m-%d")
                }

        return {'success': False, 'message': '无法解析离岸人民币汇率数据'}
    except Exception as e:
        # 如果新浪接口失败，尝试使用备用数据源
        try:
            backup_url = "http://web.juhe.cn:8080/finance/exchange/fx"
            response = requests.get(backup_url, timeout=10)
            data = response.json()

            if data.get('result') and isinstance(data['result'], list):
                for item in data['result']:
                    if item.get('name') == '美元/人民币':
                        return {
                            'success': True,
                            'rate': round(float(item['price']), 4),
                            'date': datetime.now().strftime("%Y-%m-%d")
                        }
            return {'success': False, 'message': '无法获取离岸人民币汇率'}
        except Exception as e2:
            return {'success': False, 'message': str(e)}


def get_onshore_rate():
    """获取在岸人民币汇率"""
    url = "https://www.chinamoney.com.cn/ags/ms/cm-u-bk-ccpr/CcprHisNew"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://www.chinamoney.com.cn"
    }

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.post(
            url,
            headers=headers,
            json={
                "startDate": today,
                "endDate": today,
                "currency": "USD/CNY",
                "pageNum": 1,
                "pageSize": 1
            },
            timeout=10
        )
        data = response.json()

        if data.get('records'):
            latest_rate = data['records'][0]
            return {
                'success': True,
                'rate': float(latest_rate['values'][0]),
                'date': latest_rate['date']
            }
        return {'success': False, 'message': '无数据'}
    except Exception as e:
        # 如果主数据源失败，尝试使用新浪财经的在岸人民币数据
        try:
            backup_url = "https://hq.sinajs.cn/list=fx_susdcny"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://finance.sina.com.cn"
            }
            response = requests.get(backup_url, headers=headers, timeout=10)
            text = response.text
            match = re.search(r'"([^"]+)"', text)
            if match:
                data = match.group(1).split(",")
                if len(data) >= 8:
                    rate = float(data[7])
                    return {
                        'success': True,
                        'rate': round(rate, 4),
                        'date': datetime.now().strftime("%Y-%m-%d")
                    }
            return {'success': False, 'message': '无数据'}
        except Exception as e2:
            return {'success': False, 'message': str(e)}


def get_exchange_rates():
    """获取所有汇率"""
    onshore_data = get_onshore_rate()
    offshore_data = get_offshore_rate()

    return {
        'success': True,
        'data': {
            'central': {
                'currencies': {
                    'CNY': round(onshore_data['rate'], 4) if onshore_data['success'] else None,
                    'CNH': round(offshore_data['rate'], 4) if offshore_data['success'] else None
                },
                'date': onshore_data.get('date') or offshore_data.get('date')
            }
        }
    }


# 缓存机制
cache_data = {
    'rates': None,
    'last_update': None
}


def get_cached_rates():
    """获取带缓存的汇率数据"""
    now = datetime.now()

    # 如果缓存存在且未过期（5分钟内），则返回缓存数据
    if (cache_data['rates'] is not None and
            cache_data['last_update'] is not None and
            now - cache_data['last_update'] < timedelta(minutes=5)):
        return cache_data['rates']

    # 获取新数据
    rates = get_exchange_rates()

    # 更新缓存
    cache_data['rates'] = rates
    cache_data['last_update'] = now

    return rates


# 测试函数
def test_exchange_rates():
    """测试汇率获取是否正常"""
    try:
        print("正在测试在岸汇率...")
        onshore = get_onshore_rate()
        print("在岸汇率:", onshore)

        print("\n正在测试离岸汇率...")
        offshore = get_offshore_rate()
        print("离岸汇率:", offshore)

        print("\n正在测试完整汇率数据...")
        all_rates = get_exchange_rates()
        print("所有汇率:", json.dumps(all_rates, indent=2, ensure_ascii=False))

        return True
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    test_exchange_rates()