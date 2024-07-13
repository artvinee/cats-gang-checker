import os
import random

from utils.cats import Cats
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio

max_retries = config.DELAYS['MAX_ATTEMPTS']


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    cat = Cats(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await cat.login():
        logger.success(f"Thread {thread} | {account} | Login")
        await task(cat, thread, account)
    else:
        logger.error(f"Thread {thread} | {account} | Failed to login")
        await cat.logout()


async def task(cat, thread, account):
    try:
        for attempt in range(max_retries):
            status, age, rewards, ref_code = await cat.user()
            if status is None:
                create = await cat.create()
                if create is True:
                    status, age, rewards, ref_code = await cat.user()
                    logger.success(f"Thread {thread} | {account} | Age of account: {age}. Balance: {rewards}")
                    break
                else:
                    if attempt < max_retries:
                        logger.error(f"Thread {thread} | {account} | Error to check age and balance. Try again..")
                        await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                        continue
            elif status is True:
                logger.success(f"Thread {thread} | {account} | Age of account: {age}. Balance: {rewards}")
                break
            else:
                if attempt < max_retries:
                    logger.error(f"Thread {thread} | {account} | Error to check age and balance. Try again..")
                    await asyncio.sleep(random.randint(config.DELAYS['REPEAT'][0], config.DELAYS['REPEAT'][1]))
                    continue
                else:
                    break
        await cat.logout()
    except Exception as e:
        logger.error(f"Thread {thread} | {account} | Error: {e}")


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(
            Cats(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Balance', 'Age', 'Referral link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
