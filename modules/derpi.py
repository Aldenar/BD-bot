name = "derpi"
hooks = ["on_ready", "on_message"]


def on_ready(cli):
    cli.send_message(cli.get_channel('295615551991054347'), "Ping pong, I got a big dong!")


def on_message(cli, message):
    cli.send_message(message.channel, "Oh come on, fug off, lemme sleep")
