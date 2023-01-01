import discord
import typing
import wavelink
from discord.ext import commands
from discord.commands import SlashCommandGroup

class Music(commands.Cog,description='音楽などのコマンドです。'):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="lava.link", port="80", password="dismusic")

    greetings = SlashCommandGroup("music", "music command")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc: player = ctx.voice_client

        if vc.loop:
            return await vc.play(track)
        
        if vc.queue.is_empty:
            return await ctx.respond("再生できるものがありません。")
        
        next_song = vc.queue.get()
        song = await wavelink.YouTubeTrack.search(query=str(next_song), return_first=True)
        if not song.uri == None:
                ur = song.uri
        else:
            ur = "None"
        if not song.author == None:
            au = song.author
        else:
            au = "None"
        if song.is_stream():
            stream = "True"
        else:
            stream = "False"
        await vc.play(song)
        embed = discord.Embed(title=f"`{song.title}`を再生しています。", description=f"Info:\n長さ, {song.duration}\nAuthor, {au}\リンク, {ur}\nライブ, {stream}", color=discord.Color.blue())
        await ctx.respond(embed=embed)

    @greetings.command(name="join", aliases=["connect", "summon"], description="ボイスチャットに参加します。")
    async def join_commad(self, ctx, channel: typing.Optional[discord.VoiceChannel]):
        try:
            if channel is None:
                channel = ctx.author.voice.channel
            
            node = wavelink.NodePool.get_node()
            player = node.get_player(ctx.guild)

            if player is not None:
                if player.is_connected():
                    return await ctx.respond("すでにボイスチャットに参加しています。")
            
            await channel.connect(cls=wavelink.Player)
            embed = discord.Embed(title=f"{channel.name}に接続しました。", color=discord.Color.from_rgb(255, 255, 255))
            await ctx.respond(embed=embed)
        except AttributeError:
            await ctx.respond("あなたがボイスチャットにいません。")

    @greetings.command(name="leave", aliases=["disconnect", "quit"], description="ボイスチャットから切断します。")
    async def leave_command(self, ctx):

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.respond("ボットがボイスチャットに参加していません。")
        vc: wavelink.Player = ctx.voice_client
        if vc.is_playing():
            return await ctx.respond("音楽を再生中なので切断できません。stopコマンドを使用してください。")

        await player.disconnect()
        embed=discord.Embed(title="切断しました。", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.respond(embed=embed)
    
    @greetings.command(name="play", description="音楽を再生します。")
    async def play_command(self, ctx, *, search: str):
        await ctx.defer()
        try:
            if not ctx.author.voice:
                return await ctx.respond("ボイスチャットに参加してください。")
            song = await wavelink.YouTubeTrack.search(query=search, return_first=True)
            
            if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            else:
                vc: wavelink.Player = ctx.voice_client
            
            if vc.queue.is_empty and not vc.is_playing():
                await vc.play(song)
                if not song.uri == None:
                    ur = song.uri
                else:
                    ur = "None"
                if not song.author == None:
                    au = song.author
                else:
                    au = "None"
                if song.is_stream():
                    stream = "True"
                else:
                    stream = "False"
                embed = discord.Embed(title=f"`{song.title}`を再生しています。", description=f"Info:\n長さ, {song.duration}\n投稿者, {au}\nリンク, {ur}\nライブ, {stream}", color=discord.Color.from_rgb(255, 255, 255))
            else:
                await vc.queue.put_wait(song)
                embed = discord.Embed(title=f"`{song}`をキューに追加しました。", color=discord.Color.from_rgb(255, 255, 255))
            
            vc.ctx = ctx
            setattr(vc, "loop", False)
            await ctx.respond(embed=embed)
        except Exception as e:
            if e == 'Invalid response from Lavalink server.':
                await ctx.respond('該当する動画が見つかりませんでした。リンクを入力してもう一度お試しください。')
            else:
                await ctx.respond(f'エラーが発生しました。もう一度お試しください。{e}')

    @greetings.command(name="overrideplay", description="音楽をキューに追加せずに流します。")
    async def overrideplay_command(self, ctx, *, search: str):
        await ctx.defer()
        if not ctx.author.voice:
            return await ctx.respond("ボイスチャンネルに参加してください。")
        song = await wavelink.YouTubeTrack.search(query=search, return_first=True)
        
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            await vc.play(song)
            if not song.uri == None:
                ur = song.uri
            else:
                ur = "None"
            if not song.author == None:
                au = song.author
            else:
                au = "None"
            if song.is_stream():
                stream = "True"
            else:
                stream = "False"
            embed = discord.Embed(title=f"`{song.title}`を再生しています。", description=f"Info:\n長さ, {song.duration}\n投稿者, {au}\nリンク, {ur}\nライブ, {stream}", color=discord.Color.from_rgb(255, 255, 255))
        else:
            await ctx.respond("キューが空ではないのでコマンドを使用できません。")
        await ctx.respond(embed=embed)
        vc.ctx = ctx
        setattr(vc, "loop", False)
    
    @greetings.command(name="stop", description="音楽を止めます。")
    async def stop_command(self, ctx):
        try:


                node = wavelink.NodePool.get_node()
                player = node.get_player(ctx.guild)

                if player is None:
                    return await ctx.respond("ボットがボイスチャンネルに参加していません。")
                else:
                    vc: wavelink.Player = ctx.voice_client
                
                if player.is_playing:
                    if not vc.loop:
                        if not vc.queue.is_empty:
                            vc.queue.clear()
                            await player.stop()
                        else:
                            await player.stop()
                        embed=discord.Embed(title="ストップしました。", color=discord.Color.from_rgb(255, 255, 255))
                        return await ctx.respond(embed=embed)
                    else:
                        return await ctx.respond("ループがオンです。オフにして再度実行してください。")
                else:
                    return await ctx.respond("何も再生されていません。")

        except Exception as e:
            print(e)

    @greetings.command(name="skip", description="音楽をスキップできます。")
    async def skip_command(self, ctx):
        node = wavelink.NodePool.get_node()
        vc: wavelink.Player = ctx.voice_client
        if vc.is_playing:
            await vc.stop()
            embed=discord.Embed(title="スキップしました。", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.respond(embed=embed)
        else:
            return await ctx.respond("何も再生されていません。")

    @greetings.command(name="pause", description="音楽を一時停止します。")
    async def pause_command(self, ctx):

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.respond("ボットがボイスチャンネルに参加していません。")
        
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                embed = discord.Embed(title="一時停止しました。", color=discord.Color.from_rgb(255, 255, 255))
                return await ctx.respond(embed=embed)
            else:
                return await ctx.respond("何も再生されていません。")
        else:
            return await ctx.respond("すでに停止されています。")
    
    @greetings.command(name="resume", aliases=["continue"], description="音楽が一時停止されている場合、再開します。")
    async def resume_command(self, ctx):
        await ctx.defer()
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.respond("ボットがボイスチャンネルに参加していません。")
        
        if player.is_paused():
            await player.resume()
            embed = discord.Embed(title="再開しました。", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.respond(embed=embed)
        else:
            return await ctx.respond("一時停止されていません。")

    @greetings.command(name="volume", description="1から100の間で音量を調節します。")
    async def volume_command(self, ctx, to:int):
        await ctx.defer()
        if not ctx.voice_client:
            return await ctx.respond("ボイスチャンネルに参加していません。")
        if to > 100:
            return await ctx.respond("音量は1から100の間で指定できます。")
        elif to < 1:
            return await ctx.respond("音量は1から100の間で指定できます。")
        
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        await player.set_volume(to)
        embed = discord.Embed(title=f"音量を{to}に変更しました。", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.respond(embed=embed)
    
    @greetings.command(name="loop", description="音楽をループします。")
    async def loop_command(self, ctx):

        if not ctx.voice_client:
            return await ctx.respond("ボットがボイスチャンネルに参加していません。")
        elif not ctx.author.voice:
            return await ctx.respond("あなたがボイスチャンネルに参加していません。")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.loop == False:
            vc.loop = True
        else:
            setattr(vc, "loop", False)
        
        if vc.loop:
            return await ctx.respond("ループがオンになりました。")
        else:
            return await ctx.respond("ループがオフになりました。")

    @greetings.command(name="queue", description="キューを表示します。")
    async def queue_command(self, ctx):
        if not ctx.voice_client:
            return await ctx.respond("ボットがボイスチャンネルに参加していません。")
        elif not ctx.author.voice:
            return await ctx.respond("あなたがボイスチャンネルに参加していません。")
        else:
            vc: wavelink.Player = ctx.voice_client

        if vc.queue.is_empty:
            return await ctx.respond("キューが空です。")
        
        embed = discord.Embed(title="キュー", color=discord.Color.from_rgb(255, 255, 255))
        queue = vc.queue.copy()
        song_count = 0
        for song in queue:
            song_count += 1
            embed.add_field(name=f"曲 {song_count}", value=f"`{song}`")

        return await ctx.respond(embed=embed)

def setup(bot):
  bot.add_cog(Music(bot))