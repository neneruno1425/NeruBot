from discord.ext import commands
import discord
import json
from discord import option
from discord.commands import SlashCommandGroup

class embedmaker(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    embedslash = SlashCommandGroup("embed", "埋め込み",default_member_permissions=discord.Permissions(manage_messages=True))
    @embedslash.command()
    @option("title", description="埋め込みのタイトルを指定してください。")
    @option("description", description="埋め込みの説明を指定してください。")
    @option("link", description="リンクを指定できます。httpまたはhttpsから始めてください。")
    @option("color", description="HEXで指定してください。カラーピッカーはgoogleなどで調べると使えます。")
    @option("thumbnail", description="埋め込みの画像のリンクを指定してください。画像をアップロードしてから、元ファイルを開くのリンクを使うと良いです。")
    @option("footer", description="フッター（下の小さい文字）を指定できます。")
    async def make(self,ctx,title,description,link=None,color=None,thumbnail=None,footer=None):
        '''埋め込みを作成できます。'''
        embed = discord.Embed(title=title, description=description)
        if color is not None:
            color = int(color.replace('#',''),16)
            embed.color = color
        if link is not None:
            embed.url = link
        if footer is not None:
            embed.set_footer(text=footer)
        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)
        class newfield(discord.ui.Modal):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                self.add_item(discord.ui.InputText(label="名前"))
                self.add_item(discord.ui.InputText(label="値", style=discord.InputTextStyle.long))
            async def callback(self, interaction: discord.Interaction):
                newembed = editembed.embeds[0]
                newembed.add_field(name=self.children[0].value, value=self.children[1].value, inline=False)
                await editembed.edit(embed=newembed)
                await interaction.response.defer()
        class controlpanel(discord.ui.View):
            @discord.ui.button(label="フィールドを追加")
            async def newfield_callback(self, button, interaction):
                await interaction.response.send_modal(newfield(title="フィールドを追加"))
            # @discord.ui.button(label="完了")
            # async def done_callback(self, button, interaction):
            #     await ctx.send(embed=editembed.embeds[0])
            #     await editembed.delete()
            @discord.ui.button(label="エクスポート")
            async def export_callback(self, button, interaction):
                jsonconst = {}
                jsonconst['title'] = editembed.embeds[0].title
                jsonconst['description'] = editembed.embeds[0].description
                if color is not None:
                    jsonconst['color'] = editembed.embeds[0].colour.value
                if link is not None:
                    jsonconst['url'] = editembed.embeds[0].url
                if footer is not None:
                    jsonconst['footer'] = editembed.embeds[0].footer.text
                if thumbnail is not None:
                    jsonconst['thumbnail'] = editembed.embeds[0].thumbnail.url
                fieldforjson = list()
                for i in editembed.embeds[0].fields:
                    jsonconst_field = {}
                    jsonconst_field[i.name] = i.value
                    fieldforjson.append(jsonconst_field)
                jsonconst['fields'] = fieldforjson
                exportedjson = json.dumps(jsonconst, ensure_ascii=False)
                await ctx.send(exportedjson.replace('\n',''))
                await editembed.delete()
        editembed = await ctx.send(embed=embed,view=controlpanel())
        await ctx.respond('埋め込みを作成しました。',ephemeral=True)
    @embedslash.command()
    @option("embedjson", description="エクスポートした埋め込みを指定してください。")
    async def load(self,ctx,embedjson):
        '''エクスポートした埋め込みをロードします。'''
        embedjson = json.loads(embedjson)
        embed = discord.Embed(title=embedjson['title'],description=embedjson['description'])
        if 'color' in embedjson:
            embed.color = embedjson['color']
        if 'url' in embedjson:
            embed.url = embedjson['url']
        if 'footer' in embedjson:
            embed.set_footer(text=embedjson['footer'])
        if 'thumbnail' in embedjson:
            embed.set_thumbnail(url=embedjson['thumbnail'])
        for i in embedjson['fields']:
            s = list(i.items())[0]
            embed.add_field(name=s[0],value=s[1])
        await ctx.send(embed=embed)
        await ctx.respond('ロードしました。',ephemeral=True)
def setup(bot):
    bot.add_cog(embedmaker(bot))