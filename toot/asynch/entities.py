import dacite
import typing

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from typing import get_origin, get_args


@dataclass(frozen=True)
class AccountField:
    """
    https://docs.joinmastodon.org/entities/Account/#Field
    """
    name: str
    value: str
    verified_at: Optional[datetime]


@dataclass(frozen=True)
class CustomEmoji:
    """
    https://docs.joinmastodon.org/entities/CustomEmoji/
    """
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: str


@dataclass(frozen=True)
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
    last_status_at: Optional[datetime]
    statuses_count: int
    followers_count: int
    following_count: int

    @classmethod
    def from_dict(cls, data: Dict) -> "Account":
        return dacite.from_dict(cls, data)


def from_dict(cls, data):
    for name, field in cls.__dataclass_fields__.items():
        print(name, prune_optional(field.type))


def prune_optional(field_type):
    if get_origin(field_type) == typing.Union:
        args = get_args(field_type)
        if len(args) == 2 and args[1] == type(None):
            return args[0]

    return field_type


if __name__ == '__main__':
    import json
    with open('acc.json') as f:
        data = json.load(f)
        # account = from_dict(Account, data)
        from_dict(AccountField, data["fields"][0])
