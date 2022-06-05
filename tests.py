from aiohttp.test_utils import AioHTTPTestCase
from aiohttp import web
from json import dumps
from scan.app import counter


class MyAppTestCase(AioHTTPTestCase):

    date = dumps([{"port": 8080, "state": "close"}, {"port": 8081, "state": "close"}])

    async def get_application(self):
        app = web.Application()
        app.router.add_route('GET', '/scan/{ip}/{begin_port}/{end_port}', counter)
        return app

    async def test_connect(self):
        async with self.client.request('GET', '/scan/127.0.0.1/8080/8081') as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.json()
        self.assertEqual(self.date, text)
