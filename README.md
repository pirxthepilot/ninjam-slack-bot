# ninjam/slack bot

Monitors a [Ninjam](http://www.cockos.com/ninjam/) server and sends notifications to a Slack channel everytime someone logs in. Also reports the count and list of currently logged in users.

Powered by [Errbot](http://errbot.io)!


## Prerequisites

* Python 3.3+
* pip
* Virtualenv is recommended


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


## Acknowledgment

Huge thanks to [teamikl](https://github.com/teamikl) for the Ninjam-side code (based [here](https://github.com/teamikl/ninjam-chat/blob/master/src/ninjam-bot/bot.py))
