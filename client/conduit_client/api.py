import logging
import asyncio
import threading
import time
from http import HTTPStatus

from aiohttp import web

from conduit_client.tunnel import Tunnels, Tunnel


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


class REST:
    def __init__(self, tunnels=None, host='localhost', port=0, loop=None):
        self.tunnels = Tunnels() if tunnels is None else tunnels
        self._host = host
        self._port = port
        self._loop = loop or asyncio.new_event_loop()
        self._running = threading.Event()
        self._stopping = False
        self._app = web.Application()
        self._app.router.add_route('*', '/tunnels/{domain:.*}', self._handler)
        self._runner = None
        self._site = None

    @property
    def port(self):
        if not self._running.is_set():
            raise ValueError('Cannot determine port if not running')
        return self._site._server.sockets[0].getsockname()[1]

    async def _handler(self, request):
        domain = request.match_info.get('domain')

        if request.method == 'GET':
            if not domain:
                obj = self.tunnels
            else:
                try:
                    obj = self.tunnels[domain]
                except KeyError:
                    return web.Response(status=HTTPStatus.NOT_FOUND)

            return web.json_response(obj.to_dict())

        elif request.method == 'POST':
            obj = await request.json()
            if not domain:
                tunnels = {}
                for domain, data in obj.items():
                    data['domain'] = domain
                    tunnels[domain] = Tunnel.from_dict(data)
                self.tunnels.clear()
                self.tunnels.update(tunnels)
            else:
                obj['domain'] = domain
                self.tunnels[domain] = Tunnel.from_dict(obj)
            return web.json_response(
                self.tunnels.to_dict(), status=HTTPStatus.CREATED)

        elif request.method == 'DELETE':
            if not domain:
                self.tunnels.clear()
            else:
                try:
                    self.tunnels.pop(domain)
                except KeyError:
                    return web.Response(status=HTTPStatus.NOT_FOUND)
            return web.Response(status=HTTPStatus.NO_CONTENT)

    async def _run(self):
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()
        self._running.set()
        while not self._stopping:
            await asyncio.sleep(0.1)
        LOGGER.info('Stopping server on %i', self.port)
        await self._runner.cleanup()

    def _run_in_thread(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._run())

    def start(self):
        t = threading.Thread(target=self._run_in_thread)
        t.start()
        self._running.wait()

    def stop(self):
        self._stopping = True
