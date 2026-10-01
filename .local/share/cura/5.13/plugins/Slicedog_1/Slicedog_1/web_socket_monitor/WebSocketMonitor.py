from PyQt6 import QtCore

from UM.Logger import Logger

import asyncio
import websockets
import threading
import json

from Slicedog_1.message_manager.MessageType import MessageType
from Slicedog_1.utils.server_connection import server_wss

class WebSocketMonitor(QtCore.QObject):
    finished = QtCore.pyqtSignal(str, MessageType, str, str, bool)
    # finished = QtCore.pyqtSignal(str, MessageType, str, str)
    progress = QtCore.pyqtSignal(str, MessageType, str, str)

    def __init__(self, token: str, reconnect_delay: float = 3.0):
        super().__init__()
        self._uri = f"{server_wss}/ws?token={token}"
        self._stop_event = threading.Event()
        self._reconnect_delay = reconnect_delay

    def stop(self):
        self._stop_event.set()

    def run(self):
        # Run the asyncio loop inside the QThread
        asyncio.run(self._connectLoop())

    async def _connectLoop(self):
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self._uri) as ws:
                    Logger.log('d', "WebSocketWorker: Connected.")
                    await self._listen(ws)
            except Exception as e:
                await asyncio.sleep(self._reconnect_delay)

    async def _listen(self, ws):
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                    type_ = data.get("type")
                    payload = data.get("payload")
                    Logger.log('d', f"Payload: {payload}")

                    if type_ == "FEEDBACK":
                        info = payload['message']
                        status = payload['status']
                        iteration_info = payload['iteration_info']
                        self.progress.emit(info, MessageType.FEEDBACK, status, iteration_info)
                    elif type_ == "RESULT":
                        status = payload['status']
                        result_uri = payload['result_gcs_uri']
                        # model_filepath = payload['result_gcs_uri']
                        # metadata_filepath = payload['metadata_gcs_uri']
                        info = payload['message']
                        new_user = payload['new_user']
                        if status == "SUCCEEDED":
                            message_type = MessageType.OPTIMIZATION_SUCCESS
                        elif status == "CANCELLED":
                            message_type = MessageType.OPTIMIZATION_CANCELLED_BY_USER
                        else:
                            message_type = MessageType.OPTIMIZATION_FAIL
                        self.finished.emit(info, message_type, status, result_uri, new_user)
                        # self.finished.emit(info, message_type, model_filepath, metadata_filepath)
                    else:
                        self.progress.emit(f"Unknown message type: {type_}", MessageType.UNKNOWN, None)
                        Logger.log('w', f"Unknown message type: {type_}")
                except json.JSONDecodeError:
                    self.progress.emit(f"Non-JSON message: {message}", MessageType.UNKNOWN, None)
                    Logger.log('w', f"Non-JSON message: {message}")
        except websockets.ConnectionClosed:
            pass
            # self.progress.emit('', MessageType.NO_CONNECTION)
        except Exception as e:
            self.progress.emit(f"Listening failed: {e}", MessageType.UNKNOWN, None)
            Logger.log('w', f"Listening failed: {e}")