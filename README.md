# ninjam/slack bot

Monitors a [Ninjam](http://www.cockos.com/ninjam/) server and sends notifications to a Slack channel everytime someone logs in. Also reports the count and list of currently logged in users.

Powered by [Errbot](http://errbot.io)!


## Prerequisites

* Python 3.3+
* pip
* Virtualenv is recommended
* Systemd (for the auto-start service)


## Installation

First, deploy this repo and install the necessary python modules

```
git clone https://github.com/pirxthepilot/ninjam-slack-bot.git
cd ninjam-slack-bot
virtualenv --python=$(which python3) virtualenv
. virtualenv/bin/activate
pip install -r requirements.txt
```

Inside the `ninjam-slack-bot` dir, create `config.py` and `ninjam.cfg` (see included .example files). Set the parameters as needed.

Finally, run errbot:

```
errbot
```

or

```
errbot --daemon
```

**To start automatically as a service with systemd:**

Copy the supplied `errbot.service.example` to `/etc/systemd/system/errbot.service`. Edit the paths and username in the file - make sure everything is correct!

Then do

```
systemctl daemon-reload
systemctl enable errbot
systemctl start errbot
```


## Acknowledgments

Huge thanks to:

* [teamikl](https://github.com/teamikl) for the Ninjam-side code (based [here](https://github.com/teamikl/ninjam-chat/blob/master/src/ninjam-bot/bot.py))
* The [Ninjam Protocol](https://github.com/wahjam/wahjam/wiki/Ninjam-Protocol) documentation
