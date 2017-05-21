# Ninjam Bot
#
# Code lifted from
#   https://github.com/teamikl/ninjam-chat/blob/master/src/ninjam-bot/bot.py
#
# Credits: Ikkei Shimomura


import io
import sys
import os
import re
import hashlib
import logging
from socket import socket
from struct import Struct, pack, unpack
from threading import Thread
from collections import namedtuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
handler = logging.FileHandler('ninjam.log')
logger.addHandler(handler)

EXIT_RESTART = 3

NetMsg = Struct("<BL")

UserInfo = namedtuple(
    "UserInfo",
    "active,index,volume,pan,flags,username,channel")



class NINJAMConnection:
    def __init__(self, host, port, username, password):
        sock = socket()
        sock.connect((host, int(port)))

        self._sock = sock
        self._stream = sock.makefile("rb")
        self.username = username
        self.password = password
        self.users = {}

    def message_loop(self):
        read = self._stream.read
        for header in iter(lambda: read(5), b''):
            if len(header) < 5:
                logger.debug("NINJAM Connection lost")
                os._exit(EXIT_RESTART)
                break
            msgtype, msglen = NetMsg.unpack(header)
            msgbody = read(msglen) if msglen > 0 else b''
            yield msgtype, msgbody

    def sendmsg(self, msgtype, msg):
        logger.debug("SEND> {:02X} {}".format(msgtype, msg))
        try:
            self._sock.sendall(NetMsg.pack(msgtype, len(msg)) + msg)
        except:
            Logger.error(('sendmsg error'))
            import traceback
            traceback.print_exc()
            os._exit(EXIT_RESTART)

    @staticmethod
    def _parse_user_info(data, offset=0):
        assert isinstance(data, bytes)
        view = memoryview(data)
        stream = io.BytesIO(data)

        while len(data) > offset:
            params = unpack("<BBhBB", view[offset:offset+6])
            active, index, volume, pan, flags = params
            offset += 6
            stream.seek(offset, io.SEEK_SET)

            offset = data.find(b"\x00", offset + 1)
            assert offset >= 0
            username = stream.read(offset - stream.tell())
            stream.seek(1, io.SEEK_CUR)

            offset = data.find(b"\x00", offset + 1)
            assert offset >= 0
            channel = stream.read(offset - stream.tell())
            stream.seek(1, io.SEEK_CUR)
            offset += 1

            yield UserInfo(active, index, volume, pan, flags,
                           username, channel)

    @classmethod
    def parse_user_info(cls, data):
        return list(cls._parse_user_info(data))


def ninjam_start_keep_alive_timer(ninjam, interval):
        thread = make_daemon_thread(
                    target=ninjam_keep_alive_timer,
                    args=(ninjam, interval))
        thread.start()
        #Logger.info("KeepAlive timer started (interval {})".format(interval))
        return thread

def ninjam_keep_alive_timer(ninjam, interval):
    import time
    while 1:
        time.sleep(interval)
        ninjam.sendmsg(0xfd, b"")

def make_daemon_thread(**kw):
    thread = Thread(**kw)
    thread.setDaemon(True)
    return thread


def ninjam_bot(Q, ninjam):
    for msgtype, msgbody in ninjam.message_loop():
        logger.debug("{:02X} {}".format(msgtype, msgbody))
        if msgtype == 0x00:  # SERVER AUTH CHALLENGE
            username = ninjam.username.encode("latin-1")
            password = ninjam.password.encode("latin-1")
            challenge, servercaps, protover = unpack("<8sLL", msgbody[:16])
            #logger.debug("{} {:08x} {:08x}".format(challenge, servercaps, protover))

            # keep-alive (minimum keep-alive is 3)
            keep_alive_interval = max((servercaps >> 8) & 0xff, 3)
            ninjam_start_keep_alive_timer(ninjam, keep_alive_interval)

            passhash = hashlib.sha1(username + b":" + password).digest()
            passhash = hashlib.sha1(passhash + challenge).digest()
            # CLIENT AUTH USER
            x = pack("<LL", servercaps, protover)
            chunk = passhash + username + b"\x00" + x
            ninjam.sendmsg(0x80, chunk)
            del x, chunk
        elif msgtype == 0x01:  # SERVER AUTH REPLY
            logger.debug("Setting channel info")
            ninjam.sendmsg(0x82, b"")
        elif msgtype == 0x03:  # SERVER USERINFO CHANGE NOTIFY
            for info in ninjam.parse_user_info(msgbody):
                if info.active == 1:
                    ninjam.users[info.username.decode("latin-1")] = 1
        elif msgtype == 0xC0:  # CHAT
            params = msgbody.split(b'\x00')
            assert len(params) == 6
            mode, sender, message, _, _, _ = params
            sender = sender.decode('latin-1')
            if mode == b"JOIN":
                logger.info('%s logged in' % sender)
                ninjam.users[sender] = 1
                Q.put(("LOGIN", sender))
            elif mode == b"PART":
                logger.info('%s logged off' % sender)
                ninjam.users.pop(sender, None)
                #Q.put(("LOGOFF", sender))
