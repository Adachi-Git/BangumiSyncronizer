import json
import requests
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def calculate_rate(score):
    # 对于评分为 0，始终返回 0
    if score == 0:
        return 0
    # 50% 的概率向下取整，50% 的概率向下取整再加 1
    return math.floor(score) + random.choice([0, 1])

def process_item(item, auth_token, processed_ids, max_retries=3):
    item_id = item["id"]
    
    # 跳过已处理的 ID
    if item_id in processed_ids:
        print(f"Subject ID {item_id} has already been processed. Skipping.")
        return

    item_score = item["score"]
    
    # 计算rate
    item_rate = calculate_rate(item_score)
    
    # 构造发送到API的数据
    api_data = {
        "type": 3,
        "rate": item_rate,
        "comment": "string",  # 可根据需要修改
        "private": True,  # 可根据需要修改
        "tags": ["string"]  # 可根据需要修改
    }

    # 构造API请求
    api_url = f'https://api.bgm.tv/v0/users/-/collections/{item_id}'
    headers = {
        'accept': '*/*',
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'User-Agent': 'Adachi/BangumiMigrate(https://github.com/Adachi-Git/BangumiMigrate)'
    }

    # 重试逻辑
    for retry in range(max_retries):
        try:
            # 发送POST请求
            response = requests.post(api_url, headers=headers, json=api_data)

            # 打印请求结果
            print(f"Subject ID: {item_id}, Score: {item_score}, Rate: {item_rate}, API Response: {response.status_code}")

            # 记录已处理的 ID
            processed_ids.add(item_id)

            # 延时5秒
            time.sleep(5)

            # 跳出重试循环
            break
        except requests.RequestException as e:
            # 请求异常，进行重试
            print(f"Request failed. Retrying... (Retry {retry + 1}/{max_retries})")
            time.sleep(5)  # 延时5秒后重试
    else:
        # 所有重试失败，保存到日志
        print(f"Subject ID {item_id} failed after {max_retries} retries. Check log for details.")

def main():
    # 从外部JSON文件加载数据
    input_file_path = r"C:\Users\Darling\Desktop\1.json"  # 替换为你实际的JSON文件路径
    with open(input_file_path, "r", encoding="utf-8") as input_file:
        json_data = json.load(input_file)

    # 记录已处理的 ID 的文件路径
    processed_ids_file = "processed_ids.txt"

    # 在代码开始处定义一个集合
    processed_ids = set()

    # 加载已处理的 ID 记录
    try:
        with open(processed_ids_file, "r") as f:
            processed_ids = set(map(int, f.read().splitlines()))
    except FileNotFoundError:
        pass

    # 替换为你的实际认证令牌
    auth_token = ''

    # 使用 ThreadPoolExecutor 实现并发处理
    with ThreadPoolExecutor() as executor:
        # 提交任务到线程池
        futures = [executor.submit(process_item, item, auth_token, processed_ids) for item in json_data]

        # 等待所有任务完成
        for future in as_completed(futures):
            # 处理异常，防止一个任务的异常影响其他任务
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

    # 保存已处理的 ID 记录
    with open(processed_ids_file, "w") as f:
        f.write("\n".join(map(str, processed_ids)))

    print("所有数据处理完成")

if __name__ == "__main__":
    main()
