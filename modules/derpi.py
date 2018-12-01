import re

name="derpi"
hooks=["on_message", "on_member_join"]

def on_message(cli, message):
    if not is_interesting_message(cli, message.content):
        return



def on_member_join(cli, member):
    return


def is_interesting_message(cli, text):
    parts = re.sub(" {2,}", "", text).split(" ")
    cli.logger.debug(parts)
