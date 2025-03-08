import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# 读取JSON文件
with open('allitem.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 确保opt目录存在
os.makedirs('opt', exist_ok=True)

# HTTP代理设置
proxies = {
#    'http': 'http://127.0.0.1:10808'
}

# 下载函数
def download_item(item):
    title_id = item['TitleID']
    
    # 构造请求URL（假设URL格式为https://example.com/api/{title_id}）
    url = f'http://xboxunity.net/api/v2/Covers/{title_id}'
    
    try:
        # 发送HTTP请求
        response = requests.get(url, proxies=proxies)
        
        if response.status_code == 200:
            # 将响应内容保存到opt目录
            with open(f'opt/{title_id}.json', 'w', encoding='utf-8') as outfile:
                json.dump(response.json(), outfile, ensure_ascii=False, indent=4)
        else:
            print(f"请求失败，TitleID: {title_id}, 状态码: {response.status_code}")
    except Exception as e:
        print(f"请求失败，TitleID: {title_id}, 错误: {e}")

# 使用多线程下载并添加进度条
items = data['Items']
with ThreadPoolExecutor(max_workers=32) as executor:
    list(tqdm(executor.map(download_item, items), total=len(items)))