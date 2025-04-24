import nextcord
from nextcord.ext import commands
from langdetect import detect
from db.MainDatabase import MainDatabase
from bot_utils.language import Language

class Listeners(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        self.config = config

        self.star_channel = self.config["star_channel"]

    async def star_embed(self, guild_id, channel_id, message_id, message, member):
        user = await self.bot.fetch_user(member)

        title = f"Starred message by {user}"

        url = f"https://discord.com/channels/{str(guild_id)}/{str(channel_id)}/{str(message_id)}"
        print(url)

        embed = nextcord.Embed(colour=nextcord.colour.Colour.yellow(), color=None, title=title, type='rich', url=url, description=message, timestamp=None)
        try:
            user = await self.bot.fetch_user(member)
            embed.set_thumbnail(url=str(user.avatar))
        except:
            pass
        return embed

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        if before.channel is None and after.channel is not None:
            print(f"{member.name} joined voice channel {after.channel.name}")

        elif before.channel is not None and after.channel is None:
            print(f"{member.name} left voice channel {before.channel.name}")

        elif before.channel != after.channel:
            print(f"{member.name} switched from {before.channel.name} to {after.channel.name}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if user.bot:
            return
        await self.db.set_reaction(reaction.message.id, user.id, reaction.message.author.id, reaction.emoji, True)
        is_starred_enough = await self.db.is_starred_enough(reaction.message.id)

        if is_starred_enough:
            is_in_db = await self.db.is_starred_message(reaction.message.id)

            if not is_in_db:
                await self.db.add_starred_message(reaction.message.id, reaction.message.author.id)
                channel = self.bot.get_channel(self.star_channel)
                embed = await self.star_embed(reaction.message.guild.id, reaction.message.channel.id, reaction.message.id, reaction.message.content, reaction.message.author.id)
                await channel.send(embed=embed)
            
        print(f"{user.name} reacted with {reaction.emoji} on message {reaction.message.id}")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if user.bot:
            return
        await self.db.set_reaction(reaction.message.id, user.id, reaction.message.author.id, reaction.emoji, False)
        print(f"{user.name} removed reaction {reaction.emoji} from message {reaction.message.id}")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Basic message statistics
        num_words = len(message.content.split())
        num_exclamations = message.content.count("!")
        num_questions = message.content.count("?")
        num_periods = message.content.count(".")

        language = Language()

        num_emojis = language.num_emojis(message.content)
        num_curse_words = language.num_curses(message.content)
        num_good_words = language.num_good(message.content)
        num_bad_words = language.num_bad(message.content)

        if num_words == 0:
            return

        lang = None
        reading_level = None
        dale_chall = None

        if num_words >= 3:
            try:
                lang = detect(message.content)
            except:
                pass
            
            try:
                if not language.is_gibberish(message.content):
                    reading_level = language.reading_level(message.content)
                    dale_chall = language.dale_chall(message.content)
                    print("Not gibberish")
            except:
                pass

        await self.db.add_message(message.author.id, message.channel.id, num_words, num_curse_words, num_questions, num_periods, num_exclamations, num_emojis, lang, reading_level, dale_chall)
        
        ze_credits = num_good_words-num_bad_words
        await self.db.add_credits(message.id, ze_credits)

        print(f"Processed message from {message.author}: {message.content}")

    async def cog_unload(self):
        await self.db.close()

