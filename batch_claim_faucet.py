# -*- coding: utf-8 -*-
# Time     :2024/1/25 03:15
# Author   :ym
# File     :batch_claim.py
import asyncio
import json
from typing import Union

import aiofiles
import aiohttp
from eth_typing import ChecksumAddress, Address
from faker import Faker
from loguru import logger
import random
from curl_cffi.requests import AsyncSession

fake = Faker()
address_file = 'address.txt'
claim_success_file = 'claim_success.txt'


async def get_2captcha_google_token(session: aiohttp.ClientSession) -> Union[bool, str]:
    params = {'key': client_key, 'method': 'userrecaptcha', 'version': 'v3', 'action': 'submit', 'min_score': 0.5,
              'googlekey': '6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH', 'pageurl': 'https://artio.faucet.berachain.com/',
              'json': 1}
    async with session.get('https://2captcha.com/in.php?', params=params) as response:
        response_json = await response.json()
        # logger.debug(response_json)
        if response_json['status'] != 1:
            logger.warning(response_json)
            return False
        task_id = response_json['request']
    for _ in range(120):
        async with session.get(
                f'https://2captcha.com/res.php?key={client_key}&action=get&id={task_id}&json=1') as response:
            response_json = await response.json()
            if response_json['status'] == 1:
                return response_json['request']
            else:
                await asyncio.sleep(1)
    return False


async def get_2captcha_turnstile_token(session: aiohttp.ClientSession) -> Union[bool, str]:
    params = {'key': client_key, 'method': 'turnstile',
              'sitekey': '0x4AAAAAAARdAuciFArKhVwt',
              'pageurl': 'https://artio.faucet.berachain.com/',
              'json': 1}
    async with session.get('https://2captcha.com/in.php?', params=params) as response:
        response_json = await response.json()
        # logger.debug(response_json)
        if response_json['status'] != 1:
            logger.warning(response_json)
            return False
        task_id = response_json['request']
    for _ in range(120):
        async with session.get(
                f'https://2captcha.com/res.php?key={client_key}&action=get&id={task_id}&json=1') as response:
            response_json = await response.json()
            if response_json['status'] == 1:
                return response_json['request']
            else:
                await asyncio.sleep(1)
    return False


async def get_yescaptcha_google_token(session: aiohttp.ClientSession) -> Union[bool, str]:
    json_data = {"clientKey": client_key,
                 "task": {"websiteURL": "https://artio.faucet.berachain.com/",
                          "websiteKey": "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
                          "type": "RecaptchaV3TaskProxylessM1S7", "pageAction": "submit"}, "softID": 109}
    async with session.post('https://api.yescaptcha.com/createTask', json=json_data) as response:
        response_json = await response.json()
        if response_json['errorId'] != 0:
            logger.warning(response_json)
            return False
        task_id = response_json['taskId']
    for _ in range(120):
        data = {"clientKey": client_key, "taskId": task_id}
        async with session.post('https://api.yescaptcha.com/getTaskResult', json=data) as response:
            response_json = await response.json()
            if response_json['status'] == 'ready':
                return response_json['solution']['gRecaptchaResponse']
            else:
                await asyncio.sleep(1)
    return False


async def get_yescaptcha_turnstile_token(session: aiohttp.ClientSession) -> Union[bool, str]:
    json_data = {"clientKey": client_key,
                 "task": {"websiteURL": "https://artio.faucet.berachain.com/",
                          "websiteKey": "0x4AAAAAAARdAuciFArKhVwt",
                          "type": "TurnstileTaskProxylessM1"}, "softID": 109}
    async with session.post('https://api.yescaptcha.com/createTask', json=json_data) as response:
        response_json = await response.json()
        if response_json['errorId'] != 0:
            logger.warning(response_json)
            return False
        task_id = response_json['taskId']
    for _ in range(120):
        data = {"clientKey": client_key, "taskId": task_id}
        async with session.post('https://api.yescaptcha.com/getTaskResult', json=data) as response:
            response_json = await response.json()
            if response_json['status'] == 'ready':
                return response_json['solution']['token']
            else:
                await asyncio.sleep(1)
    return False


async def get_ez_captcha_google_token(session: aiohttp.ClientSession) -> Union[bool, str]:
    json_data = {
        "clientKey": client_key, "task": {"websiteURL": "https://artio.faucet.berachain.com/",
                                          "websiteKey": "6LfOA04pAAAAAL9ttkwIz40hC63_7IsaU2MgcwVH",
                                          "type": "ReCaptchaV3TaskProxyless"}, "appId": "34119"}
    async with session.post('https://api.ez-captcha.com/createTask', json=json_data) as response:
        response_json = await response.json()
        if response_json['errorId'] != 0:
            logger.warning(response_json)
            return False
        task_id = response_json['taskId']
    for _ in range(120):
        data = {"clientKey": client_key, "taskId": task_id}
        async with session.post('https://api.ez-captcha.com/getTaskResult', json=data) as response:
            response_json = await response.json()
            if response_json['status'] == 'ready':
                return response_json['solution']['gRecaptchaResponse']
            else:
                await asyncio.sleep(1)
    return False


async def get_ip(session: aiohttp.ClientSession) -> str:
    async with session.get(get_ip_url) as response:
        response_text = await response.text()
        print(f'http://{response_text.strip()}')
    # proxy 格式 : 'http://user:password@ip:port' or 'http://ip:port'
        # 生成1到3之间的随机浮点数
        wait_time = random.uniform(1, 2)
            # 程序等待这个随机时间
        await asyncio.sleep(wait_time)
        
    return f'http://{response_text.strip()}'


async def write_to_file(address: Union[Address, ChecksumAddress]):
    async with aiofiles.open(claim_success_file, 'a+') as f:
        await f.write(f'{address}\n')


async def read_to_file(file_path: str):
    async with aiofiles.open(claim_success_file, 'r') as success_file:
        claim_success = await success_file.read()

    async with aiofiles.open(file_path, 'r') as file:
        lines = await file.readlines()
     
    claim_list = [_address.strip() for _address in lines if _address.strip() not in claim_success]

    return claim_list


async def claim_faucet(address: Union[Address, ChecksumAddress], google_token: str, session: aiohttp.ClientSession):

    headers = {'authority': 'artio-80085-faucet-api-cf.berachain.com', 'accept': '*/*',
               'accept-language': 'zh-CN,zh;q=0.9', 'authorization': f'Bearer {google_token}',
               'cache-control': 'no-cache', 'content-type': 'text/plain;charset=UTF-8',
               'origin': 'https://artio.faucet.berachain.com', 'pragma': 'no-cache',
               'referer': 'https://artio.faucet.berachain.com/', 
               'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
    params = {'address': address}
    myproxy = await get_ip(session)
    proxies = {"https": myproxy}
    asysession = AsyncSession(timeout=120,headers= headers, impersonate="chrome120",proxies=proxies)

    response = await asysession.post(f'https://artio-80085-faucet-api-cf.berachain.com/api/claim?address={address}',data=json.dumps(params), params=params)
    response_text = response.text
    if 'try again' not in response_text and 'msg":"' in response_text:
        logger.success(response_text)
        await write_to_file(address)
    elif 'Txhash' in response_text:
        logger.success(response_text)
        await write_to_file(address)
    else:
        logger.warning(response_text.replace('\n', ''))


def get_solver_provider():
    provider_dict = {'yescaptcha': get_yescaptcha_turnstile_token, '2captcha': get_2captcha_turnstile_token}
    if solver_provider not in list(provider_dict.keys()):
        raise ValueError("solver_provider must be 'yescaptcha'")
    return provider_dict[solver_provider]


async def claim(address: Union[Address, ChecksumAddress], session: aiohttp.ClientSession):
    try:
        google_token = await get_solver_provider()(session)
        if google_token:
            await claim_faucet(address, google_token, session)
    except Exception as e:
        logger.warning(f'{address}:{e}')


async def run(file_path):
    sem = asyncio.Semaphore(max_concurrent)
    address_list = await read_to_file(file_path)
    async with aiohttp.ClientSession() as session:
        async def claim_wrapper(address):
            async with sem:
                await claim(address, session)

        await asyncio.gather(*[claim_wrapper(address) for address in address_list])



def process_fail():
    # 读取总的地址列表
    with open(address_file, 'r') as file:
        addresses = file.read().splitlines()

    # 读取成功处理过的地址列表
    with open(claim_success_file, 'r') as file:
        success_addresses = file.read().splitlines()

    # 使用集合操作找出失败的地址
    fail_addresses = set(addresses) - set(success_addresses)

    # 将失败的地址写入到新文件 address_fail.txt 中
    with open('/workspace/BeraChainTools/script/claim_fail.txt', 'w') as file:
        for address in fail_addresses:
            file.write(f"{address}\n")

    print("失败地址已写入到 address_fail.txt 文件中。")

def shuffle_file(file_path):
  """
  打乱文件行顺序并保存

  Args:
    file_path: 要打乱的文件路径

  Returns:
    None
  """

  # 读取文件内容
  with open(file_path, 'r') as f:
    lines = f.readlines()

  # 打乱行顺序
  random.shuffle(lines)

  # 写入文件
  with open(file_path, 'w') as f:
    f.writelines(lines)
if __name__ == '__main__':
    
    """
    如果你不能完全的读懂代码，不建议直接运行本程序避免造成损失
    运行时会读取当前文件夹下的claim_success.txt文本，跳过已经成功的地址
    单进程性能会有瓶颈,大概一分钟能领1000左右,自行套多进程或复制多开
    """
    import os

    os.truncate(claim_success_file, 0)
    # 验证平台key
    client_key = 'your client'
    # 目前支持使用yescaptcha 2captcha
    solver_provider = '2captcha'
    # 代理获取链接 设置一次提取一个 返回格式为text
    get_ip_url = "ip代理"
    # 并发数量
    max_concurrent = 2
    # 读取文件的路径 地址一行一个
    _file_path = address_file
    #读取文件打乱顺序并保存
    shuffle_file(address_file)
    asyncio.run(run(_file_path))
    #升成处理失败的钱包txt