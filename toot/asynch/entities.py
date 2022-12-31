import typing
import dataclasses

from dataclasses import dataclass, is_dataclass
from datetime import date, datetime, time
from typing import Dict, List, Optional
from typing import get_origin, get_args


@dataclass
class AccountField:
    """
    https://docs.joinmastodon.org/entities/Account/#Field
    """
    name: str
    value: str
    verified_at: Optional[datetime]


@dataclass
class CustomEmoji:
    """
    https://docs.joinmastodon.org/entities/CustomEmoji/
    """
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: str


@dataclass
class Account:
    """
    https://docs.joinmastodon.org/entities/Account/
    """
    id: str
    username: str
    acct: str
    url: str
    display_name: str
    note: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    locked: bool
    fields: List[AccountField]
    emojis: List[CustomEmoji]
    bot: bool
    group: bool
    discoverable: Optional[bool]
    noindex: Optional[bool]
    moved: Optional["Account"]
    suspended: Optional[bool]
    limited: Optional[bool]
    created_at: datetime
    last_status_at: Optional[date]
    statuses_count: int
    followers_count: int
    following_count: int


@dataclass
class Application:
    name: str
    website: str


@dataclass
class MediaAttachment:
    id: str
    type: str
    url: str
    preview_url: str
    remote_url: Optional[str]
    meta: dict
    description: str
    blurhash: str


@dataclass
class StatusMention:
    """
    https://docs.joinmastodon.org/entities/Status/#Mention
    """
    id: str
    username: str
    url: str
    acct: str


@dataclass
class StatusTag:
    """
    https://docs.joinmastodon.org/entities/Status/#Tag
    """
    name: str
    url: str


@dataclass
class PollOption:
    """
    https://docs.joinmastodon.org/entities/Poll/#Option
    """
    title: str
    votes_count: Optional[int]


@dataclass
class Poll:
    """
    https://docs.joinmastodon.org/entities/Poll/
    """
    id: str
    expires_at: Optional[datetime]
    expired: bool
    multiple: bool
    votes_count: int
    voters_count: Optional[int]
    options: List[PollOption]
    emojis: List[CustomEmoji]
    voted: Optional[bool]
    own_votes: Optional[List[int]]


@dataclass
class PreviewCard:
    url: str
    title: str
    description: str
    type: str
    author_name: str
    author_url: str
    provider_name: str
    provider_url: str
    html: str
    width: int
    height: int
    image: Optional[str]
    embed_url: str
    blurhash: Optional[str]


@dataclass
class FilterKeyword:
    id: str
    keyword: str
    whole_word: str


@dataclass
class FilterStatus:
    id: str
    status_id: str


@dataclass
class Filter:
    id: str
    title: str
    context: List[str]
    expires_at: Optional[datetime]
    filter_action: str
    keywords: List[FilterKeyword]
    statuses: List[FilterStatus]


@dataclass
class FilterResult:
    filter: Filter
    keyword_matches: Optional[List[str]]
    status_matches: Optional[str]


@dataclass
class Status:
    id: str
    uri: str
    created_at: datetime
    account: Account
    content: str
    visibility: str
    sensitive: bool
    spoiler_text: str
    media_attachments: List[MediaAttachment]
    application: Optional[Application]
    mentions: List[StatusMention]
    tags: List[StatusTag]
    emojis: List[CustomEmoji]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    url: Optional[str]
    in_reply_to_id: Optional[str]
    in_reply_to_account_id: Optional[str]
    reblog: Optional["Status"]
    poll: Optional[Poll]
    card: Optional[PreviewCard]
    language: Optional[str]
    text: Optional[str]
    edited_at: Optional[datetime]
    favourited: bool = False
    reblogged: bool = False
    muted: bool = False
    bookmarked: bool = False
    pinned: bool = False
    filtered: List[FilterResult]

    @property
    def original(self):
        return self.reblog or self


def from_dict(cls, data):
    def _fields():
        hints = typing.get_type_hints(cls)
        for field in dataclasses.fields(cls):
            default = field.default if field.default is not dataclasses.MISSING else None
            field_type = prune_optional(hints[field.name])
            value = data.get(field.name, default)
            yield convert(field_type, value)

    return cls(*_fields())


def convert(field_type, value):
    if value is None:
        return None

    if field_type in [str, int, bool, dict]:
        return value

    if field_type == datetime:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")

    if field_type == date:
        return date.fromisoformat(value)

    if get_origin(field_type) == list:
        (inner_type,) = get_args(field_type)
        return [convert(inner_type, x) for x in value]

    if is_dataclass(field_type):
        return from_dict(field_type, value)

    raise ValueError(f"Not implemented for type '{field_type}'")


def prune_optional(field_type):
    if get_origin(field_type) == typing.Union:
        args = get_args(field_type)
        if len(args) == 2 and args[1] == type(None):
            return args[0]

    return field_type
