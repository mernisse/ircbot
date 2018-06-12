# -*- coding: UTF-8 -*-
''' api.py (c) 2018 Matthew J Ernisse <matt@going-flying.com>
All Rights Reserved.

Serve a websocket API to provide bot commands.

Redistribution and use in source and binary forms,
with or without modification, are permitted provided
that the following conditions are met:

    * Redistributions of source code must retain the
      above copyright notice, this list of conditions
      and the following disclaimer.
    * Redistributions in binary form must reproduce
      the above copyright notice, this list of conditions
      and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import asyncio
import core
import json
import threading
import time
import websockets

from botlogger import err, log, logException


class ApiClient(object):
	""" Hold data for a client. """
	def __init__(self, socket, path):
		self.path = path
		self.socket = socket
		self.lastSeen = time.time()
		log("New ApiClient(): {}".format(self.getRemoteAddr()))

	def __repr__(self):
		return "<ApiClient: {}, lastseen: {}>".format(
			self.getRemoteAddr(),
			self.lastSeen
		)

	def getRemoteAddr(self):
		""" Return the remote address of the connection taking potential
		Proxy into account.
		"""
		if "X-Forwarded-For" in [
			i[0]
			for i in self.socket.raw_request_headers
		]:
			return [
				i[1]
				for i in self.socket.raw_request_headers
				if i[0] == "X-Forwarded-For"][0]
		else:
			return self.socket.remote_address[0]

	def touch(self):
		''' Update the last seen time of the client. '''
		self.lastSeen = time.time()

	def needsTouch(self):
		''' Return True if the client has not been seen in more than 5
		minutes.
		'''
		if time.time() - self.lastSeen >= 600:
			return True

		return False


class ApiServer(threading.Thread):
	""" Implement a websocket API to control the bot. """
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
		self.clients = []
		self.evt = asyncio.new_event_loop()
		self.server = None
		self.shouldStop = threading.Event()

	def broadcast(self, event):
		""" Send a message to all connected clients."""
		for client in self.clients:
			asyncio.ensure_future(
				self._sendEvent(client.socket, event),
				loop=self.evt
			)

	def run(self):
		""" Start the websocket server """
		log("ApiServer thread starting...")
		while not self.shouldStop.is_set():
			try:
				self.server = websockets.serve(
					self._handle,
					"::",
					8765,
					loop=self.evt
				)
				self.evt.run_until_complete(
					self.server
				)
				self.evt.run_forever()
			except Exception as e:
				err("ApiServer: Exception caught.")
				logException(e)
				break

		log("ApiServer: ending event loop...")
		self.server.ws_server.close()
		self.evt.run_until_complete(
			self.server.ws_server.wait_closed()
		)

		try:
			self.evt.run_until_complete(
				asyncio.gather(
					*asyncio.Task.all_tasks(loop=self.evt),
					loop=self.evt
				)
			)
		except asyncio.futures.CancelledError:
			pass

		self.evt.close()

	def stop(self):
		""" Shutdown the websocket server and exit the thread. """
		self.broadcast({"message": "serverStopping"})
		self.shouldStop.set()
		for client in self.clients:
			self.evt.call_soon_threadsafe(client.socket.close)

		if self.evt.is_running():
			self.evt.call_soon_threadsafe(self.evt.stop)

	async def _handle(self, socket, path):
		client = ApiClient(socket, path)
		self.clients.append(client)
		while not self.shouldStop.is_set():
			try:
				if client.needsTouch():
					await asyncio.wait_for(
						client.socket.ping(),
						timeout=2)
					client.touch()

			except asyncio.TimeoutError:
				log("ApiServer: Client {} timed out.".format(
					client.getRemoteAddr()
				))
				client.socket.close()
				self.clients.remove(client)
				return

			try:
				_msg = await asyncio.wait_for(
					socket.recv(),
					timeout=1
				)

				_msg = json.loads(_msg)
				client.touch()

				if _msg.get("request") == "listChannels":
					await self._sendMessage(socket, self.bot.channels)

				elif _msg.get("request") == "listModules":
					await self._sendMessage(socket, core.MODULES)

				elif _msg.get("request") == "listUsers":
					target = _msg.get("target")
					if not target:
						await self._sendError(socket, "incomplete request")
						continue

					if target not in self.bot.channels:
						await self._sendError(socket, "invalid channel")
						continue

					await self._sendMessage(socket, self.bot.chatters[target])

				elif _msg.get("request") == "privmsg":
					target = _msg.get("target")
					message = _msg.get("message")
					if not target or not message:
						await self._sendError(socket, "incomplete request")
						continue

					self.bot.msg(target, message)
					await self._sendMessage(socket, "done")

				elif _msg.get("request") == "reloadConfig":
					self.bot.factory.config.rehash()
					await self._sendMessage(socket, "done")

				else:
					await self._sendError(socket, "invalid request")

			except websockets.exceptions.ConnectionClosed:
				log("ApiServer: Client {} disconnected.".format(
					client.getRemoteAddr()
				))
				self.clients.remove(client)
				return

			except json.JSONDecodeError as e:
				err("unhandled raw message")
				logException(e)
				await socket.send(_msg)
				continue

			except asyncio.TimeoutError:
				pass

			except asyncio.futures.CancelledError:
				return

			except Exception as e:
				logException(e)
				return

	async def _sendError(self, socket, message):
		""" Send an Error response back to the client. """
		_resp = {"status": "error", "message": message}
		await socket.send(json.dumps(_resp))

	async def _sendEvent(self, socket, message):
		"""Send the given message back to the client as is. """
		_resp = message
		await socket.send(json.dumps(_resp))

	async def _sendMessage(self, socket, message):
		""" Send a reply message back to the client. """
		_resp = {"status": "ok", "message": message}
		await socket.send(json.dumps(_resp))


def action(bot, user, channel, msg):
	nick = user.split("!", 1)[0]
	_event = {
		"source": channel,
		"nick": nick,
		"message": msg,
		"type": "action"
	}
	apiServer.broadcast(_event)


def connectionMade(bot):
	global apiServer
	if apiServer:
		err("api.connectionMade(): called while thread running.")
		return

	apiServer = ApiServer(bot)
	apiServer.start()


def connectionLost(bot):
	global apiServer
	try:
		apiServer.stop()
	except Exception as e:
		logException(e)
		return

	apiServer.join()


def privmsg(self, user, channel, msg):
	nick = user.split("!", 1)[0]
	src = nick
	eType = "privmsg"
	if channel != self.nickname:
		src = channel
		_msg = self._forMe(msg)
		if not _msg:
			if not msg.startswith("!"):
				eType = "pubmsg"
		else:
			msg = _msg

	_event = {
		"source": src,
		"nick": nick,
		"message": msg,
		"type": eType
	}
	apiServer.broadcast(_event)


def userJoined(self, user, channel):
	_event = {
		"source": channel,
		"nick": user,
		"type": "join"
	}
	apiServer.broadcast(_event)


def userLeft(self, user, channel):
	_event = {
		"source": channel,
		"nick": user,
		"type": "part"
	}
	apiServer.broadcast(_event)


apiServer = None
core.register_module(__name__)
