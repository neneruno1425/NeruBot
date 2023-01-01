from discord.ext import commands
import discord
import tool
from discord.commands import SlashCommandGroup

class autopublish(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    autopublish = SlashCommandGroup("autopublish", "自動公開",default_member_permissions=discord.Permissions(manage_messages=True))
    @autopublish.command(description='自動公開をオンにします。')
    async def add(self,ctx):
        cfg = tool.loadcfg()
        if not ctx.channel.is_news():
            return await ctx.respond('ニュースチャンネルではありません。｀')
        cfg['autopublish'].append(str(ctx.channel.id))
        tool.savecfg(cfg)
        await ctx.respond('追加しました。')
    @autopublish.command(description='自動公開をオフにします。')
    async def remove(self,ctx):
        cfg = tool.loadcfg()
        if not str(ctx.channel.id) in cfg['autopublish']:
            return await ctx.respond('登録されていません。')
        cfg['autopublish'].remove(str(ctx.channel.id))
        tool.savecfg(cfg)
        await ctx.respond('削除しました。')
    @commands.Cog.listener()
    async def on_message(self,message):
        cfg = tool.loadcfg()
        if str(message.channel.id) in cfg['autopublish']:
            await message.publish()
def setup(bot):
    bot.add_cog(autopublish(bot))