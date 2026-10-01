import io
import socket
import urllib
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from PyQt6 import QtCore
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog

from UM.i18n import i18nCatalog
from UM.Application import Application
from UM.Extension import Extension
from UM.PluginRegistry import PluginRegistry
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.FileHandler.WriteFileJob import WriteFileJob
from UM.Mesh.MeshWriter import MeshWriter
from UM.Mesh.ReadMeshJob import ReadMeshJob
from UM.Scene.SceneNodeSettings import SceneNodeSettings
from UM.Scene.Selection import Selection
from UM.Settings.SettingInstance import SettingInstance
from UM.Message import Message
from UM.Qt.QtApplication import QtApplication
from UM.Logger import Logger

from cura.Scene.CuraSceneNode import CuraSceneNode
from cura.Scene.ConvexHullDecorator import ConvexHullDecorator
from cura.Scene.BlockSlicingDecorator import BlockSlicingDecorator
from cura.Scene.SliceableObjectDecorator import SliceableObjectDecorator
from cura.Scene.BuildPlateDecorator import BuildPlateDecorator
from cura.Settings.SettingOverrideDecorator import SettingOverrideDecorator

import os.path
import sys
import time
import threading

# Load bundled packages
libs_path = os.path.join(os.path.dirname(__file__), "../libs")
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

import tempfile
import requests
import json
import time
import numpy as np
import copy
import tarfile
from google_auth_oauthlib.flow import InstalledAppFlow
from scipy.optimize import least_squares
from dataclasses import asdict, replace

from Slicedog_1.message_manager.MessageType import MessageType
from Slicedog_1.message_manager.MessageManager import MessageManager
from Slicedog_1.web_socket_monitor.WebSocketMonitor import WebSocketMonitor
from Slicedog_1.api_wrapper.SlicedogApiWrapper import SlicedogApiWrapper
from Slicedog_1.utils.slicedog_dataclasses import CurrentForce
from Slicedog_1.mesh_manager.MeshManager import MeshManager
from Slicedog_1.geometry_analyzer import geometry_analyzer
from .SlicedogHighlightsObject import SlicedogHighlightManager, QtHighlightManagerWrapper
from Slicedog_1.utils.server_connection import server_https
from Slicedog_1.utils.cura_utils import getPrintableNodes

i18n_catalog = i18nCatalog("Slicedog_1")

class SlicedogExtension(Extension):
    def __init__(self):
        super().__init__()
        self._face = None
        self._mesh_manager = MeshManager()
        self._current_force = CurrentForce()
        self._surface_selection = 'flat_surface'
        self._objects = {}
        self._anchors = {}
        self._forces = {}
        self._temp_path = ''
        self._stream = None
        self._is_importing = False
        self._is_import_success = False
        self._source_node = None
        self._result_offset = None
        self._import_metadata = {}
        self._message_manager = MessageManager()
        self._optimization_safety_ratio = 3.0
        self._optimization_strategy = 'Material'
        self._optimization_auto_lower_safety_ratio = True
        self._ws_thread = QtCore.QThread()
        self._ws_worker = None
        self._access_token = None
        self._check_slicing_timer = QtCore.QTimer()
        self._check_slicing_timer.setInterval(500)
        self._check_slicing_start_time = None
        self._material_diff_slicing_result = None
        self._current_step = 0
        self._steps_confirmed_flags = [False, False, False, False]
        self._rotation_active = False
        self._select_multiple_areas = True
        self._last_feedback = ""
        self._last_feedback_status = ""
        self._last_status_feedback = ""
        self._last_iteration_feedback = ""
        self._current_iteration_info = None
        self._should_use_slice = True
        self._oauth_server = None
        self._oauth_thread = None
        self._oauth_session = None
        self._oauth_port = self._pick_oauth_port()

        self._expected_extruder_global_settings = {
            'layer_height': 0.15,
        }

        self._expected_extruder_local_settings = {
            'wall_line_count': 3,
            'line_width': 0.4,
            'infill_pattern': 'triangles',
            'zig_zaggify_infill': True
        }
        self._user_infill = None

        self._callbacks = {
            "current_force": [],
            "surface_selection": [],
            "objects": [],
            "anchors": [],
            "forces": [],
            "optimization_strategy": [],
            "optimization_safety_ratio": [],
            "optimization_auto_lower_safety_ratio": [],
            "access_token": [],
            "current_step": [],
            "steps_confirmed_flags": [],
            "rotation_active": [],
            "select_multiple_areas": [],
            "feedback": [],
            "iteration_feedback": [],
            "status_feedback": [],
            "popup_requested": []
        }

        self.onChanged("current_force", self._onCurrentForceChangedCb)

        self._registerMessages()

        self._highlights_manager = SlicedogHighlightManager(self, Application.getInstance().getController().getScene().getRoot())
        self._highlights_manager_wrapper = QtHighlightManagerWrapper(manager=self._highlights_manager)

        self._api_wrapper = SlicedogApiWrapper(self)

    def reset(self):
        self.setFace(None)
        self.resetCurrentForce()
        self.setSurfaceSelection('flat_surface')
        self.setAnchors({})
        self.setForces({})
        self._temp_path = ''
        self._stream = None
        self.resetImportTrack()
        self._source_node = None
        self._result_offset = None
        self._import_metadata = {}
        self.setOptimizationStrategy('Material')
        self.setOptimizationSafetyRatio(3.0)
        self.setOptimizationAutoLowerSafetyRatio(True)
        self.setCurrentStep(0)
        self.resetStepsConfirmedFlags()
        self.setLastFeedback("")
        self.setRotationActive(False)
        self.setSelectMultipleAreas(True)
        self.getHighlightManager().setEnabled(False)
        self._should_use_slice = True

    # TODO this can fail, try to figure out better way as it seems that Google Cloud does not support wildcard for ports
    @staticmethod
    def _pick_oauth_port():
        port_pool = list(range(51372, 51392))

        for port in port_pool:
            try:
                sock = socket.socket()
                sock.bind(('localhost', port))
                sock.close()
                Logger.log('d', f'Selected port {port}')
                return port
            except OSError:
                continue

        raise RuntimeError("No available port from OAuth pool!")

    def isSelectedMeshCached(self):
        return self._mesh_manager.getCachedMeshWithAdjacency(self._face[0].getName()) is not None

    def setFace(self, face):
        self._face = face
        if self._face is not None:
            self._highlights_manager._mesh_data = face[0].getMeshData()
            self._mesh_manager.setMeshData(face[0].getMeshData())

    def getFace(self):
        return self._face

    def _createDialogue(self, filepath):
        qml_file_path = os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), filepath)
        main_window = QtApplication.getInstance().getMainWindow()
        component = Application.getInstance().createQmlComponent(qml_file_path)
        component.setTransientParent(main_window)
        screen = main_window.screen()
        geometry = screen.geometry()

        margin_x = int(geometry.width() * 0.10)
        margin_y = int(geometry.height() * 0.10)

        component.setX(geometry.x() + margin_x)
        component.setY(geometry.y() + margin_y)

        return component

    def getHighlightManager(self, engine=None, script_engine=None):
        return self._highlights_manager

    def getHighlightManagerWrapper(self, engine=None, script_engine=None):
        return self._highlights_manager_wrapper

    def getMessageManager(self):
        return self._message_manager

    def _registerMessages(self):
        # NONE

        # NO_CONNECTION
        no_connection_message = Message(title="Can't reach the server",
                                        text="Most likely the server is not running or you are not connected to the internet.",
                                        message_type=Message.MessageType.ERROR,
                                        lifetime=0)
        self._message_manager.registerMessage(MessageType.NO_CONNECTION, no_connection_message)

        # REGISTRATION_FAILED
        authorization_error_message = Message(title='Registration failed',
                                              text='',
                                              message_type=Message.MessageType.ERROR,
                                              lifetime=0)
        self._message_manager.registerMessage(MessageType.REGISTRATION_FAILED, authorization_error_message)

        # OPTIMIZATION_NOT_RUNNING
        optimization_not_running_message = Message(title='Optimization is not running',
                                                   message_type=Message.MessageType.WARNING,
                                                   lifetime=0)
        self._message_manager.registerMessage(MessageType.OPTIMIZATION_NOT_RUNNING, optimization_not_running_message)

        # OPTIMIZATION_STILL_RUNNING
        optimization_still_running_message = Message(title='Optimization in progress, please wait',
                                                     message_type=Message.MessageType.WARNING,
                                                     text="Your optimization is still processing, please wait",
                                                     lifetime=0)
        self._message_manager.registerMessage(MessageType.OPTIMIZATION_STILL_RUNNING,
                                               optimization_still_running_message)

        # OPTIMIZATION_SUCCESS
        optimization_success_message = Message(title='Optimization result',
                                               message_type=Message.MessageType.POSITIVE,
                                               lifetime=0)
        self._message_manager.registerMessage(MessageType.OPTIMIZATION_SUCCESS, optimization_success_message)

        # OPTIMIZATION_FAIL
        optimization_fail_message = Message(title='Optimization error',
                                            message_type=Message.MessageType.ERROR,
                                            lifetime=0)
        self._message_manager.registerMessage(MessageType.OPTIMIZATION_FAIL, optimization_fail_message)

        # # OPTIMIZATION_CANCELLED_BY_USER
        # optimization_cancelled_by_user_message = Message(title='Optimization cancelled',
        #                                                  text='Optimization cancelled by user',
        #                                                  message_type=Message.MessageType.POSITIVE,
        #                                                  lifetime=0)
        # self._message_manager.registerMessage(MessageType.OPTIMIZATION_CANCELLED_BY_USER,
        #                                        optimization_cancelled_by_user_message)

        # SCENE_NOT_READY
        scene_not_ready_message = Message(title="Invalid print for Slicedog",
                                          message_type=Message.MessageType.WARNING,
                                          text="I need exactly one model to start sniffing out for the material - not none, not two or more",
                                          lifetime=0)
        self._message_manager.registerMessage(MessageType.SCENE_NOT_READY, scene_not_ready_message)

        # # LIMIT_EXCEEDED
        # limit_exceeded_message = Message(title='Uh-oh, I ran out of execution time. Check Common issues to see how to fix it.',
        #                                  message_type=Message.MessageType.WARNING,
        #                                  lifetime=0)
        # limit_exceeded_message.addAction(
        #     action_id="open_help",
        #     name="Common issues",
        #     icon="",
        #     description="Open help page",
        #     button_style=Message.ActionButtonStyle.LINK
        # )
        # limit_exceeded_message.pyQtActionTriggered.connect(lambda message, action: QDesktopServices.openUrl(QtCore.QUrl("https://slicedog.com/help/common-issues/")))
        # self._message_manager.registerMessage(MessageType.LIMIT_EXCEEDED, limit_exceeded_message)

        # REGISTRATION_SENT
        registration_sent_message = Message(title="Thanks for signing up! I've passed your request to my human friends for approval",
                                            message_type=Message.MessageType.POSITIVE,
                                            lifetime=0)
        self._message_manager.registerMessage(MessageType.REGISTRATION_SENT, registration_sent_message)

        # # LOG_IN_OUT_MESSAGE
        # log_in_out_message = Message(title="",
        #                              message_type=Message.MessageType.POSITIVE,
        #                              lifetime=0)
        # self._message_manager.registerMessage(MessageType.LOG_IN_OUT_MESSAGE, log_in_out_message)

        # # TOO_MANY_REQUESTS
        # too_many_requests_message = Message(title="Too many requests detected",
        #                                     message_type=Message.MessageType.WARNING,
        #                                     text="Please wait a little before trying again",
        #                                     lifetime=0)
        # self._message_manager.registerMessage(MessageType.TOO_MANY_REQUESTS, too_many_requests_message)

        # LOG_IN_ERROR
        login_message = Message(title='Authorization failed',
                                message_type=Message.MessageType.ERROR,
                                text='You are not logged in - please log in to continue',
                                lifetime=0)
        login_message.addAction('LOG_IN', "Log in", "", "")
        login_message.addAction('REGISTER', "Register", "", "")
        login_message.actionTriggered.connect(self._loginErrorAction)
        self._message_manager.registerMessage(MessageType.LOG_IN_ERROR, login_message)

        # UPDATE_EXTRUDER_SETTINGS_REQUEST
        text = ''
        for key, value in (self._expected_extruder_local_settings | self._expected_extruder_global_settings).items():
            formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
            text += f"{formatted_key} = {value}\n"
        update_extruder_setting_request = Message(
            title='Unsupported settings detected',
            text="Looks like some print settings of an active extruder aren't Slicedog ready. "
                 "No worries - just click on UPDATE and I'll change them for you and continue",
            # text=f'Slicedog expects the following settings to be set for active extruder:\n{text}\nYou can click on '
            #      f'\"Update\" to automatically update the settings',
            lifetime=0)
        # update_extruder_setting_request.addAction('Update',
        #                                 i18n_catalog.i18nc("@Update", "Update"),
        #                                 "",  # icon
        #                                 "description",  # description
        #                                 # button_style=Message.ActionButtonStyle.SECONDARY
        #                                 )
        # update_extruder_setting_request.actionTriggered.connect(self.updateExtruderSettings)
        # self._message_manager.registerMessage(MessageType.UPDATE_EXTRUDER_SETTINGS_REQUEST, update_extruder_setting_request)

        # OPEN_SAMPLES
        open_samples_message = Message(message_type=Message.MessageType.NEUTRAL,
                                       title="",
                                       text="",
                                       lifetime=0)
        open_samples_message.addAction('Open samples',
                                       i18n_catalog.i18nc("@Open samples", "Open samples"),
                                       "",
                                       "description",
                                       )
        open_samples_message.actionTriggered.connect(self.openSamplesFolder)
        self._message_manager.registerMessage(MessageType.OPEN_SAMPLES, open_samples_message)

        # SAMPLE_SETUP
        sample_setup_message = Message(message_type=Message.MessageType.NEUTRAL,
                                       title="Sample loaded. Setup guide available",
                                       text="Click Open Web Guide to see where to place forces and fixed points",
                                       lifetime=0)
        sample_setup_message.addAction('Open Web Guide',
                                       i18n_catalog.i18nc("@Open Web Guide", "Open Web Guide"),
                                       "",
                                       "description",
                                       )
        sample_setup_message.pyQtActionTriggered.connect(lambda message, action: QDesktopServices.openUrl(QtCore.QUrl("https://slicedog.com/sample-setup/")))
        self._message_manager.registerMessage(MessageType.SAMPLE_SETUP, sample_setup_message)

        # PREVIOUS_STEP_NOT_CONFIRMED
        not_confirmed_message = Message(title="Hold on! There’s still a step that needs a treat",
                                        message_type=Message.MessageType.WARNING,
                                        text="",
                                        lifetime=0)
        self._message_manager.registerMessage(MessageType.PREVIOUS_STEP_NOT_CONFIRMED, not_confirmed_message)

        # MISSING_USER_ACTION
        missing_user_action_message = Message(title="Hold on! I need you to do something more",
                                              message_type=Message.MessageType.WARNING,
                                              lifetime=0)
        self._message_manager.registerMessage(MessageType.MISSING_USER_ACTION, missing_user_action_message)

        # UNKNOWN
        general_error_message = Message(title='Unknown or unhandled error occurred',
                                        message_type=Message.MessageType.ERROR,
                                        lifetime=0)
        self._message_manager.registerMessage(MessageType.UNKNOWN, general_error_message)

    def logInWithGoogle(self, on_token_ready, is_registering=False):
        port = self._oauth_port

        session_id = str(uuid.uuid4())
        self._oauth_session = session_id

        r = requests.get(f"{server_https}/auth/google/start",
                         params={"port": port, "session_id": session_id})
        data = r.json()
        login_url = data["login_url"]

        if self._oauth_server is not None:
            try:
                self._oauth_server.shutdown()
                self._oauth_server.server_close()
            except:
                pass
            self._oauth_server = None

        auth_code_holder = {"code": None}

        class OAuthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)

                code = params.get("code", [None])[0]
                state = params.get("state", [None])[0]

                if state != self.server.gui_session_id:
                    self.send_response(410)
                    self.end_headers()
                    self.wfile.write(b"This login attempt has expired.")
                    return

                auth_code_holder["code"] = code

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Login successful. You can close this window.")

            def log_message(self, *args):
                return

        self._oauth_server = HTTPServer(("localhost", port), OAuthHandler)
        self._oauth_server.gui_session_id = session_id
        self._oauth_thread = threading.Thread(
            target=self._oauth_server.serve_forever,
            daemon=True
        )
        self._oauth_thread.start()

        webbrowser.open(login_url)

        while auth_code_holder["code"] is None:
            time.sleep(0.1)

        code = auth_code_holder["code"]
        self._oauth_server.shutdown()
        self._oauth_server.server_close()

        if code is None:
            raise Exception("Google login failed: no code received")

        r2 = requests.post(f"{server_https}/auth/google/exchange",
                           data={"code": code, "port": port})
        if r2.status_code != 200:
            raise Exception("Backend failed to exchange code")

        google_token = r2.json()["google_token"]

        on_token_ready(google_token, is_registering)

    def logOut(self):
        if self._ws_worker is not None:
            self._ws_worker.stop()
            self._ws_thread.quit()
            # self._ws_thread.wait()
        self.setAccessToken(None)
        # self._message_manager.showMessage(
        #     MessageType.LOG_IN_OUT_MESSAGE,
        #     "Logged out"
        # )

    def isLoggedIn(self):
        return self._access_token is not None

    def onLogInGoogleCompleted(self, id_token, is_registering=False):
        if is_registering:
            self.registerToSlicedog(id_token)
        else:
            self.logInToSlicedog(id_token)

    def logInToSlicedog(self, id_token):
        try:
            # Send token to backend
            response = requests.post(f"{server_https}/auth/verify", data={"google_token": id_token}, timeout=5)
        except requests.ConnectionError as e:
            Logger.log('e', f'ConnectionError during upload: {e}')
            self._emit("popup_requested", "noConnection")
            # self._message_manager.showMessage(MessageType.NO_CONNECTION)
            return
        except Exception as e:
            Logger.log('e', f'Exception occurred while trying to access Slicedog server. {e}')
            self._emit("popup_requested", "serverNotReachable")
            # self._message_manager.showMessage(
            #     MessageType.UNKNOWN,
            #     f'Error while trying to access Slicedog server: error type {e.__class__.__name__}')
            return

        if response.status_code == 200:
            self.setAccessToken(response.json().get('access_token', None))

            self._ws_worker = WebSocketMonitor(token=f"{self._access_token}")
            self._ws_worker.moveToThread(self._ws_thread)

            self._ws_worker.progress.connect(self.onFeedbackUpdated)
            self._ws_worker.finished.connect(self.onOptimizationFinished)

            self._ws_thread.started.connect(self._ws_worker.run)
            self._ws_thread.start()
            self._message_manager.hideMessage(MessageType.LOG_IN_ERROR)

            if response.json().get('new_user', False):
                self._message_manager.showMessage(
                    message_type=MessageType.OPEN_SAMPLES,
                    text="For the best first experience, try running our sample model. Click on Open samples button",
                    title="Tip for first use"
                )
            # self._message_manager.showMessage(
            #     MessageType.LOG_IN_OUT_MESSAGE,
            #     "Log in successful"
            # )
        elif response.status_code == 429:
            self.setLastFeedback("Too many requests detected. Please wait a little before trying again")
            # self._message_manager.showMessage(MessageType.TOO_MANY_REQUESTS)
        elif response.status_code == 404:
            self._emit("popup_requested", "userNotRegistered")
        else:
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(
            #     MessageType.LOG_IN_ERROR,
            #     response.json().get('detail', 'User not registered, please register first')
            # )

    def registerToSlicedog(self, id_token):
        try:
            response = requests.post(f"{server_https}/auth/register", data={"google_token": id_token})
        except requests.ConnectionError as e:
            Logger.log('e', f'ConnectionError during upload: {e}')
            self._emit("popup_requested", "noConnection")
            # self._message_manager.showMessage(MessageType.NO_CONNECTION)
            return
        except Exception as e:
            Logger.log('e', f'Exception occurred while trying to access Slicedog server: {e}')
            self._emit("popup_requested", "serverNotReachable")
            # self._message_manager.showMessage(
            #     MessageType.UNKNOWN,
            #     f'Error while trying to access Slicedog server: error type {e.__class__.__name__}')
            return

        if response.status_code == 200:
            self._emit("popup_requested", "registeredInfo")
            # self.setLastFeedback("Thanks for signing up! I've passed your request to my human friends for approval")
            # self._message_manager.showMessage(MessageType.REGISTRATION_SENT,
            #                                   "Thanks for signing up! I've passed your request to my human friends for approval")
        elif response.status_code == 409:
            self._emit("popup_requested", "userAlreadyRegistered")
            # self._message_manager.showMessage(MessageType.REGISTRATION_FAILED,
            #                                   response.json().get('detail', 'User already registered'))
        elif response.status_code == 429:
            self.setLastFeedback("Too many requests detected. Please wait a little before trying again")
            # self._message_manager.showMessage(MessageType.TOO_MANY_REQUESTS)
        else:
            self._emit("popup_requested", "unknownErrorWhileRegistering")
            # self._message_manager.showMessage(MessageType.UNKNOWN,
            #                                   response.json().get('detail', f"Something went wrong during registration. Please contact support"))

    def exportStl(self):
        # TODO this needs to be handled differently - maybe we should check if optimization is running on reconnecting?
        if self.isOptimizationRunning():
            Logger.log('w', 'Last optimization still running')
            self.setLastFeedback("Your optimization is still processing, please wait")
            # self._message_manager.showMessage(MessageType.OPTIMIZATION_STILL_RUNNING)
            return False

        if not self.isLoggedIn():
            self._emit("popup_requested", "login")
            # self._message_manager.showMessage(MessageType.LOG_IN_ERROR)
            return False

        self._is_import_success = False

        # Create a temporary file for STL
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".stl")
        self._temp_path = temp_file.name
        temp_file.close()

        self._stream = open(self._temp_path, "w")

        self._source_node = Selection.getSelectedObject(0)
        if self._source_node is None:
            self._source_node = getPrintableNodes()[0]

        global_stack = Application.getInstance().getGlobalContainerStack()
        if not global_stack:
            self.setLastFeedback("Unexpected CURA state - missing global stack!")
            # self._message_manager.showMessage(MessageType.UNKNOWN, "Unexpected CURA state - missing global stack!")
            return False

        model_extruder = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
        extruder_found = False
        is_all_already_set = True
        for extruder_stack in global_stack.extruderList:
            if model_extruder == extruder_stack.id:
                extruder_found = True
                self._user_infill = extruder_stack.getProperty('infill_sparse_density', 'value')
                for k, v in self._expected_extruder_global_settings.items():
                    gsv = global_stack.getProperty(k, 'value')
                    if isinstance(gsv, float):
                        is_already_set = np.isclose(gsv, v)
                    else:
                        is_already_set = gsv == v
                    is_all_already_set &= is_already_set

                for k, v in self._expected_extruder_local_settings.items():
                    esv = extruder_stack.getProperty(k, 'value')
                    if isinstance(esv, float):
                        is_already_set = np.isclose(esv, v)
                    else:
                        is_already_set = esv == v
                    is_all_already_set &= is_already_set

        if not is_all_already_set:
            self._emit("popup_requested", "updateExtruderSettings")
            # self._message_manager.showMessage(MessageType.UPDATE_EXTRUDER_SETTINGS_REQUEST)
            return False

        if not extruder_found:
            self.setLastFeedback("Unexpected CURA state - model extruder not found in global stack!")
            # self._message_manager.showMessage(MessageType.UNKNOWN, "Unexpected CURA state - model extruder not found in global stack!")
            return False

        nodes = [self._source_node]

        # Write STL export
        writer = Application.getInstance().getMeshFileHandler().getWriter('STLWriter')
        job = WriteFileJob(writer, self._stream, nodes, MeshWriter.OutputMode.TextMode)
        job.finished.connect(self._onExportDone)
        job.start()

        self.setCurrentStep(3)
        return True


    def updateExtruderSettings(self):
        global_stack = Application.getInstance().getGlobalContainerStack()
        if not global_stack:
            self.setLastFeedback("Unexpected CURA state - missing global stack!")
            # self._message_manager.showMessage(MessageType.UNKNOWN, "Unexpected CURA state - missing global stack!")
            return

        model_extruder = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
        for k, v in self._expected_extruder_global_settings.items():
            global_stack.setProperty(k, 'value', v)
        for extruder_stack in global_stack.extruderList:
            if model_extruder == extruder_stack.id:
                for k, v in self._expected_extruder_local_settings.items():
                    extruder_stack.setProperty(k, 'value', v)


    # def updateExtruderSettings(self, msg, action):
    #     if action == 'Update':
    #         global_stack = Application.getInstance().getGlobalContainerStack()
    #         if not global_stack:
    #             self._message_manager.showMessage(MessageType.UNKNOWN, "Unexpected CURA state - missing global stack!")
    #             return
    #
    #         model_extruder = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
    #         for k, v in self._expected_extruder_global_settings.items():
    #             global_stack.setProperty(k, 'value', v)
    #         for extruder_stack in global_stack.extruderList:
    #             if model_extruder == extruder_stack.id:
    #                 for k, v in self._expected_extruder_local_settings.items():
    #                     extruder_stack.setProperty(k, 'value', v)
    #
    #         self._message_manager.hideMessage(MessageType.UPDATE_EXTRUDER_SETTINGS_REQUEST)

    def openSamplesFolder(self, msg, action):
        if action == 'Open samples':
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Choose a model to import",
                os.path.join(PluginRegistry.getInstance().getPluginPath(self.getPluginId()), "resources", "samples"),
                "STL Files (*.stl);;All Files (*)",
                options=QFileDialog.Option.DontUseNativeDialog
            )

            if file_path:
                self._is_importing = True
                job = ReadMeshJob(file_path, add_to_recent_files=False)
                job.finished.connect(self._onSampleImportFinished)
                job.start()

    def _onSampleImportFinished(self, job):
        nodes = job.getResult()

        printableNodes = getPrintableNodes()

        for original_node in nodes:
            # Slightly updated CuraImport code
            if isinstance(original_node, CuraSceneNode):
                node = original_node
            else:
                node = CuraSceneNode()
                node.setMeshData(original_node.getMeshData())
                node.source_mime_type = original_node.source_mime_type

            sliceable_decorator = SliceableObjectDecorator()
            node.addDecorator(sliceable_decorator)

            # If there is no convex hull for the node, start calculating it and continue.
            if not node.getDecorator(ConvexHullDecorator):
                node.addDecorator(ConvexHullDecorator())
            for child in node.getAllChildren():
                if not child.getDecorator(ConvexHullDecorator):
                    child.addDecorator(ConvexHullDecorator())

            target_build_plate = Application.getInstance().getMultiBuildPlateModel().activeBuildPlate

            build_plate_decorator = node.getDecorator(BuildPlateDecorator)
            if build_plate_decorator is None:
                build_plate_decorator = BuildPlateDecorator(target_build_plate)
                node.addDecorator(build_plate_decorator)
            build_plate_decorator.setBuildPlateNumber(target_build_plate)

            node.setSelectable(True)
            node.setName(os.path.basename(job.getFileName()))
            node.setSetting(SceneNodeSettings.AutoDropDown, False)

            Selection.clear()
            Selection.add(node)

            Selection.clear()

            scene = Application.getInstance().getController().getScene()
            scene_root = scene.getRoot()

            node.translate(node.getMeshData().getCenterPosition())

            # TODO is this necessary in my plugin? Check the dependencies when you have time
            # We need to prevent circular dependency, so do some just in time importing.
            from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
            op = AddSceneNodeOperation(node, scene_root)
            op.push()
            Application.getInstance().getController().getScene().sceneChanged.emit(node)

        for printableNode in printableNodes:
            # TODO is this necessary in my plugin? Check the dependencies when you have time
            # We need to prevent circular dependency, so do some just in time importing.
            from UM.Operations.RemoveSceneNodeOperation import RemoveSceneNodeOperation
            op = RemoveSceneNodeOperation(printableNode)
            op.push()

        self.reset()
        self.getHighlightManager().setEnabled(True)
        self._message_manager.showMessage(MessageType.SAMPLE_SETUP)
        self._is_importing = False


    def cancelOptimization(self, action):
        data = {'option': action}

        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}"
            }
            response = requests.post(f"{server_https}/jobs/cancel", data=data, headers=headers)
            if response.status_code == 202:
                Logger.log('d', 'Cancel acknowledged')
                # if action == "KILL":
                #     self.setCurrentStep(2, True)
                # self.setLastFeedback("I delivered the cancel to the server and it was confirmed")
                # self._message_manager.showMessage(MessageType.OPTIMIZATION_CANCELLED_BY_USER,
                #                                   "I delivered the cancel to the server and it was confirmed")
                self._is_importing = False
                self._is_import_success = False
            elif response.status_code in [404, 409]:
                # TODO COULD NOT BE CANCELLED - NOT RUNNING?
                text = response.json().get('detail', 'Tried to cancel the optimization but something went wrong. Please try again')
                self.setLastFeedback(text)
                # self._message_manager.showMessage(MessageType.OPTIMIZATION_NOT_RUNNING, text)
                # self._message_manager.updateCurrentMessageText('Could not cancel optimization')
            elif response.status_code == 429:
                self.setLastFeedback("Too many requests detected. Please wait a little before trying again")
                # self._message_manager.showMessage(MessageType.TOO_MANY_REQUESTS)
            else:
                # TODO COULD NOT BE CANCELLED - ERROR
                # text = response.json().get('detail', '')
                self.setLastFeedback("Cancel didn't go through. Error while trying to cancel optimization")
                # self._message_manager.showMessage(
                #     MessageType.UNKNOWN,
                #     f"Cancel didn't go through. Error while trying to cancel optimization")
                # self._message_manager.updateCurrentMessageText(f'Error while trying to cancel optimization: status code {response.status_code}')
        except Exception as e:
            Logger.log('e', f'Exception occurred while trying to cancel optimization.')
            self.setLastFeedback("Cancel didn't go through. Error while trying to cancel optimization")
            # self._message_manager.showMessage(
            #     MessageType.UNKNOWN,
            #     f'Error while trying to cancel optimization: error type {e.__class__.__name__}')
            # self._message_manager.updateCurrentMessageText(
            #     f'Error while trying to cancel optimization: error type {e.__class__.__name__}')

    def _onExportDone(self, job):
        self._stream.close()
        Logger.log('d', f"STL exported to: {self._temp_path}")

        temp_file = ""
        temp_tar_file = ""
        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}"
            }

            anchor_faces = [value.facesFlat for key, value in self._anchors.items()]
            force_data = [
                {
                    'faces': value.facesFlat,
                    'direction': [value.direction.getData()[0], -value.direction.getData()[2], value.direction.getData()[1]],
                    'magnitude': exportForceInN(value.magnitude, value.unit),
                    'push': value.push
                }
                for key, value in self._forces.items()]
            data = {"anchors": json.dumps(anchor_faces),
                    "forces": json.dumps(force_data),
                    "optimization_strategy": json.dumps(self._optimization_strategy),
                    "optimization_safety_ratio": json.dumps(self._optimization_safety_ratio),
                    "infill_sparse_density": json.dumps(self._user_infill),
                    "auto_lower_safety_ratio": json.dumps(self._optimization_auto_lower_safety_ratio),
                    "source_node_position": json.dumps(self._source_node.getPosition().getData().tolist())
                    }

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            temp_file.close()

            with open(temp_file.name, "w") as f:
                json.dump(data, f)

            temp_tar_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz")
            with tarfile.open(temp_tar_file.name, "w:gz") as tar:
                tar.add(self._temp_path, arcname='model.stl')
                tar.add(temp_file.name, arcname='opt_args.json')

            data = {
                "filename": temp_tar_file.name,
            }

            response = requests.post(f"{server_https}/upload/get-signed-url", data=data, headers=headers)
            response.raise_for_status()

            url = response.json().get('uploadURL')

            with open(temp_tar_file.name, "rb") as f:
                upload_headers = {"Content-Type": "application/gzip"}
                response = requests.put(url, data=f, headers=upload_headers)
                response.raise_for_status()

            data = {"gcs_uri": ""}
            response = requests.post(f"{server_https}/jobs", data=data, headers=headers)
            if response.status_code == 202:
                self.setLastStatusFeedback('This usually takes about 30\u00A0s')
                # Application.getInstance().getBackend().forceSlice()
            elif response.status_code == 409:
                self.setLastFeedback("Your optimization is still processing, please wait")
                # self._message_manager.showMessage(MessageType.OPTIMIZATION_STILL_RUNNING)
            elif response.status_code == 401:
                self._message_manager.showMessage(
                    MessageType.LOG_IN_ERROR, response.json().get("detail", "Unknown error"))
            elif response.status_code == 403:
                # self.setLastFeedback("The optimization exceeded time limit and was stopped automatically")
                # self._message_manager.showMessage(MessageType.LIMIT_EXCEEDED)
                self.setCurrentStep(2, True)
                detail_code = response.json().get("detail", {"code": "UNKNOWN", "message": "Unknown error"}).get("code", None) \
                    if isinstance(response.json().get("detail"), dict) else None
                if detail_code == "AUTO_APPROVAL_FORM":
                    trial_form_response = requests.get(f"{server_https}/trial_form/generate_url", headers=headers)
                    if trial_form_response.status_code != 200:
                        self._message_manager.showMessage(
                            MessageType.UNKNOWN, response.json().get("detail", "Unknown error"))
                        return

                    trial_form_url = trial_form_response.json().get("url", "")
                    if not trial_form_url:
                        self._message_manager.showMessage(
                            MessageType.UNKNOWN, response.json().get("detail", "No URL to trial form received"))
                        return

                    message = (
                        f'<b>Activate your free trial</b><br>'
                        f'To start using Slicedog, please complete a quick trial setup.<br>'
                        f'It only takes 30 seconds and no credit card is needed.<br>'
                        f'Click <a href="{trial_form_url}">here</a> to open the trial form.'
                    )

                    self._emit("popup_requested", "trialFormUrl", message)
                elif detail_code == "ADMIN_APPROVAL_MISSING":
                    self._emit("popup_requested", "adminApprovalMissing")
                elif detail_code == "MONTHLY_LIMIT_EXCEEDED":
                    self._emit("popup_requested", "executionTimeLimitExceeded")
                else:
                    self._message_manager.showMessage(
                        MessageType.UNKNOWN, response.json().get("detail", "Unknown error"))
                # self._message_manager.showMessage(
                #     MessageType.LIMIT_EXCEEDED, response.json().get("detail", "Ran out of time, execution time exceeded"))
            elif response.status_code == 429:
                self.setLastFeedback("Too many requests detected. Please wait a little before trying again")
                # self._message_manager.showMessage(MessageType.TOO_MANY_REQUESTS)
            else:
                Logger.log('e', f'Optimization did not start, status code: {response.status_code}')
                self.setLastFeedback(f"Optimization did not start, status code: {response.status_code}")
                # self._message_manager.showMessage(
                #     MessageType.UNKNOWN, f'Optimization did not start, status code: {response.status_code}\n'
                #     f'{response.json().get("detail", "Unknown error")}')
        except requests.ConnectionError as e:
            Logger.log('e', f'ConnectionError during upload: {e}')
            self._emit("popup_requested", "noConnection")
            # self._message_manager.showMessage(MessageType.NO_CONNECTION)
        except Exception as e:
            Logger.log('e', f"Exception during upload: {e}")
            self.setLastFeedback(f'{e.__class__.__name__} during upload')
            # self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(MessageType.UNKNOWN, f'{e.__class__.__name__} during upload')
            # self._message_manager.updateCurrentMessageText(f'{e.__class__.__name__} during upload')
        finally:
            try:
                os.remove(self._temp_path)
                Logger.log('d', f"Deleted temporary file {self._temp_path}")
                os.remove(temp_file.name)
                Logger.log('d', f"Deleted temporary file {temp_file.name}")
            except Exception as e:
                Logger.log('e', f"Could not delete temporary files due to: {e}")

    def _onImportDonePreSlice(self, job):
        last_print_information = Application.getInstance().getPrintInformation()
        last_print_uuid = last_print_information.slice_uuid
        last_print_weight = sum(last_print_information.materialWeights)
        last_print_seconds = last_print_information.currentPrintTime.__int__()

        # let's assume that the only node on print is our source node (there should be exactly one present)
        if self._source_node is None:
            self._source_node = getPrintableNodes()[0]

        if 'safe_static_infill' in self._import_metadata:
            global_stack = Application.getInstance().getGlobalContainerStack()
            if self._source_node is not None:
                model_extruder = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
                for extruder_stack in global_stack.extruderList:
                    if model_extruder == extruder_stack.id:
                        extruder_stack.setProperty('infill_sparse_density', 'value', self._import_metadata['safe_static_infill'])
            else:
                Logger.log('e', 'Source node is none when trying to process import metadata!')
                self._should_use_slice = False
        else:
            self._should_use_slice = False

        if self._should_use_slice:
            self.setLastFeedback("Optimization successful, now I'm just waiting for slicing to finish, so I can show "
                                 "you how much material we saved!")
            self.setLastStatusFeedback("", self._last_feedback_status)
            QtCore.QTimer.singleShot(1000, self._startSlice)

            self._check_slicing_start_time = time.time()
            # TODO this isn't clean either..
            try:
                self._check_slicing_timer.timeout.disconnect()
            except TypeError:
                Logger.log('d', 'Nothing to disconnect')
            self._check_slicing_timer.timeout.connect(
                lambda: self._checkPreSliceDone(last_print_uuid, last_print_weight, last_print_seconds, job))
            self._check_slicing_timer.start()

    def _onImportDone(self, job):
        last_print_information = Application.getInstance().getPrintInformation()
        last_print_uuid = last_print_information.slice_uuid
        last_print_weight = sum(last_print_information.materialWeights)
        last_print_seconds = last_print_information.currentPrintTime.__int__()

        nodes = job.getResult()
        self._processImportMetadata()

        for original_node in nodes:
            # Slightly updated CuraImport code - main difference is the transformation and mesh settings
            if isinstance(original_node, CuraSceneNode):
                node = original_node
            else:
                node = CuraSceneNode()
                node.setMeshData(original_node.getMeshData())
                node.source_mime_type = original_node.source_mime_type

            sliceable_decorator = SliceableObjectDecorator()
            node.addDecorator(sliceable_decorator)

            # If there is no convex hull for the node, start calculating it and continue.
            if not node.getDecorator(ConvexHullDecorator):
                node.addDecorator(ConvexHullDecorator())
            for child in node.getAllChildren():
                if not child.getDecorator(ConvexHullDecorator):
                    child.addDecorator(ConvexHullDecorator())

            target_build_plate = Application.getInstance().getMultiBuildPlateModel().activeBuildPlate

            build_plate_decorator = node.getDecorator(BuildPlateDecorator)
            if build_plate_decorator is None:
                build_plate_decorator = BuildPlateDecorator(target_build_plate)
                node.addDecorator(build_plate_decorator)
            build_plate_decorator.setBuildPlateNumber(target_build_plate)

            node.setSelectable(True)
            node.setName(os.path.basename(job.getFileName()))
            node.setSetting(SceneNodeSettings.AutoDropDown, False)

            Selection.clear()
            Selection.add(node)

            controller = Application.getInstance().getController()
            controller.setActiveTool("PerObjectSettingsTool")
            controller.getActiveTool().setMeshType('infill_mesh')

            Selection.clear()

            stack = node.callDecoration("getStack")
            if not stack:
                node.addDecorator(SettingOverrideDecorator())
                stack = node.callDecoration("getStack")
            settings = stack.getTop()
            # definition = stack.getSettingDefinition('infill_mesh')
            # new_instance = SettingInstance(definition, settings)
            # new_instance.setProperty('value', True)
            # new_instance.resetState()
            # settings.addInstance(new_instance)

            definition = stack.getSettingDefinition('infill_sparse_density')
            new_instance = SettingInstance(definition, settings)
            new_instance.setProperty('value', self._import_metadata.get('infill_high_density', 80))
            new_instance.resetState()
            settings.addInstance(new_instance)

            extruder_stack_id = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
            node.getDecorator(SettingOverrideDecorator).setActiveExtruder(extruder_stack_id)

            scene = Application.getInstance().getController().getScene()
            scene_root = scene.getRoot()

            node.translate(node.getMeshData().getCenterPosition())
            if self._result_offset is not None:
                node.translate(self._source_node.getPosition() - self._result_offset)
            # node.translate(node.getMeshData().getCenterPosition() - self._source_node.getMeshData().getCenterPosition().set(y=0))

            # TODO is this necessary in my plugin? Check the dependencies when you have time
            # We need to prevent circular dependency, so do some just in time importing.
            from UM.Operations.AddSceneNodeOperation import AddSceneNodeOperation
            op = AddSceneNodeOperation(node, scene_root)
            op.push()
            Application.getInstance().getController().getScene().sceneChanged.emit(node)
            self.getHighlightManager().setEnabled(False)

        if last_print_uuid is None or last_print_weight == 0 or last_print_seconds == 0 or not self._should_use_slice:
            self._createImportResultMessage()
            self._is_importing = False
            self._is_import_success = True
        else:
            # TODO figure out the correct way to connect start slice - it must be called only after the new node is
            #  added as there is a delay between push and apply. But right now this is implemented as cheap as possible
            self.setLastFeedback("Optimization successful, now I'm just waiting for slicing to finish, so I can show "
                                 "you how much material we saved!")
            self.setLastStatusFeedback("", self._last_feedback_status)
            # self._message_manager.showMessage(MessageType.OPTIMIZATION_SUCCESS,
            #                                   "Optimization successful, now I'm just waiting for slicing to finish, so I can show you how much material we saved!")
            QtCore.QTimer.singleShot(1000, self._startSlice)
            self._check_slicing_start_time = time.time()
            # TODO this isn't clean either..
            try:
                self._check_slicing_timer.timeout.disconnect()
            except TypeError:
                Logger.log('d', 'Nothing to disconnect')
            self._check_slicing_timer.timeout.connect(
                lambda: self._checkSliceDone(last_print_uuid, last_print_weight, last_print_seconds))
            self._check_slicing_timer.start()

    def _startSlice(self):
        Application.getInstance().getBackend().forceSlice()

    def _checkPreSliceDone(self, last_print_uuid, last_print_weight, last_print_seconds, job):
        print_info = Application.getInstance().getPrintInformation()
        Logger.log('d', f'Last   : UUID: {last_print_uuid}, weights: {last_print_weight}, seconds: {last_print_seconds}')
        Logger.log('d', f'Current: UUID: {print_info.slice_uuid}, weights: {sum(print_info.materialWeights)}, seconds: {print_info.currentPrintTime.__int__()}')
        if print_info.slice_uuid != last_print_uuid and sum(print_info.materialWeights) != 0 and print_info.currentPrintTime.__int__() != 0:
            self._check_slicing_timer.stop()
            self._onImportDone(job)

        if time.time() - self._check_slicing_start_time > 30:
            Logger.log('w', 'Pre-Slicing timed out')
            self._check_slicing_timer.stop()
            self._should_use_slice = False
            self._onImportDone(job)


    def _checkSliceDone(self, last_print_uuid, last_print_weight, last_print_seconds):
        print_info = Application.getInstance().getPrintInformation()
        Logger.log('d', f'Last   : UUID: {last_print_uuid}, weights: {last_print_weight}, seconds: {last_print_seconds}')
        Logger.log('d', f'Current: UUID: {print_info.slice_uuid}, weights: {sum(print_info.materialWeights)}, seconds: {print_info.currentPrintTime.__int__()}')
        if print_info.slice_uuid != last_print_uuid and sum(print_info.materialWeights) != 0 and print_info.currentPrintTime.__int__() != 0:
            self._check_slicing_timer.stop()
            self._createImportResultMessage((1 - (sum(print_info.materialWeights) / last_print_weight)) * 100,
                                            last_print_seconds - print_info.currentPrintTime.__int__())
            self._is_importing = False
            self._is_import_success = True
            Application.getInstance().activityChanged.emit()

        if time.time() - self._check_slicing_start_time > 30:
            Logger.log('w', 'Slicing timed out')
            self._check_slicing_timer.stop()
            self._createImportResultMessage()
            self._is_importing = False
            self._is_import_success = True
            Application.getInstance().activityChanged.emit()

    def _createImportResultMessage(self, saved_mass_ratio=None, saved_print_time=None):
        message_text = ''
        # message = Message(title='Optimization result', text='', message_type=Message.MessageType.POSITIVE)
        if ('user_specified_infill' in self._import_metadata and 'safe_static_infill' in self._import_metadata and
                'optimization_safety_ratio' in self._import_metadata):
            user_specified_infill = self._import_metadata['user_specified_infill']
            static_save_infill = self._import_metadata['safe_static_infill']
            optimization_safety_ratio = self._import_metadata['optimization_safety_ratio']
            auto_lowered_safety_ratio = self._import_metadata.get('auto_lowered_safety_ratio', None)
            if saved_mass_ratio is None:
                saved_mass_ratio = self._import_metadata.get('saved_mass_ratio', 0)
            if user_specified_infill < static_save_infill:
                message_text += f"\u2022 Material saved: {saved_mass_ratio:.2f}%\n"
                if saved_print_time is not None:
                    message_text += f"\u2022 Printing time saved: {(saved_print_time / 3600):.1f}\u00A0hours\n"
                if auto_lowered_safety_ratio is not None:
                    message_text += (f"\u2022 Safety factor auto-lowered to {auto_lowered_safety_ratio:.1f} "
                                     f"({safetyFactorExplanation(optimization_safety_ratio)})\n")
                    message_text += "\n"
                    message_text += (f"It was impossible to reach desired safety factor {optimization_safety_ratio:.1f}"
                                     f" ({safetyFactorExplanation(optimization_safety_ratio)}) on the strongest print "
                                     f"settings so it was auto-lowered. Original {user_specified_infill}% infill wasn't "
                                     f"safe. Minimum infill for required safety factor would be {static_save_infill}%.")
                else:
                    message_text += (f"\u2022 Required safety factor {optimization_safety_ratio:.1f} "
                                     f"({safetyFactorExplanation(optimization_safety_ratio)}) met\n")
                    message_text += "\n"
                    message_text += (f"Original {user_specified_infill}% infill wasn't safe. Minimum infill for required "
                                     f"safety factor would be {static_save_infill}%.")
            else:
                if saved_mass_ratio >= 0:
                    message_text += f"\u2022 Material saved: {saved_mass_ratio:.2f}%\n"
                    if saved_print_time is not None:
                        message_text += f"\u2022 Printing time saved: {(saved_print_time / 3600):.1f}\u00A0hours\n"
                    if auto_lowered_safety_ratio is not None:
                        message_text += (f"\u2022 Safety factor auto-lowered to {auto_lowered_safety_ratio:.1f} "
                                         f"({safetyFactorExplanation(optimization_safety_ratio)})\n")
                        message_text += "\n"
                        message_text += (f"It was impossible to reach desired safety factor {optimization_safety_ratio:.1f}"
                                         f" ({safetyFactorExplanation(optimization_safety_ratio)}) on the strongest print "
                                         f"settings so it was auto-lowered. Original {user_specified_infill}% infill was "
                                         f"safe but we've manager the savings above.")
                    else:
                        message_text += (f"\u2022 Required safety factor {optimization_safety_ratio:.1f} "
                                         f"({safetyFactorExplanation(optimization_safety_ratio)}) met\n")
                        message_text += "\n"
                        message_text += (f"Original {user_specified_infill}% was safe but we've manager the savings "
                                         f"above. Woof!")
                else:
                        message_text += (f"\u2022 Optimization enabled reaching safety factor "
                                         f"{optimization_safety_ratio:.1f} "
                                         f"({safetyFactorExplanation(optimization_safety_ratio)})\n")
                        message_text += f"\u2022 Material usage increased by: {-saved_mass_ratio:.2f}%\n"
                        if saved_print_time is not None:
                            message_text += f"\u2022 Printing time increased: {(-saved_print_time / 60):.0f}\u00A0minutes\n"
                        message_text += "\n"
                        message_text += (f"Original {user_specified_infill}% was safe but safety factor was optimized "
                                         f"to required value. Woof!")

                # message_text += f"\u2022 Material saved: {saved_mass_ratio:.2f}%\n"
                # message_text += f"\u2022 Printing time saved: TODO hours\n"
                # message_text += f"\u2022 Required safety factor {optimization_safety_ratio:.1f} (TODO) met\n"
                # message_text += "\n"
                #
                # message_text += (f'Your original {user_specified_infill}% infill is already safe. But optimization '
                #                  f'fetched extra strength, your part now has {optimization_safety_ratio:.1f} safety '
                #                  f'factor which makes it {optimization_safety_ratio:.1f}x more safe')

        # auto_lowered_safety_ratio = self._import_metadata.get('auto_lowered_safety_ratio', None)
        # if auto_lowered_safety_ratio is not None:
        #     message_text += f"I had to lower the safety factor to {auto_lowered_safety_ratio:.1f} so I could fetch you material back\n"
        #
        # if saved_mass_ratio is None:
        #     saved_mass_ratio = self._import_metadata.get('saved_mass_ratio', 0)

        # if saved_mass_ratio >= 0:
        #     message_text += f'{message.getText()}\nSaved mass: {saved_mass_ratio:.2f}%'
        # else:
        #     message_text += f'{message.getText()}\nUsed {-saved_mass_ratio:.2f}% more material'

        # if 'has_high_density' in self._import_metadata:
        #     has_high_density = self._import_metadata['has_high_density']
        #     if not has_high_density:
        #         message_text += f'{message.getText()}\nOptimization removed all HIGH_DENSITY elements'

        self._message_manager.showMessage(MessageType.OPTIMIZATION_SUCCESS, message_text)

    def _processImportMetadata(self):
        if 'infill_sparse_density' in self._import_metadata:
            global_stack = Application.getInstance().getGlobalContainerStack()
            if self._source_node is not None:
                model_extruder = self._source_node.getDecorator(SettingOverrideDecorator).getActiveExtruder()
                for extruder_stack in global_stack.extruderList:
                    if model_extruder == extruder_stack.id:
                        extruder_stack.setProperty('infill_sparse_density', 'value', self._import_metadata['infill_sparse_density'])
            else:
                Logger.log('e', 'Source node is none when trying to process import metadata!')
                
        self._result_offset = self._import_metadata.get('source_node_position', None)
        if self._result_offset is not None:
            self._result_offset = json.loads(self._result_offset)
            self._result_offset = Vector(data=self._result_offset)
        # self._message_manager.updateCurrentMessageText(message_text)

    def onFeedbackUpdated(self, message, message_type, status, iteration_info):
        if message:
            if iteration_info:
                self.setLastIterationFeedback(message, iteration_info)
                if status:
                    self.setLastStatusFeedback(None, status)
            elif status:
                self.setLastStatusFeedback(message, status)
            else:
                self.setLastFeedback(message)
                # self.setLastFeedback(message, status, iteration_info)
        # self._message_manager.showMessage(message_type, message)
        # if message:
        #     self._message_manager.updateCurrentMessageText(message)

    def importLastResult(self):
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }
        url_response = requests.get(f'{server_https}/jobs/last', headers=headers)
        if url_response.status_code == 200:
            Logger.log('d', f'Got signed URL for last job')
            url = url_response.json().get('downloadURL')
        elif url_response.status_code == 401:
            self._emit("popup_requested", "login")
            # self._message_manager.showMessage(
            #     MessageType.LOG_IN_ERROR, url_response.json().get("detail", "Unknown error"))
            return
        elif url_response.status_code == 404:
            message = url_response.json().get("detail", "Execution time exceeded!")
            Logger.log('e', f'Last job could not be found; {message}')
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(MessageType.UNKNOWN, message)
            return
        else:
            Logger.log('e', f'Could not get last result; status code {url_response.status_code}')
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(MessageType.UNKNOWN, f'{url_response.status_code}')
            return

        response = requests.get(url)
        if response.status_code == 200:
            tar_bytes = response.content
        else:
            Logger.log('e', f'Could not download result from signed URL; status code {response.status_code}')
            return

        if tar_bytes and tar_bytes is not None:
            extract_to = '/tmp'
            try:
                with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:gz') as tar:
                    tar.extractall(path=extract_to)
                    model_filepath = os.path.join(extract_to, 'results', 'HIGH_DENSITY.stl')
                    metadata_filepath = os.path.join(extract_to, 'results', 'metadata.json')
            except Exception as e:
                Logger.log('e', f'{e.__class__.__name__}: {e}')

        try:
            self._is_importing = True
            self._is_import_success = False
            self._import_metadata = {}
            with open(metadata_filepath, "r", encoding="utf-8") as mf:
                self._import_metadata = json.load(mf)

            self._source_node = Selection.getSelectedObject(0)
            job = ReadMeshJob(model_filepath, add_to_recent_files=False)
            job.finished.connect(self._onImportDonePreSlice)
            job.start()
        except Exception as e:
            self._is_importing = False
            self._is_import_success = False
            Logger.log('e', f'Exception occurred while trying to get results: error type {e.__class__.__name__}: {e}')
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(
            #     MessageType.UNKNOWN,
            #     f'Exception occurred while trying to get results: error type {e.__class__.__name__}')

    def onOptimizationFinished(self, message, message_type, status, result_uri, new_user):
        model_filepath = ""
        metadata_filepath = ""
        tar_bytes = ""

        if result_uri and result_uri is not None:
            response = requests.get(result_uri)
            if response.status_code == 200:
                tar_bytes = response.content
            else:
                Logger.log('e', f'Could not download result from signed URL; status code {response.status_code}')

        if tar_bytes and tar_bytes is not None:
            extract_to = '/tmp'
            try:
                with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode='r:gz') as tar:
                    tar.extractall(path=extract_to)
                    model_filepath = os.path.join(extract_to, 'results', 'HIGH_DENSITY.stl')
                    metadata_filepath = os.path.join(extract_to, 'results', 'metadata.json')
            except Exception as e:
                Logger.log('e', f'{e.__class__.__name__}: {e}')

        if (message_type == MessageType.OPTIMIZATION_SUCCESS or
                message_type == MessageType.OPTIMIZATION_CANCELLED_BY_USER and model_filepath):
            self.setLastStatusFeedback("", status)
            self.setLastFeedback(message)
            try:
                self._is_importing = True
                self._is_import_success = False
                self._import_metadata = {}
                with open(metadata_filepath, "r", encoding="utf-8") as mf:
                    self._import_metadata = json.load(mf)

                job = ReadMeshJob(model_filepath, add_to_recent_files=False)
                job.finished.connect(self._onImportDonePreSlice)
                job.start()
            except Exception as e:
                self._is_importing = False
                self._is_import_success = False
                Logger.log('e', f'Exception occurred while trying to get results: error type {e.__class__.__name__}: {e}')
                self._emit("popup_requested", "unhandled")
                # self._message_manager.showMessage(
                #     MessageType.UNKNOWN,
                #     f'Exception occurred while trying to get results: error type {e.__class__.__name__}')
                # self._message_manager.updateCurrentMessageText(
                #     f'Exception occurred while trying to get results: error type {e.__class__.__name__}')
        elif message_type == MessageType.OPTIMIZATION_CANCELLED_BY_USER:
            # self.setLastFeedback('Cancelled by user, no result returned')
            self.setCurrentStep(2)
            self.setLastFeedback(message)
            # self.setLastFeedback(message, status)
            # self._message_manager.showMessage(message_type)
        else:
            self.setCurrentStep(2)
            # self.setLastFeedback(message)
            # self.setLastFeedback(message, status)
            self._message_manager.showMessage(MessageType.OPTIMIZATION_FAIL, message)
            if new_user:
                self._message_manager.showMessage(
                    message_type=MessageType.OPEN_SAMPLES,
                    text="You have 1 more try. The sample model works best for the first run. Click on Open samples button",
                    title="Optimization didn't complete."
                )

    def isOptimizationRunning(self):
        # assume that optimization is not running if we can't get status
        if not self.isLoggedIn():
            return False

        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }
        try:
            response = requests.post(f"{server_https}/jobs/status", headers=headers)
            if response.status_code == 200:
                if response.json().get('detail', '') in ["ACCEPTED", "ACCEPTED_BY_JOB", "RUNNING", "RUNNING_ANALYSIS",
                                                         "RUNNING_OPTIMIZATION", "RUNNING_OPTIMIZATION_PAST_3_ITERS"]:
                    return True
                else:
                    return False
            elif response.status_code == 429:
                # assume that it is running if TOO_MANY_REQUESTS - otherwise spam clicking will allow to change the state
                self.setLastFeedback("Too many requests detected. Please wait a little before trying again")
                # self._message_manager.showMessage(MessageType.TOO_MANY_REQUESTS)
                return True
            else:
                # TODO: determine based on status code?
                return False
        except requests.ConnectionError:
            Logger.log('e', f'Connection error while trying to determine if optimization is running')
            return False
        except Exception as e:
            Logger.log('e', f'Exception occurred while trying to get results: error type {e.__class__.__name__}: {e}')
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(
            #     MessageType.UNKNOWN,
            #     f'Exception occurred while trying to get results: error type {e.__class__.__name__}')
            return False

    def getCurrentStep(self):
        return self._current_step

    def isStepDefined(self, step):
        match step:
            case 0:
                return len(self.getForcesAsList()) > 0 and self.areAllForcesConfirmed()
            case 1:
                return len(self.getAnchorsAsList()) > 0 and self.areAllAnchorsConfirmed()
            case 2:
                # radio buttons, slider value and switch
                return True
            case 3:
                # this acts as feedback, no definition needed
                return True
            case _:
                Logger.log('e', f'Unknown step ID {self._current_step}')
                return False

    def getStepsConfirmedFlags(self):
        return self._steps_confirmed_flags

    def resetStepsConfirmedFlags(self):
        self._steps_confirmed_flags = [False] * 4

    def confirmCurrentStep(self):
        if self._current_step < 0 or self._current_step > len(self._steps_confirmed_flags) - 1:
            Logger.log('e', "Only steps 0-3 are possible")
            return False

        if not self.isStepDefined(self._current_step):
            self._emit("popup_requested", "stepNotDefined")
            # self._message_manager.showMessage(MessageType.UNKNOWN, f"Step definition not finished")
            return False

        self._steps_confirmed_flags[self._current_step] = True
        self._emit("steps_confirmed_flags", self._steps_confirmed_flags)
        Logger.log('i', f'Setting current step {self._current_step} as confirmed.')
        return True

    def setCurrentStep(self, step, force=False):
        if self._current_step == step:
            return

        if step < 0 or step > len(self._steps_confirmed_flags) - 1:
            Logger.log('e', "Only steps 0-3 are possible")
            return

        previous_steps_flags = self._steps_confirmed_flags[:step]
        if not all(previous_steps_flags):
            self._emit("popup_requested", "stepNotDefined")
            # self._message_manager.showMessage(
            #     MessageType.PREVIOUS_STEP_NOT_CONFIRMED,
            #     f"Could not switch to step {step + 1} as there is a previous step that is not confirmed")
            return

        # TODO: maybe it will be necessary to replace isOptimizationRunning
        if self._current_step == 3 and self.isOptimizationRunning() and not force:
            if self.isOptimizationRunning():
                self.setLastFeedback("Your optimization is still processing, please wait")
                # self._message_manager.showMessage(MessageType.OPTIMIZATION_STILL_RUNNING)
                return
            else:
                self.setLastIterationFeedback("", "")

        self._current_step = step
        self._emit("current_step", self._current_step)
        self._steps_confirmed_flags[self._current_step] = False
        self.setLastFeedback("")
        self.setLastStatusFeedback("", "")
        # self.setLastFeedback("", self._last_feedback_status)
        Logger.log('i', f'Step {step} is set as the new current step.')

    def isImporting(self):
        return self._is_importing

    def isImportSuccess(self):
        return self._is_import_success

    def resetImportTrack(self):
        self._is_import_success = False

    def onChanged(self, name: str, cb):
        self._callbacks[name].append(cb)

    def _emit(self, name, *args):
        for cb in self._callbacks[name]:
            cb(*args)

    def getCurrentForceAsDict(self):
        return self._current_force.to_dict()

    def getCurrentForce(self):
        return self._current_force

    def confirmCurrentForce(self, magnitude, unit):
        if self._current_force.magnitude < 0:
            self._current_force.magnitude = magnitude

        if self._current_force.unit is None or not self._current_force.unit:
            self._current_force.unit = unit

        if not self.getCurrentForceFacesFlat():
            self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "You have to select at least one face")
            return False

        if self._current_force.magnitude < 0:
            self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "You need to specify force magnitude")
            return False

        if self._current_force.unit == '%' and self._current_force.magnitude > 100:
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(MessageType.UNKNOWN, "Unable to create new force, please contact support")
            return False

        self.setCurrentForceConfirmed(True)

        Selection.clearFace()
        self.resetCurrentForce()
        self.setRotationActive(False)

        return True

    def confirmCurrentAnchor(self):
        if not self.getCurrentForceFacesFlat():
            self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "You have to select at least one face")
            return False

        self.setCurrentForceConfirmed(True)

        Selection.clearFace()
        self.resetCurrentForce()

        return True

    def resetCurrentForce(self):
        self.setCurrentForce(CurrentForce())
        self.setRotationActive(False)
        self._highlights_manager.drawSavedObjectsAndCurrentSelection(current_selection=self.getCurrentForce())

    def setCurrentForce(self, value):
        if isinstance(value, dict):
            value = CurrentForce(**value)
        self._current_force = value
        self._emit("current_force", self._current_force)

    def getCurrentForceFaces(self):
        return self._current_force.faces

    def getCurrentForceFacesFlat(self):
        return self._current_force.facesFlat

    def setCurrentForceFaces(self, faces):
        self._current_force.faces = faces
        self._emit("current_force", self._current_force)

    def getCurrentForcePush(self):
        return self._current_force.push

    def setCurrentForcePush(self, push):
        self._current_force.push = push
        self._emit("current_force", self._current_force)

    def getCurrentForceMagnitude(self):
        return self._current_force.magnitude

    def setCurrentForceMagnitude(self, magnitude):
        self._current_force.magnitude = magnitude
        self._emit("current_force", self._current_force)

    def getCurrentForceUnit(self):
        return self._current_force.unit

    def setCurrentForceUnit(self, unit):
        self._current_force.unit = unit
        self._emit("current_force", self._current_force)

    def getCurrentForceCenter(self):
        return self._current_force.center

    def setCurrentForceCenter(self, center):
        if isinstance(center, list):
            center = Vector(data=center)

        self._current_force.center = center
        self._emit("current_force", self._current_force)

    def getCurrentForceDirection(self):
        return self._current_force.direction

    def setCurrentForceDirection(self, direction):
        if isinstance(direction, list):
            direction = Vector(data=direction)
        direction = direction.normalized()
        self._current_force.direction = direction
        self._emit("current_force", self._current_force)

    def getCurrentForceId(self):
        return self._current_force.id

    def setCurrentForceId(self, o):
        self._current_force.id = o
        self._emit("current_force", self._current_force)

    def getCurrentForceConfirmed(self):
        return self._current_force.confirmed

    def setCurrentForceConfirmed(self, value):
        self._current_force.confirmed = value
        if value:
            if self._current_force.id.startswith('anchor'):
                self.updateAnchors(self.getCurrentForce())
            else:
                self.updateForces(self.getCurrentForce())
        self._emit("current_force", self._current_force)

    def isCurrentForcePrecise(self):
        return self.getCurrentForceUnit() == 'N'

    def getSurfaceSelection(self):
        return self._surface_selection

    def setSurfaceSelection(self, o):
        if self._surface_selection != o:
            self._surface_selection = o
            self._emit("surface_selection", self._surface_selection)

    def getObjects(self):
        return self._objects

    def getObjectsAsList(self):
        object_list = [asdict(v) for k, v in self._objects.items()]
        return object_list

    def getAnchors(self):
        return self._anchors

    def getAnchorsAsList(self):
        anchors_list = [{'id': v.id, 'faces': v.facesFlat, 'confirmed': v.confirmed} for k, v in self._anchors.items()]
        return anchors_list

    def setAnchors(self, anchors):
        if self._anchors != anchors:
            self._anchors = anchors
            self._objects = (self._anchors | self._forces)
            self._emit("anchors", self._anchors)
            self._emit("objects", self._objects)

    def removeCurrentAnchor(self):
        if self._current_force is not None:
            self.removeAnchor(self._current_force.id)
        else:
            Logger.log('e', f'No current anchor available')

    def removeAnchor(self, anchor_id):
        if anchor_id in self._anchors:
            new_anchors = {}
            for k, v in self.getAnchors().items():
                if k != self.getCurrentForceId():
                    v.id = f'anchor_{len(new_anchors)}'
                    new_anchors[v.id] = v
            self.setAnchors(new_anchors)
            self.resetCurrentForce()
            Logger.log('i', f'Deleted anchor id={anchor_id}')
        else:
            Logger.log('e', f'Could not delete anchor: no anchor with id={anchor_id}')

    def selectAnchor(self, anchor_id):
        if anchor_id in self._anchors:
            if not Selection.hasSelection():
                Selection.add(getPrintableNodes()[0])
            self._current_force = copy.deepcopy(self._anchors[anchor_id])
            self._highlights_manager.drawSavedObjectsAndCurrentSelection(
                current_selection=self.getCurrentForce()
            )
            self._emit("current_force", self._current_force)
            Logger.log('d', f'Current anchor id={anchor_id}')
        else:
            Logger.log('e', f'No anchor with id={anchor_id}')

    def areAllAnchorsConfirmed(self):
        return all(f.confirmed for f in self._anchors.values())

    def getForces(self):
        return self._forces

    def updateForces(self, value):
        if isinstance(value, dict):
            value = CurrentForce(**value)
        if value.id not in self._forces:
            value.id = f'force_{len(self._forces)}'
            self.setCurrentForceId(value.id)
        self._forces[value.id] = copy.deepcopy(value)
        self._objects = (self._anchors | self._forces)
        self._emit("forces", self._forces)
        self._emit("objects", self._objects)

    def updateAnchors(self, value):
        if isinstance(value, dict):
            value = CurrentForce(**value)
        if value.id not in self._anchors:
            value.id = f'anchor_{len(self._anchors)}'
            self.setCurrentForceId(value.id)
        self._anchors[value.id] = copy.deepcopy(value)
        self._objects = (self._anchors | self._forces)
        self._emit("anchors", self._anchors)
        self._emit("objects", self._objects)

    def removeCurrentForce(self):
        if self._current_force is not None:
            self.removeForce(self._current_force.id)
        else:
            Logger.log('e', f'No current force available')

    def removeForce(self, force_id):
        if force_id in self.getForces():
            new_forces = {}
            for k, v in self.getForces().items():
                if k != self.getCurrentForceId():
                    v.id = f'force_{len(new_forces)}'
                    new_forces[v.id] = v
            self.setForces(new_forces)
            self.resetCurrentForce()
            Logger.log('i', f'Deleted force id={force_id}')
        else:
            Logger.log('e', f'Could not delete force: no force with id={force_id}')

    def selectForce(self, force_id):
        if force_id in self._forces:
            if not Selection.hasSelection():
                Selection.add(getPrintableNodes()[0])
            self._current_force = copy.deepcopy(self._forces[force_id])
            self._highlights_manager.drawSavedObjectsAndCurrentSelection(
                current_selection=self.getCurrentForce()
            )
            self._emit("current_force", self._current_force)
            Logger.log('d', f'Current force id={force_id}')
        else:
            Logger.log('e', f'No force with id={force_id}')

    def areAllForcesConfirmed(self):
        return all(f.confirmed for f in self._forces.values())

    def getForcesAsList(self):
        forces_list = [{'id': v.id, 'faces': v.facesFlat, 'confirmed': v.confirmed} for k, v in self._forces.items()]
        return forces_list

    def setForces(self, forces):
        if self._forces != forces:
            self._forces = forces
            self._objects = (self._anchors | self._forces)
            self._emit("forces", self._forces)
            self._emit("objects", self._objects)

    def getOptimizationStrategy(self):
        return self._optimization_strategy

    def setOptimizationStrategy(self, optimization_strategy):
        if self._optimization_strategy != optimization_strategy:
            self._optimization_strategy = optimization_strategy
            self._emit("optimization_strategy", self._optimization_strategy)

    def getOptimizationSafetyRatio(self):
        return self._optimization_safety_ratio

    def setOptimizationSafetyRatio(self, optimization_safety_ratio):
        if self._optimization_safety_ratio != optimization_safety_ratio:
            self._optimization_safety_ratio = optimization_safety_ratio
            self._emit("optimization_safety_ratio", self._optimization_safety_ratio)

    def getOptimizationAutoLowerSafetyRatio(self):
        return self._optimization_auto_lower_safety_ratio

    def setOptimizationAutoLowerSafetyRatio(self, optimization_auto_lower):
        if self._optimization_auto_lower_safety_ratio != optimization_auto_lower:
            self._optimization_auto_lower_safety_ratio = optimization_auto_lower
            self._emit("optimization_auto_lower_safety_ratio", self._optimization_auto_lower_safety_ratio)

    def setAccessToken(self, access_token):
        if self._access_token != access_token:
            self._access_token = access_token
            self._emit("access_token")

    def setRotationActive(self, active):
        controller = Application.getInstance().getController()
        if active and not self.getCurrentForceFacesFlat():
            self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "You have to select at least one face")
            return
        if self._rotation_active != active:
            self._rotation_active = active
            if active:
                controller.setActiveTool("Slicedog_1_RotateForceTool")
            else:
                controller.setActiveTool(None)
            self._emit("rotation_active", active)

    def getRotationActive(self):
        return self._rotation_active

    def getApiWrapper(self):
        return self._api_wrapper

    def isSelectMultipleAreas(self):
        return self._select_multiple_areas

    def setSelectMultipleAreas(self, val):
        if self._select_multiple_areas != val:
            self._select_multiple_areas = val
            self._emit("select_multiple_areas", val)

    def getLastFeedback(self):
        return self._last_feedback

    def getLastIterationFeedback(self):
        return self._last_iteration_feedback

    def getLastStatusFeedback(self):
        return self._last_status_feedback

    def getLastFeedbackStatusIndex(self):
        match self._last_feedback_status:
            case "RUNNING_MESH_ALGORITHMS":
                return 1
            case "RUNNING_ANALYSIS":
                return 2
            case "RUNNING_OPTIMIZATION":
                return 3
            case "RUNNING_OPTIMIZATION_PAST_3_ITERS":
                ## TODO: should be another step? Not from specification...
                return 3
            case "SUCCEEDED":
                return 4
            case _:
                return 0

    def getCurrentIterationInfo(self):
        return self._current_iteration_info

    def setLastFeedback(self, val):
    # def setLastFeedback(self, val, status=None, iteration_info=None):
        ## TODO: maybe update as feedback_status and iteration_info were added
        feedback_changed = False
        if val is not None:
        # if val is not None and self._last_feedback != val:
        # if val and val is not None and self._last_feedback != val:
            self._last_feedback = val
            feedback_changed = True

        # if status is not None:
        # # if status is not None and self._last_feedback_status != status:
        #     self._last_feedback_status = status
        #     feedback_changed = True

        # if iteration_info is not None and self._current_iteration_info != iteration_info:
        #     self._current_iteration_info = iteration_info
        #     feedback_changed = True

        if feedback_changed:
            self._emit("feedback", val)

    def setLastStatusFeedback(self, val, status=None):
        feedback_changed = False
        if val is not None:
            self._last_status_feedback = val
            feedback_changed = True

        if status is not None:
            self._last_feedback_status = status
            feedback_changed = True

        if feedback_changed:
            self._emit("status_feedback", val)

    def setLastIterationFeedback(self, val, iteration_info=None):
        feedback_changed = False
        if val is not None:
        # if val is not None and self._last_iteration_feedback != val:
            self._last_iteration_feedback = val
            feedback_changed = True

        if iteration_info is not None and self._current_iteration_info != iteration_info:
            self._current_iteration_info = iteration_info
            feedback_changed = True

        if feedback_changed:
            self._emit("iteration_feedback", val)

    def determineIfSaved(self):
        if self._face is None:
            return False

        face = self._face[0]
        face_id = self._face[1]

        for k, v in self.getObjects().items():
            faces = v.facesFlat
            if face_id in faces:
                if k.startswith('force'):
                    self.setCurrentStep(0)
                    # TODO what if step can't be selected?
                    if self.getCurrentStep() == 0:
                        self.selectForce(k)
                else:
                    self.setCurrentStep(1)
                    if self.getCurrentStep() == 1:
                        self.selectAnchor(k)

                return True

        return False

    def determineObjectFaces(self):
        if self._face is None:
            return

        face = self._face[0]
        face_id = self._face[1]

        all_faces = self._mesh_manager.getCachedMeshWithAdjacency(face.getName())
        if all_faces is None:
            start = time.time()
            connectivity = self._mesh_manager.buildEdgeConnectivity()
            end = time.time()
            Logger.log('d', f'Connectivity time elapsed: {end-start} s')
            start = time.time()
            all_faces = self._mesh_manager.buildFaceAdjacency(connectivity)
            end = time.time()
            Logger.log('d', f'Neighbors time elapsed: {end-start} s')

            self._mesh_manager.cacheMeshWithAdjacency(face.getName(), all_faces)

        object_faces = None
        # cached_objects = self._highlights_manager._cached_objects[face.getName()]
        # TODO: this is disabled for testing purposes; may be enabled after testing is complete; I suppose it should
        #  only be enabled once a robust and consistent detection of curved surfaces is working
        # for cached_object in cached_objects:
        #     if id in cached_object:
        #         print('Object cached')
        #         object_faces = cached_object
        #         break

        is_cylinder = False
        cylinder_axis_guess = None
        push = True
        if object_faces is None:
            ids = []

            if self._surface_selection == 'flat_surface':
                geometry_analyzer.findFlatSurface(self._mesh_manager.getMeshData(), face_id, all_faces, ids)
            elif self._surface_selection == 'convex_surface':
                is_cylinder, cylinder_axis_guess = geometry_analyzer.findConvexSurface(
                    self._mesh_manager.getMeshData(), face_id, all_faces, ids)
            elif self._surface_selection == 'concave_surface':
                is_cylinder, cylinder_axis_guess = geometry_analyzer.findConcaveSurface(
                    self._mesh_manager.getMeshData(), face_id, all_faces, ids)
                if is_cylinder:
                    push = False
            else:
                # TODO: fallback
                geometry_analyzer.findFlatSurface(self._mesh_manager.getMeshData(), face_id, all_faces, ids)

            object_faces = ids
            # self._highlights_manager._cached_objects[face.getName()].append(object_faces)

        # object_id = None
        # for k, v in self.getObjects().items():
        #     faces = v.facesFlat
        #     # TODO: is it enough to be a subset as we allow more complex objects to be created?
        #     # if sorted(faces) == sorted(object_faces):
        #     if set(object_faces).issubset(faces):
        #         if self.getCurrentStep() == 0:
        #             if k.startswith('force'):
        #                 self.selectForce(k)
        #                 return
        #             else:
        #                 self.setCurrentStep(1)
        #                 if self.getCurrentStep() == 1:
        #                     self.selectAnchor(k)
        #         elif self.getCurrentStep() == 1:
        #             if k.startswith('anchor'):
        #                 self.selectAnchor(k)
        #             else:
        #                 self.setCurrentStep(0)
        #                 if self.getCurrentStep() == 0:
        #                     self.selectForce(k)
        #         return

        if not self._current_force.id:
            if self.getCurrentStep() == 1:
                self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "Click on Add New Fixed Point first")
            else:
                self._message_manager.showMessage(MessageType.MISSING_USER_ACTION, "Click on Add New Force first")
            return

        current_force_facesFlat = self.getCurrentForceFacesFlat()
        if self._select_multiple_areas and current_force_facesFlat:
            # TODO does order matter? For now assuming that it does not
            all_faces = self.getCurrentForceFaces()
            # only add if faces are not already present
            if not set(object_faces).issubset(current_force_facesFlat):
                all_faces.append(object_faces)
        else:
            all_faces = [object_faces]


        # TODO this is rather quick, non-robust solution that may not work as expected, but I don't have time for this now
        points = []
        if is_cylinder:
            for face in all_faces[-1]:
                points.extend(self._highlights_manager.getMeshData().getFaceNodes(face))
            points = np.array(points)
            centroid = np.mean(points, axis=0)
            r_guess = np.mean(np.linalg.norm(points - centroid, axis=1))
            initial_guess = np.hstack([centroid, cylinder_axis_guess.getData(), r_guess])
            result = least_squares(geometry_analyzer.cylinderResiduals, initial_guess, args=(points,))
            cx, cy, cz, nx, ny, nz, r = result.x
            determined_center = Vector(cx, cy, cz)
            n = Vector(nx, ny, nz).normalized()
            # TODO: if determined r >> r_guess, probably not a cylinder to begin with; fallback
            if r > 2 * r_guess:
                determined_center, area = geometry_analyzer.calculateCenterOfMassAndArea(self._highlights_manager.getMeshData(), all_faces[-1])
                _, n = geometry_analyzer.getFacePlaneVectors(self.getHighlightManager().getMeshData(), all_faces[-1][0])
        else:
            determined_center = None
            largest_area = -1
            n = None
            for i, face_list in enumerate(all_faces):
                center, area = geometry_analyzer.calculateCenterOfMassAndArea(self._highlights_manager.getMeshData(), face_list)
                if area > largest_area:
                    largest_area = area
                    determined_center = center
                    _, n = geometry_analyzer.getFacePlaneVectors(self.getHighlightManager().getMeshData(), face_list[0])

        update_dict = {
            # 'id': object_id,
            'faces': all_faces,
            'center': determined_center,
            'direction': n,
            'push': push
        }
        self.setCurrentForce(replace(self.getCurrentForce(), **update_dict))

    def setProgressCallback(self, callback):
        self._mesh_manager.setProgressCallback(callback)

    def _onCurrentForceChangedCb(self, _):
        # confirmed should not be updated in saved forces; to save confirmed flag, explicitly update forces when confirming
        if self.getCurrentForceId() in self.getForces() and not self.getCurrentForceConfirmed():
            self.updateForces(self.getCurrentForce())
        elif self.getCurrentForceId() in self.getAnchors() and not self.getCurrentForceConfirmed():
            self.updateAnchors(self.getCurrentForce())


    def _loginErrorAction(self, msg, action):
        if action == 'LOG_IN':
            threading.Thread(target=lambda: self.logInWithGoogle(self._api_wrapper.logInGoogleCompleted.emit, False), daemon=True).start()
        elif action == 'REGISTER':
            threading.Thread(target=lambda: self.logInWithGoogle(self._api_wrapper.logInGoogleCompleted.emit, True), daemon=True).start()
        else:
            Logger.log('e', f'Unknown option {action}')
            self._emit("popup_requested", "unhandled")
            # self._message_manager.showMessage(MessageType.UNKNOWN)

def exportForceInN(magnitude: float, unit: str):
    match unit:
        case 'N':
            return magnitude
        case '%':
            min_value = 25
            max_value = 1000
            diff = max_value - min_value
            return min_value + diff * magnitude / 100
        case _:
            raise ValueError(f'Unknown unit {unit} in force definition!')

def safetyFactorExplanation(safety_factor: float):
    thresholds = [
        (1.5, 'At limit'),
        (2.5, 'Typical machinery'),
        (3.5, 'Robust'),
        (4.5, 'Conservative')
    ]

    for limit, label in thresholds:
        if safety_factor < limit:
            return label
    return 'Mission-critical'
