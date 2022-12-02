import asyncio
import click
import logging
import os
import random
import sys

from typing import List, NamedTuple, Optional, Tuple
from toot import __version__
from toot.asynch import api
from toot.output import echo, print_out
from toot.utils import EOF_KEY, editor_input, multiline_input

# Tweak the Click context
# https://click.palletsprojects.com/en/8.1.x/api/#context
CONTEXT = dict(
    # Enable using environment variables to specify options
    auto_envvar_prefix='TOOT',
    # Add shorthand -h for invoking help
    help_option_names=['-h', '--help'],
    # Give help some more room (default is 80)
    max_content_width=100,
    # Always show default values for options
    show_default=True,
)


def validate_language(ctx, param, value: str) -> str:
    if value and len(value) != 3:
        raise click.BadParameter(
            "Expected a 3 letter abbreviation according to ISO 639-2 standard."
        )

    return value


class Obj(NamedTuple):
    color: bool
    debug: bool
    json: bool
    quiet: bool


@click.group(context_settings=CONTEXT)
@click.option("--debug/--no-debug", default=False, help="Log debug info to stderr")
@click.option("--color/--no-color", default=sys.stdout.isatty(), help="Use ANSI color in output")
@click.option("--quiet/--no-quiet", default=False, help="Don't print anything to stdout")
@click.option("--json/--no-json", default=False, help="Print data as JSON rather than human readable textv")
@click.version_option(version=__version__, prog_name="toot")
@click.pass_context
def cli(ctx, debug: bool, color: bool, quiet: bool, json: bool):
    ctx.color = color
    ctx.obj = Obj(color=color, debug=debug, json=json, quiet=quiet)
    print(ctx.obj)
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.argument("url")
def instance(url: str):
    instance = asyncio.run(api.instance(url)).json()
    # print(instance.body)
    click.secho(instance["title"], fg="green")
    click.secho(instance["uri"], fg="blue")
    click.echo(f'Running Mastodon {instance["version"]}')


@cli.command()
@click.argument("text", required=False)
@click.option(
    "-e", "--editor", is_flag=True,
    flag_value=os.environ.get("EDITOR"),
    show_default=os.environ.get("EDITOR"),
    help="""Use an editor to compose your toot, defaults to editor defined in
            the $EDITOR environment variable."""
)
@click.option(
    "-m", "--media", multiple=True,
    help="""Path to a media file to attach (specify multiple times to attach up
            to 4 files)""",
)
@click.option(
    "-d", "--description", multiple=True,
    help="""Plain-text description of the media for accessibility purposes, one
            per attached media""",
)
@click.option(
    "-l", "--language",
    help="ISO 639-2 language code of the toot, to skip automatic detection",
    callback=validate_language
)
def post(
    text: str,
    editor: str,
    media: Tuple[str, ...],
    description: Tuple[str, ...],
    language: Optional[str],
):
    if editor and not sys.stdin.isatty():
        raise click.UsageError("Cannot run editor if not in tty.")

    if media and len(media) > 4:
        raise click.UsageError("Cannot attach more than 4 files.")

    echo("unstyled <red>posting</red> <dim>dim</dim> <underline><red>unde</red><blue>rline</blue></underline> <b>bold</b> unstlyed")
    echo("<bold>Bold<italic> bold and italic </bold>italic</italic>")
    echo("<bold red underline>foo</>bar")
    echo("\\<bold red underline>foo</>bar")
    echo("plain <blue>red <underline> red <green>and</green> underline </underline> red </blue> plain")
    # echo("Done")
    # media_ids = _upload_media(app, user, args)
    # status_text = _get_status_text(text, editor)

    # if not status_text and not media_ids:
    #     raise click.UsageError("You must specify either text or media to post.")

    # response = api.post_status(
    #     app, user, status_text,
    #     visibility=args.visibility,
    #     media_ids=media_ids,
    #     sensitive=args.sensitive,
    #     spoiler_text=args.spoiler_text,
    #     in_reply_to_id=args.reply_to,
    #     language=args.language,
    #     scheduled_at=args.scheduled_at,
    #     content_type=args.content_type
    # )

    # if "scheduled_at" in response:
    #     print_out("Toot scheduled for: <green>{}</green>".format(response["scheduled_at"]))
    # else:
    #     print_out("Toot posted: <green>{}</green>".format(response.get('url')))


def _get_status_text(text, editor):
    isatty = sys.stdin.isatty()

    if not text and not isatty:
        text = sys.stdin.read().rstrip()

    if isatty:
        if editor:
            text = editor_input(editor, text)
        elif not text:
            print_out("Write or paste your toot. Press <yellow>{}</yellow> to post it.".format(EOF_KEY))
            text = multiline_input()

    return text


def _upload_media(app, user, args):
    # Match media to corresponding description and upload
    media = args.media or []
    descriptions = args.description or []
    uploaded_media = []

    for idx, file in enumerate(media):
        description = descriptions[idx].strip() if idx < len(descriptions) else None
        result = _do_upload(app, user, file, description)
        uploaded_media.append(result)

    return [m["id"] for m in uploaded_media]


def _do_upload(app, user, file: str, description: Optional[str]):
    print("Faking upload:", file, description)
    id = random.randint(1, 99999)
    return {"id": id, "text_url": f"http://example.com/{id}"}


def main():
    # Allow overriding options using environment variables
    # https://click.palletsprojects.com/en/8.1.x/options/?highlight=auto_env#values-from-environment-variables
    cli()
