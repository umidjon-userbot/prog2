"""
    CREDITS:
        EVAL AND SH FUNCTION IN THIS MODULE IS WRITTEN BY @Pokurt.
        SOURCE:
            https://github.com/pokurt/Nana-Remix/blob/master/nana/plugins/devs.py
"""

import os
import re
import subprocess
import sys
import traceback
from inspect import getfullargspec
from io import StringIO

from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, USERBOT_PREFIX, app, app2

__MODULE__ = "Userbot"
__HELP__ = """
.alive - Send Alive Message.
.l - Execute Python Code.
.sh - Execute Shell Code.
.approve | .disapprove - Approve Or Disapprove A User To PM You.
.block | .unblock - Block Or Unblock A User.
"""


# Eval and Sh module from nana-remix


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app2.on_message(
    filters.user(SUDOERS)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.command("l", prefixes=USERBOT_PREFIX)
)
async def executor(client, message):
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await message.delete()
        return
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        f"**INPUT:**\n```{cmd}```\n\n**OUTPUT**:\n```{evaluation.strip()}```"
    )
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        await message.reply_document(
            document=filename,
            caption=f"**INPUT:**\n`{cmd[0:980]}`\n\n**OUTPUT:**\n`Attached Document`",
            quote=False,
        )
        await message.delete()
        os.remove(filename)
    else:
        await edit_or_reply(message, text=final_output)


@app2.on_message(
    filters.user(SUDOERS)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.command("sh", prefixes=USERBOT_PREFIX),
)
async def shellrunner(client, message):
    if len(message.command) < 2:
        await edit_or_reply(message, text="**Usage:**\n/sh git pull")
        return
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as err:
                print(err)
                await edit_or_reply(
                    message,
                    text=f"**INPUT:**\n```{text}```\n\n**ERROR:**\n```{err}```",
                )
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", text)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            print(err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            await edit_or_reply(
                message,
                text=f"**INPUT:**\n```{text}```\n\n**ERROR:**\n```{''.join(errors)}```",
            )
            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await app.send_document(
                message.chat.id,
                "output.txt",
                reply_to_message_id=message.message_id,
                caption="`Output`",
            )
            os.remove("output.txt")
            return
        await edit_or_reply(
            message,
            text=f"**INPUT:**\n```{text}```\n\n**OUTPUT:**\n```{output}```",
        )
    else:
        await edit_or_reply(
            message,
            text=f"**INPUT:**\n```{text}```\n\n**OUTPUT: **\n`No output`",
        )
