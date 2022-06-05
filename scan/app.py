import asyncio
from aiohttp import ClientSession, client_exceptions, web
import json
import logging.handlers


logger = logging.getLogger('logger')
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(asctime)s | %(lineno)s | %(message)s",
)
handler = logging.handlers.SysLogHandler()
logger.addHandler(handler)


async def counter(request):
    try:
        logger.info(f"recd ip: {request.match_info['ip']}; begin port: {request.match_info['begin_port']}; "
                    f"end port: {request.match_info['end_port']}")
        begin_port = int(request.match_info['begin_port'])
        end_port = int(request.match_info['end_port'])
        if end_port < begin_port:
            begin_port, end_port = end_port, begin_port
        tasks = [scan4port(request.match_info['ip'], i) for i in range(begin_port, end_port + 1)]
        logger.info(f"Search start")
        res = await asyncio.gather(*tasks)
        logger.info("Result processing")
        response = []
        for i, j in res:
            if i == 'None':
                response.append({"port": j, "state": 'close'})
            else:
                response.append({"port": j, "state": 'open'})
        res = json.dumps(response)
        logger.info("Results are ready")
        return web.json_response(res)
    except ValueError:
        logger.exception('Ports are not numbers')
        return web.Response(text="Ports must be numbers")


async def scan4port(ip, port):
    async with ClientSession() as session:
        try:
            resp = await session.get(f"http://{ip}:{port}/")
            resp.close()
            return resp.status, port
        except client_exceptions.ClientConnectorError:
            return 'None', port


if __name__ == "__main__":
    app = web.Application()
    app.router.add_route('GET', '/scan/{ip}/{begin_port}/{end_port}', counter)
    web.run_app(app)
