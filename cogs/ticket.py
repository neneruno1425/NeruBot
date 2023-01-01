import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord import option
import json

class ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_interaction(self,interaction):
        if interaction.custom_id == 'ticket_create':
            await interaction.response.defer()
            created_channel = await interaction.channel.create_thread(name=f'{interaction.user.name}-ticket', message=None, type=discord.ChannelType.private_thread, reason=None)
            await created_channel.add_user(interaction.user)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label='押してクローズ', emoji='❎', style=discord.ButtonStyle.red, custom_id='ticket_close'))
            await created_channel.send(interaction.user.mention,view=view)
        if interaction.custom_id == 'ticket_close':
            await interaction.response.defer()
            await interaction.channel.delete()
    ticketcommand = SlashCommandGroup("ticket", "チケット",default_member_permissions=discord.Permissions(manage_messages=True))
    @ticketcommand.command()
    @option("boardtext", description="ボードのメッセージを指定してください。")  
    async def board(self,ctx,boardtext):
        '''チケットを作成できるボードを作成します。'''
        isembed = True
        try:
            paneltext = json.loads(boardtext)
        except:
            isembed = False
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='押して作成', emoji='🎫', style=discord.ButtonStyle.green, custom_id='ticket_create'))
        if isembed:
            embed = discord.Embed(title=paneltext['title'],description=paneltext['description'])    
            if 'color' in paneltext:
                embed.color = paneltext['color']
            if 'url' in paneltext:
                embed.url = paneltext['url']
            if 'footer' in paneltext:
                embed.set_footer(text=paneltext['footer'])
            if 'thumbnail' in paneltext:
                embed.set_thumbnail(url=paneltext['thumbnail'])
            for i in paneltext['fields']:
                s = list(i.items())[0]
                embed.add_field(name=s[0],value=s[1])
            await ctx.send(embed=embed,view=view)
        else:
            await ctx.send(boardtext,view=view)
        await ctx.respond('作成しました。',ephemeral=True)
    @ticketcommand.command()
    @option("user", description="チケットを作成するユーザーを指定してください。")  
    async def new(self,ctx,user: discord.User):
        '''特定のユーザーのチケットを作成します。'''
        created_channel = await ctx.channel.create_thread(name=f'{user.name}-ticket', message=None, type=discord.ChannelType.private_thread, reason=None)
        await created_channel.add_user(user)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label='押してクローズ', emoji='❎', style=discord.ButtonStyle.red, custom_id='ticket_close'))
        closemessage = await created_channel.send(user.mention,view=view)
        link_view = discord.ui.View()
        link2message = 'https://discord.com/channels/' + str(ctx.guild.id) + '/' + str(created_channel.id) + '/' + str(closemessage.id)
        link_view.add_item(discord.ui.Button(label='押して飛ぶ', url=link2message, style=discord.ButtonStyle.link))
        await ctx.respond('作成しました。',view=link_view,ephemeral=True)

def setup(bot):
    bot.add_cog(ticket(bot))