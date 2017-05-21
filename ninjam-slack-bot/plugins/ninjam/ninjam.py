import os
import sys
import re
from errbot import BotPlugin, re_botcmd
from time import sleep
from ninjambot import NINJAMConnection, make_daemon_thread, ninjam_bot
from multiprocessing import Process, JoinableQueue as Queue
from configparser import ConfigParser

# Config
config = ConfigParser()
config.read("ninjam.cfg")
ninjam_config = config['ninjam']
chat_config = config['chat']


class Ninjam(BotPlugin):
    """Ninjam Notifications"""

    def activate(self):
        """Run ninjam_bot"""
        super().activate()

        # Stuff
        self.queue = Queue()
        #self.ninjam = NINJAMConnection(host, port, username, password)
        self.ninjam = NINJAMConnection(**ninjam_config)
        self.channel = self.build_identifier(chat_config['channel'])

        # Ninjam
        ninjam_thread = make_daemon_thread(
            target=ninjam_bot,
            args=(self.queue, self.ninjam))
        ninjam_thread.start()

        # Queue factory
        def queue_factory(queue, ninjam):
            while True:
                mode, *data = queue.get()
                if mode == 'LOGIN':
                    self.send(self.channel, self.report_login(data[0]))
                    self.send(self.channel, self.report_users())
                    queue.task_done()
                elif mode == 'NINJAM':
                    ninjam.sendmsg(*data)
                    queue.task_done()

        queue_thread = make_daemon_thread(
            target=queue_factory,
            args=(self.queue, self.ninjam))
        queue_thread.start()

    def report_login(self, user):
        text = "**%s** has joined ninjam" % self.get_id(user)
        self.log.info(text)
        return text

    @re_botcmd(pattern=r"^ninjam stat(us)?", prefixed=False, flags=re.IGNORECASE)
    def ninjam_status(self, msg, args):
        return self.report_users(show_users=True)

    def report_users(self, show_users=False):
        try:
            self.ninjam
        except NameError:
            self.log.error('NameError on self.ninjam')
            return "Sorry, I'm having trouble getting ninjam data"
        if len(self.ninjam.users) == 1:
            are_is = 'is'
            user_users = 'user'
        else:
            are_is = 'are'
            user_users = 'users'
        text = "There %s %d logged in %s right now" % (are_is,
                                                       len(self.ninjam.users),
                                                       user_users)
        userlist = ', '.join([self.get_id(x) for x in self.ninjam.users])
        if userlist and show_users:
            text += " (%s)" % userlist
        return text

    @staticmethod
    def get_id(user):
        return user.split('@')[0]
