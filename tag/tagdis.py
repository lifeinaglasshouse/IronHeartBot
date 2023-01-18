import discord
from .tagobj import *

class TagUser(TagClass):
    NAME = "discord::user"
    
    def __init__(self, user: discord.User) -> None:
        super().__init__()
        self.user = user
    
    def get_attr(self, name: str) -> 'TagRef':
        if name == 'name':
            return TagStr(self.user.name)
        if name == 'id':
            return TagInt(self.user.id)
        if name == 'avatar':
            return TagStr(self.user.avatar.url)
        return super().get_attr(name)
    
    def has_attr(self, name: str) -> bool:
        if name in ('name', 'id', 'avatar'):
            return True
        return super().has_attr(name)

tag_usertype = TagType(TagUser)