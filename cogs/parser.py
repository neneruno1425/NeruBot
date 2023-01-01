from discord.ext import commands
import discord

class parser(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.content.startswith('https://discord.com/channels/') or message.content.startswith('https://canary.discord.com/channels/') or message.content.startswith('https://ptb.discord.com/channels/'):
            if len(message.content.split('/')) ==  7:
                msgchannel = self.bot.get_channel(int(message.content.split('/')[5]))
                msg = await msgchannel.fetch_message(int(message.content.split('/')[6]))
                embed=discord.Embed(title=msg.content,color=0x36393f)
                embed.set_author(name=msg.author.name, icon_url=msg.author.avatar.url)
                embed.set_footer(text=msg.created_at)
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label='メッセージへ', url=msg.jump_url, style=discord.ButtonStyle.link))
                await message.channel.send(embed=embed,view=view)
def setup(bot):
    bot.add_cog(parser(bot))