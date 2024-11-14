# config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    DEBUG = True
    EXCHANGE_API_KEY = 'YOUR_API_KEY'  # 添加API密钥配置

    # 添加API配置
    EXCHANGE_APIS = {
        'primary': 'https://api.exchangerate-api.com/v4/latest/USD',
        'secondary': 'https://api.exchangerate.host/latest',
        'backup': 'https://open.er-api.com/v6/latest/USD',
        'offshore': 'https://api.apilayer.com/exchangerates_data/latest'
    }