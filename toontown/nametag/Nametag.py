from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from pandac.PandaModules import *

from otp.otpbase import OTPGlobals
from toontown.chat.ChatBalloon import ChatBalloon
from toontown.nametag import NametagGlobals


class Nametag(FSM, PandaNode, DirectObject):
    TEXT_WORD_WRAP = 8
    TEXT_Y_OFFSET = -0.05

    CHAT_TEXT_WORD_WRAP = 12

    PANEL_X_PADDING = 0.2
    PANEL_Z_PADDING = 0.2

    CHAT_BALLOON_ALPHA = 1

    def __init__(self):
        FSM.__init__(self, 'nametag')
        PandaNode.__init__(self, 'nametag')
        DirectObject.__init__(self)

        self.avatar = None
        self.active = True

        self.frame = None

        self.panel = None
        self.icon = None
        self.chatBalloon = None
        self.chatButton = NametagGlobals.noButton

        self.font = None
        self.chatFont = None

        self.chatType = NametagGlobals.CHAT
        self.chatBalloonType = NametagGlobals.CHAT_BALLOON

        self.nametagColor = NametagGlobals.NametagColors[NametagGlobals.CCNormal]
        self.chatColor = NametagGlobals.ChatColors[NametagGlobals.CCNormal]
        self.speedChatColor = self.chatColor[0][1]

        self.nametagHidden = False
        self.chatHidden = False
        self.thoughtHidden = False

        self.lastClickState = NametagGlobals.NORMAL
        self.clickState = NametagGlobals.NORMAL
        self.pendingClickState = NametagGlobals.NORMAL

        self.clickEvent = ''
        self.clickExtraArgs = []

        # Create the container of our geometry:
        self.contents = NodePath.anyPath(self).attachNewNode('contents')

        # Create our TextNodes:
        self.textNode = TextNode('text')
        self.textNode.setWordwrap(self.TEXT_WORD_WRAP)
        self.textNode.setTextColor(self.nametagColor[self.clickState][0])
        self.textNode.setAlign(TextNode.ACenter)

        self.chatTextNode = TextNode('chatText')
        self.chatTextNode.setWordwrap(self.CHAT_TEXT_WORD_WRAP)
        self.chatTextNode.setTextColor(self.chatColor[self.clickState][0])
        self.chatTextNode.setGlyphScale(ChatBalloon.TEXT_GLYPH_SCALE)
        self.chatTextNode.setGlyphShift(ChatBalloon.TEXT_GLYPH_SHIFT)

        # Add the tick task:
        self.tickTaskName = self.getUniqueName() + '-tick'
        self.tickTask = taskMgr.add(self.tick, self.tickTaskName, sort=45)

        # Create the click region:
        self.regionName = self.getUniqueName() + '-region'
        self.region = MouseWatcherRegion(self.regionName, 0, 0, 0, 0)
        base.mouseWatcherNode.addRegion(self.region)

        # Accept the mouse events:
        self.accept(base.mouseWatcherNode.getEnterPattern().replace('%r', self.regionName), self.__handleMouseEnter)
        self.accept(base.mouseWatcherNode.getLeavePattern().replace('%r', self.regionName), self.__handleMouseLeave)
        self.accept(base.mouseWatcherNode.getButtonDownPattern().replace('%r', self.regionName), self.__handleMouseDown)
        self.accept(base.mouseWatcherNode.getButtonUpPattern().replace('%r', self.regionName), self.__handleMouseUp)

    def destroy(self):
        self.ignoreAll()

        if self.tickTask is not None:
            taskMgr.remove(self.tickTask)
            self.tickTask = None

        self.chatTextNode = None
        self.textNode = None

        if self.contents is not None:
            self.contents.removeNode()
            self.contents = None

        self.chatFont = None
        self.font = None

        self.chatButton = NametagGlobals.noButton

        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.icon is not None:
            self.icon.removeAllChildren()
            self.icon = None

        if self.panel is not None:
            self.panel.removeNode()
            self.panel = None

        self.avatar = None

        if self.frame is not None:
            self.frame.destroy()
            self.frame = None

    def getUniqueName(self):
        return 'Nametag-' + str(id(self))

    def getChatBalloonModel(self):
        pass  # Inheritors should override this method.

    def getChatBalloonWidth(self):
        pass  # Inheritors should override this method.

    def getChatBalloonHeight(self):
        pass  # Inheritors should override this method.

    def tick(self, task):
        return Task.done  # Inheritors should override this method.

    def updateClickRegion(self):
        pass  # Inheritors should override this method.

    def setAvatar(self, avatar):
        self.avatar = avatar

    def getAvatar(self):
        return self.avatar

    def setActive(self, active):
        self.active = active
        if self.active:
            self.region.setActive(True)
            self.setClickState(PGButton.SReady)
        else:
            self.region.setActive(False)
            self.setClickState(PGButton.SInactive)

    def getActive(self):
        return self.active

    def setIcon(self, icon):
        self.icon = icon

    def getIcon(self):
        return self.icon

    def setChatButton(self, chatButton):
        self.chatButton = chatButton

    def getChatButton(self):
        return self.chatButton

    def setFont(self, font):
        self.font = font
        if self.font is not None:
            self.textNode.setFont(self.font)
        self.update()

    def getFont(self):
        return self.font

    def setChatFont(self, chatFont):
        self.chatFont = chatFont
        if self.chatFont is not None:
            self.chatTextNode.setFont(self.chatFont)
        self.update()

    def getChatFont(self):
        return self.chatFont

    def setChatType(self, chatType):
        self.chatType = chatType

    def getChatType(self):
        return self.chatType

    def setChatBalloonType(self, chatBalloonType):
        self.chatBalloonType = chatBalloonType

    def getChatBalloonType(self):
        return self.chatBalloonType

    def setNametagColor(self, nametagColor):
        self.nametagColor = nametagColor

    def getNametagColor(self):
        return self.nametagColor

    def setChatColor(self, chatColor):
        self.chatColor = chatColor

    def getChatColor(self):
        return self.chatColor

    def setSpeedChatColor(self, speedChatColor):
        self.speedChatColor = speedChatColor

    def getSpeedChatColor(self):
        return self.speedChatColor

    def hideNametag(self):
        self.nametagHidden = True

    def showNametag(self):
        self.nametagHidden = False

    def hideChat(self):
        self.chatHidden = True

    def showChat(self):
        self.chatHidden = False

    def hideThought(self):
        self.thoughtHidden = True

    def showThought(self):
        self.thoughtHidden = False

    def setLastClickState(self, lastClickState):
        self.lastClickState = lastClickState

    def getLastClickState(self):
        return self.lastClickState

    def setClickState(self, clickState):
        self.lastClickState = self.clickState
        self.clickState = clickState

        if self.chatBalloon is not None:
            foreground, background = self.chatColor[self.clickState]
            if self.chatType == NametagGlobals.SPEEDCHAT:
                background = self.speedChatColor
            self.chatBalloon.setForeground(foreground)
            self.chatBalloon.setBackground(background)
        elif self.panel is not None:
            foreground, background = self.nametagColor[self.clickState]
            self.setForeground(foreground)
            self.setBackground(background)

        if self.clickState == PGButton.SReady:
            self.request('Normal')
        elif self.clickState == PGButton.SDepressed:
            self.request('Down')
        elif self.clickState == PGButton.SRollover:
            self.request('Rollover')
        elif self.clickState == PGButton.SInactive:
            self.request('Disabled')

    def getClickState(self):
        return self.clickState

    def setPendingClickState(self, pendingClickState):
        self.pendingClickState = pendingClickState

    def getPendingClickState(self):
        return self.pendingClickState

    def setText(self, text):
        self.textNode.setText(text)

    def getText(self):
        return self.textNode.getText()

    def setChatText(self, chatText):
        self.chatTextNode.setText(chatText)

    def getChatText(self):
        return self.chatTextNode.getText()

    def setWordWrap(self, wordWrap):
        if wordWrap > self.TEXT_WORD_WRAP:
            wordWrap = self.TEXT_WORD_WRAP
        self.textNode.setWordwrap(wordWrap)

    def getWordWrap(self):
        return self.textNode.getWordwrap()

    def setChatWordWrap(self, chatWordWrap):
        if chatWordWrap > self.CHAT_TEXT_WORD_WRAP:
            chatWordWrap = self.CHAT_TEXT_WORD_WRAP
        self.chatTextNode.setWordwrap(chatWordWrap)

    def getChatWordWrap(self):
        return self.chatTextNode.getWordwrap()

    def setForeground(self, foreground):
        self.textNode.setTextColor(foreground)

    def setBackground(self, background):
        if self.panel is not None:
            self.panel.setColor(background)

    def setShadow(self, shadow):
        self.textNode.setShadow(shadow)

    def getShadow(self):
        return self.textNode.getShadow()

    def clearShadow(self):
        self.textNode.clearShadow()

    def setClickEvent(self, event, extraArgs=[]):
        self.clickEvent = event
        self.clickExtraArgs = extraArgs

    def update(self):
        self.contents.node().removeAllChildren()

        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.panel is not None:
            self.panel.removeNode()
            self.panel = None

        if self.getChatText():
            if self.chatBalloonType == NametagGlobals.CHAT_BALLOON:
                if not self.chatHidden:
                    model = self.getChatBalloonModel()
                    modelWidth = self.getChatBalloonWidth()
                    modelHeight = self.getChatBalloonHeight()
                    self.drawChatBalloon(model, modelWidth, modelHeight)
                    return
            elif self.chatBalloonType == NametagGlobals.THOUGHT_BALLOON:
                if not self.thoughtHidden:
                    model = NametagGlobals.thoughtBalloonModel
                    modelWidth = NametagGlobals.thoughtBalloonWidth
                    modelHeight = NametagGlobals.thoughtBalloonHeight
                    self.drawChatBalloon(model, modelWidth, modelHeight)
                    return

        if self.getText() and (not self.nametagHidden):
            self.drawNametag()

        if self.active or (self.getChatButton() != NametagGlobals.noButton):
            self.updateClickRegion()

    def drawChatBalloon(self, model, modelWidth, modelHeight):
        if self.chatFont is None:
            # We can't draw this without a font.
            return

        # If we have a chat balloon button, we must override the click state:
        if self.getChatButton() != NametagGlobals.noButton:
            self.clickState = self.pendingClickState

        foreground, background = self.chatColor[self.clickState]
        if self.chatType == NametagGlobals.SPEEDCHAT:
            background = self.speedChatColor
        if background[3] > self.CHAT_BALLOON_ALPHA:
            background = VBase4(
                background[0], background[1], background[2],
                self.CHAT_BALLOON_ALPHA)

        self.chatBalloon = ChatBalloon(
            model, modelWidth, modelHeight, self.chatTextNode,
            foreground=foreground, background=background,
            button=self.chatButton[self.clickState])
        self.chatBalloon.reparentTo(self.contents)

    def drawNametag(self):
        if self.font is None:
            # We can't draw this without a font.
            return

        # If we are not active, we must ensure that we have the correct click
        # state:
        if not self.active:
            self.clickState = PGButton.SInactive

        # Attach the icon:
        if self.icon is not None:
            self.contents.attachNewNode(self.icon)

        foreground, background = self.nametagColor[self.clickState]

        # Set the color of the TextNode:
        self.textNode.setTextColor(foreground)

        # Attach the TextNode:
        textNodePath = self.contents.attachNewNode(self.textNode, 1)
        textNodePath.setTransparency(foreground[3] < 1)
        textNodePath.setAttrib(DepthWriteAttrib.make(0))
        textNodePath.setY(self.TEXT_Y_OFFSET)

        # Attach a panel behind the TextNode:
        self.panel = NametagGlobals.cardModel.copyTo(self.contents, 0)
        self.panel.setColor(background)
        self.panel.setTransparency(background[3] < 1)

        # Reposition the panel:
        x = (self.textNode.getLeft()+self.textNode.getRight()) / 2.0
        z = (self.textNode.getTop()+self.textNode.getBottom()) / 2.0
        self.panel.setPos(x, 0, z)

        # Resize the panel:
        sX = self.textNode.getWidth() + self.PANEL_X_PADDING
        sZ = self.textNode.getHeight() + self.PANEL_Z_PADDING
        self.panel.setScale(sX, 1, sZ)

        self.panelWidth = sX
        self.panelHeight = sZ

    def enterNormal(self):
        if self.lastClickState == PGButton.SDepressed:
            messenger.send(self.clickEvent, self.clickExtraArgs)

    def enterDown(self):
        base.playSfx(NametagGlobals.clickSound)

    def enterRollover(self):
        if self.lastClickState == PGButton.SDepressed:
            messenger.send(self.clickEvent, self.clickExtraArgs)
        else:
            base.playSfx(NametagGlobals.rolloverSound)

    def enterDisabled(self):
        pass

    def __handleMouseEnter(self, region, extra):
        self.pendingClickState = PGButton.SRollover
        if (self.clickState == PGButton.SReady) or (self.getChatText() and (self.getChatButton() != NametagGlobals.noButton)):
            self.setClickState(PGButton.SRollover)

    def __handleMouseLeave(self, region, extra):
        self.pendingClickState = PGButton.SReady
        if self.clickState == PGButton.SRollover:
            self.setClickState(PGButton.SReady)

    def __handleMouseDown(self, region, button):
        if self.clickState == PGButton.SRollover:
            self.setClickState(PGButton.SDepressed)

    def __handleMouseUp(self, region, button):
        if self.clickState == PGButton.SDepressed:
            self.setClickState(self.pendingClickState)

    def setClickRegion(self, left, right, bottom, top):
        pass # Inheritors should override this method.
