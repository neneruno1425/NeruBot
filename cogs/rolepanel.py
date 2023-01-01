from discord.ext import commands
import discord
from discord import option
import json

class rolepanel(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.Cog.listener()
    async def on_interaction(self,interaction):
        if not interaction.custom_id == None:
            if interaction.custom_id.startswith('rolepanel_'):
                role = discord.utils.get(interaction.guild.roles,id=int(interaction.custom_id.split('_')[1]))
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(f'{role.name}を剥奪しました。',ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f'{role.name}を付与しました。',ephemeral=True)
    @commands.slash_command()
    @discord.default_permissions(manage_roles=True)
    @option("role", description="ロール名を指定してください。ロールが複数の場合は,で区切ってください。")
    @option("paneltext", description="ロールパネルのテキストを指定してください。/embedで作ったjsonもロード可能です。")  
    async def rolepanel(self,ctx,role,paneltext):
        '''ロールパネルを作成できます。'''
        isembed = True
        try:
            paneltext = json.loads(paneltext)
        except:
            isembed = False
        view = discord.ui.View()
        for i in role.split(','):
            try:
                role = discord.utils.get(ctx.guild.roles, name=i)
                view.add_item(discord.ui.Button(label=role.name, style=discord.ButtonStyle.green, custom_id='rolepanel_' + str(role.id)))
            except:
                await ctx.send(f'{i}というロールは存在しません。',delete_after=5)
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
            await ctx.send(paneltext,view=view)
        await ctx.respond('作成しました。',ephemeral=True)

def setup(bot):
    bot.add_cog(rolepanel(bot))