import asyncio
import random
from urllib.parse import unquote

import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from loguru import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName

from data import config


class Cats:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        self.query = None
        self.tma = None

        headers = {
            'User-Agent': UserAgent(os='android').random
        }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        await self.login()
        status, age, rewards, ref_code = await self.user()

        if status is None:
            create = await self.create()
            if create is True:
                status, age, rewards, ref_code = await self.user()
        elif status is True:
            pass

        referral_link = f'https://t.me/catsgang_bot/join?startapp={ref_code}'

        await asyncio.sleep(random.uniform(5, 7))

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, rewards, age, referral_link, proxy]

    async def do_task(self, task):
        try:
            resp = await self.session.post(
                f"https://cats-backend-production.up.railway.app/tasks/{task}/complete", headers=self.tma)
            if resp.status == 200:
                r = await resp.json()
                if r['success'] is True:
                    return True
            else:
                return False
        except Exception as e:
            print(e)

    async def get_tasks(self):
        try:
            resp = await self.session.get(f"https://cats-backend-production.up.railway.app/tasks/user", headers=self.tma)
            if resp.status == 200:
                r = await resp.json()
                return r['tasks']
            else:
                return False
        except Exception as e:
            print(e)

    async def user(self):
        try:
            resp = await self.session.get(f'https://cats-backend-production.up.railway.app/user', headers=self.tma)
            if resp.status == 200:
                r = await resp.json()
                if r['telegramAgeReward']:
                    status = True
                    age = r['telegramAge']
                    totalreward = r['totalRewards']
                    refcode = r['referrerCode']
                    return status, age, totalreward, refcode
                else:
                    return False, False, False, False
            elif resp.status == 404:
                return None, None, None, None
            else:
                return False, False, False, False
        except Exception as e:
            logger.error(f"Join: {e}")

    async def logout(self):
        await self.session.close()

    async def create(self):
        try:
            resp = await self.session.post(
                f"https://cats-backend-production.up.railway.app/user/create?referral_code={config.REF_CODE}", headers=self.tma)
            if resp.status == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        self.query = await self.get_tg_web_data()
        self.tma = {'Authorization': f"tma {self.query}"}

        if self.query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None
        else:
            return True

    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            try:
                await self.client.join_chat('@Cats_housewtf')
            except Exception as e:
                print(e)

            ref_code = config.REF_CODE

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('catsgang_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('catsgang_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param=ref_code
            ))

            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            return query

        except Exception as e:
            logger.error(f"Tg Data: {e}")
            return None

