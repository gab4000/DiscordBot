import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path="config")

default_intents = discord.Intents.default()
default_intents.members = True
bot = commands.Bot(command_prefix=".", description="Bot de test", intents=default_intents)


@bot.event
async def on_ready():
    print("Ready !")


@bot.event
async def on_member_join(member: discord.Member):
    general_channel: discord.TextChannel = bot.get_channel(985574330110971974)
    await general_channel.send(content=f"Bienvenue à {member.mention} sur le serveur !")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌  Commande introuvable !")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️  Il manque un argument !")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(":no_entry:️  Désolé, vous n'avez pas les permissions pour exécuter cette commande !")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌️  Désolé, je n'ai pas les permisions nécéssaires pour faire cette action !")


@bot.command()
async def getInfo(ctx, info):
    server = ctx.guild
    if info == "NombreMembres":
        await ctx.send("Il y a " + str(server.member_count) + " personnes sur ce serveur")
    elif info == "NombreSalons":
        await ctx.send(
            "Il y a " + str(len(server.voice_channels) + len(server.text_channels)) + " salons sur ce serveur")
    else:
        await ctx.send("Etrange... je ne connais pas cela")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    messages = await ctx.channel.history(limit=nombre + 1).flatten()
    for message in messages:
        await message.delete()


async def createMutedRole(ctx):
    mutedRole = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False, speak=False))
    for channel in ctx.guild.channels:
        await channel.set_permissions(mutedRole, send_messages=False, speak=False)
        return mutedRole


async def getMutedRole(ctx):
    roles = ctx.guild.roles
    for role in roles:
        if role.name == "Muted":
            return role
    await createMutedRole(ctx)


@bot.command()
@commands.has_role("Admin")
async def mute(ctx, member: discord.Member, *, reason="Aucune raison n'a été donnée"):
    mutedRole = await getMutedRole(ctx)
    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"🔇  L'utilisateur {member.mention} a été mute pour {reason} !")


@bot.command()
@commands.has_role("Admin")
async def unmute(ctx, member: discord.Member, *, reason="Aucune raison n'a été donnée"):
    mutedRole = await getMutedRole(ctx)
    await member.remove_roles(mutedRole, reason=reason)
    await ctx.send(f"🔈  L'utilisateur {member.mention} a été unmute pour {reason} !")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, reason="Aucune raison n'a été donnée"):
    bannedUsers = await ctx.guild.bans()
    for i in bannedUsers:
        if i.user == user:
            await ctx.guild.unban(i.user, reason=reason)
            await ctx.send(f"L'utilisateur {i.user.name} a bien été débanni pour **{reason}** !")
            return
    # ici l'user non trouvé
    await ctx.send(f"L'utilisateur {i.user.name} n'est pas trouvable dans la liste !")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, *, reason="Aucune raison n'a été donnée"):
    await ctx.guild.ban(user, reason=reason)
    embed = discord.Embed(title="**Banissement**", description="🔨  Un modérateur a frappé !", color=0xCA0000)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url="https://discordemoji.com/assets/emoji/BanneHammer.png")
    embed.add_field(name="Membre banni", value=user.name, inline=True)
    embed.add_field(name="Raison", value=reason, inline=True)

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason="Aucune raison n'a été donnée"):
        await user.kick(reason=reason)
        await ctx.send(f"L'utilisateur {user.mention} a bien été kick pour la raison : **{reason}** !")

@bot.command()
async def cuisine(ctx):
    await ctx.send("Envoyez le plat que vous voulez cuisiner !")

    def check_message(message):
        return message.author == ctx.message.author and ctx.message.channel == message.channel

    def check_reaction(reaction, user):
        return ctx.message.author == user and message.id == reaction.message.id and (
                    str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

    try:
        recette = await bot.wait_for("message", timeout=10, check=check_message)
    except:
        return

    message = await ctx.send(
        f"La préparation de la recette {recette.content} va commencer. Veuillez valider en réagissant avec ✅. Sinon, réagissez avec ❌.")
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=10, check=check_reaction)
        if reaction.emoji == "✅":
            await ctx.send(f"La recette {recette.content} a bien été lancée !")
        elif reaction.emoji == "❌":
            await ctx.send(f"La recette {recette.content} a été annulée !")
    except:
        await ctx.send(f"La recette {recette.content} a été annulée !")


@bot.command()
@commands.has_permissions(embed_links=True)
async def gif(ctx, gif: str):
    if gif.upper() == "BSOD":
        await ctx.send("https://thumbs.gfycat.com/UntriedWarlikeEasternglasslizard-size_restricted.gif")
    elif gif.upper() == "AH":
        await ctx.send("https://media.discordapp.net/attachments/958021659829342279/964825712425058324/AH.gif")
    elif gif.upper() == "AVION":
        await ctx.send("https://tenor.com/view/airplane-dancing-dance-dance-moves-dancing-airplane-gif-18115923")



bot.run(os.getenv("token"))
