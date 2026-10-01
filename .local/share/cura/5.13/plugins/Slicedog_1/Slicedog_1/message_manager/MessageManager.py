from UM.Message import Message
from Slicedog_1.message_manager.MessageType import MessageType

class MessageManager:
    def __init__(self):
        self._messages = {}
        self._current_message_type = None

    def registerMessage(self, message_type: MessageType, message: Message):
        self._messages[message_type] = message

    def isMessageTypeRegistered(self, message_type: MessageType):
        return message_type in self._messages

    def showMessage(self, message_type: MessageType, text=None, title=None):
        match message_type:
            case MessageType.NONE:
                # Just check if current message is visible and if not, show it again
                if self._current_message_type is not None:
                    current_message = self._messages.get(self._current_message_type)
                    if current_message is not None and not current_message.visible:
                        current_message.show()
            case MessageType.OPTIMIZATION_STILL_RUNNING | MessageType.OPEN_SAMPLES:
                # OPTIMIZATION_STILL_RUNNING: This is a direct warning for user clicking on a button that he shouldn't
                # and as such it does not hide other messages or becomes active - it is an extra message
                # OPEN_SAMPLES: This can accompany other message (for example optimization result)
                message = self._messages.get(message_type)
                if message:
                    message.show()
                if text is not None:
                    message.setText(text)
                if title is not None:
                    message.setTitle(title)
            case _:
                if self._current_message_type != message_type:
                    self.hideAllMessages()
                message = self._messages.get(message_type)
                if message:
                    message.show()
                    self._current_message_type = message_type
                    if text is not None:
                        message.setText(text)
                    if title is not None:
                        message.setTitle(title)

    def hideMessage(self, message_type: MessageType):
        message = self._messages.get(message_type)
        if message:
            message.hide()
            self._current_message_type = None

    def hideAllMessages(self):
        for message in self._messages.values():
            message.hide()
        self._current_message_type = None

    # def updateCurrentMessageText(self, text: str):
    #     if self._current_message_type is not None:
    #         self._messages[self._current_message_type].setText(text)

    def updateCurrentMessageIcon(self, image_source: str):
        # TODO better way - QML?
        if self._current_message_type is not None:
            self._messages[self._current_message_type]._image_source = image_source