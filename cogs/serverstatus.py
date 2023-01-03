from discord.ext import commands
import discord
import tool
from discord.commands import SlashCommandGroup
from discord import option

class serverstatus(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    serverstatusgroup = SlashCommandGroup("serverstatus", "サーバーステータス",default_member_permissions=discord.Permissions(manage_guild=True))
    @serverstatusgroup.command()
    @option("channel", description="名前を変更したいチャンネルを指定してください。")
    @option("name", description="変更したい名前を入力してください。{member}と入力することでメンバー数を入力できます。")
    async def add(self,ctx,channel:discord.VoiceChannel,name):
        '''サーバーの人数をチャンネル名に設定できます。'''
        cfg = tool.loadcfg()
        cfg['serverstatus'][ctx.guild.id] = {"name":name,"channel":channel.id}
        tool.savecfg(cfg)
        await channel.edit(name=name.replace('{member}',str(len(ctx.guild.members))))
        await ctx.respond('保存しました。')
    @serverstatusgroup.command()
    async def remove(self,ctx):
        '''設定を削除できます。'''
        cfg = tool.loadcfg()
        cfg['serverstatus'].pop(str(ctx.guild.id))
        tool.savecfg(cfg)
        await ctx.respond('削除しました。')
    @commands.Cog.listener()
    async def on_member_join(self,member):
        cfg = tool.loadcfg()
        if not cfg['serverstatus'].get(str(member.guild.id)) == None:
            channel = member.guild.get_channel(cfg['serverstatus'][str(member.guild.id)]['channel'])
            await channel.edit(name=cfg['serverstatus'][str(member.guild.id)]['name'].replace('{member}',str(len(member.guild.members))))
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        cfg = tool.loadcfg()
        if not cfg['serverstatus'].get(str(member.guild.id)) == None:
            channel = member.guild.get_channel(cfg['serverstatus'][str(member.guild.id)]['channel'])
            await channel.edit(name=cfg['serverstatus'][str(member.guild.id)]['name'].replace('{member}',str(len(member.guild.members))))
def setup(bot):
    bot.add_cog(serverstatus(bot))