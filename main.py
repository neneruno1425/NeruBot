import discord
import os
from dotenv import load_dotenv

load_dotenv()

intent = discord.Intents.all()
intent.message_content = True
bot = discord.Bot(intents=intent)

cogs = [
    'autopublish',
    'embedmaker',
    'music',
    'parser',
    'rolepanel',
    'ticket'
]
for i in cogs:
    bot.load_extension("cogs." + i)
    print(f'Loaded {i}!')

@bot.event
async def on_ready(): 
    print(f"Ready!")

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="エラーが発生しました。",description=f'エラーが発生しました。エラー内容:\n```py{error}```')
    await ctx.respond(embed=embed)

@bot.event
async def on_application_command_error(ctx, error):
    embed = discord.Embed(title="エラーが発生しました。",description=f'エラーが発生しました。エラー内容:\n```py{error}```')
    await ctx.respond(embed=embed)

bot.run(os.environ['token'])