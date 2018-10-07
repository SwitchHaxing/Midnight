#!/usr/bin/env python3

import discord
from discord.ext import commands
import sys
import os
import json

serials = {
    "XAW1": (78, 79, 100),
    "XAW4": (11, 12, 13),
    "XAW7": (17, 18, 19),
    "XAJ4": (52, 53, 60),
    "XAJ7": (42, 43, 50)
}

class Utility:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
    def find_user(self, user, ctx):
        found_member = self.bot.guild.get_member(user)
        if not found_member:
            found_member = self.bot.guild.get_member_named(user)
        if not found_member:
            try:
                found_member = ctx.message.mentions[0]
            except IndexError:
                pass
        if not found_member:
            return None
        else:
            return found_member
            
    @commands.command()
    async def restart(self, ctx):
        """Restarts the bot, obviously"""
        if ctx.author != ctx.guild.owner and ctx.author != self.bot.creator:
            return await ctx.send("You can't use this!")
        await ctx.send("Restarting...")
        with open("restart.txt", "w+") as f:
            f.write(str(ctx.message.channel.id))
            f.close()
        sys.exit(0)
            
    @commands.command(hidden=True, aliases=['game', 'music', 'watch'])
    async def playing(self, ctx, *, presence=""):
        """Changes the bot's activity.'"""
        await ctx.message.delete()
        if ctx.author != ctx.guild.owner and ctx.author != self.bot.creator:
            return await ctx.send("You can't use this!")
        if ctx.invoked_with == "playing":
            return await ctx.send("You can use 'music', 'game', or 'watch' to choose an activity for the bot.")
        elif ctx.invoked_with == "game":
            key = "game"
            game = discord.Game(name=presence)
            await self.bot.change_presence(activity=game)
            await ctx.send("Changed game status to `{}`!".format(presence))
        elif ctx.invoked_with == "music":
            key = "music"
            music = discord.Activity(name=presence, type=discord.ActivityType.listening)
            await self.bot.change_presence(activity=music)
            await ctx.send("Changed music status to `{}`!".format(presence))
        elif ctx.invoked_with == "watch":
            key = "watch"
            show = discord.Activity(name=presence, type=discord.ActivityType.watching)
            await self.bot.change_presence(activity=show)
            await ctx.send("Changed video status to `{}`!".format(presence))
        with open('saves/bot_status.json', 'r') as f:
            status = json.load(f)
        status["status"] = key
        status["presence"] = presence
        with open('saves/bot_status.json', 'w') as f:
            json.dump(status, f, indent=4)
            
    @commands.command()
    async def about(self, ctx):
        """Information about the bot"""
        await ctx.send("This is a bot coded in python for use in the SwitchHaxing server, made primarily by {}#{}. You can view the source code here: <https://github.com/GriffinG1/Midnight>.".format(self.bot.creator.name, self.bot.creator.discriminator))
        
    @commands.command(aliases=['mc'])
    async def membercount(self, ctx):
        """Returns number of people in server"""
        members = 0
        for user in ctx.guild.members:
            if not user.bot:
                members += 1
        await ctx.send("There are {} members on this server!".format(members))
        
    async def role_change(ctx, role, user):
        if not role in user.roles:
            await user.add_roles(role)
        else:
            await user.remove_roles(role)
            
    @commands.command(aliases=['tr'])
    async def togglerole(self, ctx, role=""):
        """Used to toggle roles. Available: Direct, Spoiler"""
        role = role.lower()
        found_member = ctx.message.author
        author_roles = found_member.roles[1:]
        if role == "direct":
            await self.role_change(self.bot.direct_role, found_member)
            await ctx.send("Toggled the Direct role!")
            await self.bot.log_channel.send("{}#{} toggled the Direct role.".format(found_member.name, found_member.discriminator))
        elif role == "spoiler" or role == "spoilers":
            await self.role_change(self.bot.spoiler_role, found_member)
            await ctx.send("Toggled the Spoiler role!")
            await self.bot.log_channel.send("{}#{} toggled the Spoiler role.".format(found_member.name, found_member.discriminator))
        else:
            return await ctx.send("You forgot to give an input, or gave an unrecognized input. Please try again. Available roles can be seed with `.help togglerole`")
            
    @commands.command(aliases=['ui', 'user'])
    async def userinfo(self, ctx, member=""):
        """Gets the userinfo for a given server member. If given no member, it will pull your own info."""
        if member:
            user = self.find_user(member, ctx)
            if not user:
                return await ctx.send("Could not find that user!")
        elif not member:
            user = ctx.author
        embed = discord.Embed(title="User info for {}".format(user))
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Username", value="{}".format(user.name))
        embed.add_field(name="Status", value="{}".format(str(user.status).capitalize()))
        if user.nick:
            embed.add_field(name="Nickname", value="{}".format(user.nick))
        if user.bot:
            embed.add_field(name="Bot", value="{}".format(user.bot))
        embed.add_field(name="ID", value="{}".format(user.id))
        embed.add_field(name="Highest Role", value="{}".format(user.top_role))
        embed.add_field(name="Joined At", value="{}".format(user.joined_at))
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['si', 'server'])
    async def serverinfo(self, ctx):
        """Returns info about SwitchHaxing"""
        embed = discord.Embed(title="Server information")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Guild name", value="{}".format(ctx.guild.name))
        embed.add_field(name="ID", value="{}".format(ctx.guild.id))
        embed.add_field(name="Members", value="{}".format(ctx.guild.member_count))
        embed.add_field(name="Roles", value="{}".format(len(ctx.guild.roles)))
        embed.add_field(name="Created at", value="{}".format(ctx.guild.created_at))
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['fwinfo', 'fi'])
    async def firmwareinfo(self, ctx, fw=""):
        """Returns firmware info for any released firmware in the database"""
        with open('saves/fwinfo.json', 'r') as f:
                firmware = json.load(f)
        if not fw:
            version = {}
            for i in firmware.keys():
                version[i.replace(".", "")] = i
            a = [int(i) for i in version.keys()]
            max_firm = firmware[version[str(max(a))]]
            embed = discord.Embed(title="Firmware info for version {}".format(version[str(max(a))]))
            embed.description = max_firm
            await ctx.send(embed=embed)
        else:
            if not fw in firmware.keys():
                return await ctx.send("Firmware isn't in database!")
            else:
                embed = discord.Embed(title="Firmware info for version {}".format(fw))
                embed.description = firmware[fw]
                await ctx.send(embed=embed)
            
    @commands.command(aliases=['listfw', 'lfw'])
    async def listfirmwares(self, ctx):
        """Lists all available firmwares"""
        with open('saves/fwinfo.json', 'r') as f:
            versionlist = json.load(f)
        embed = discord.Embed(title="Available firmwares", description="")
        version = {}
        for i in versionlist.keys():
            version[i.replace(".", "")] = i
        a = [int(i) for i in version.keys()]
        a.sort()
        for value in a:
            embed.description += "{}\n".format(version[str(value)])
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['sinfo'])
    async def serialinfo(self, ctx, str=""):
        """Allows a user to check if their switch is patched via serial code. Please input it with no hyphens or anything other than the serial code. Giving no input will show a guide on the patched serial codes"""
        await ctx.message.delete()
        if not str:
            embed = discord.Embed()
            embed.set_image(url="https://i.imgur.com/5yKNNme.png")
            return await ctx.send(embed=embed)
        elif len(str) < 8:
            return await ctx.send("Invalid input!")
        try:
            leading = str[:4]
            if leading == "XAJ1":
                return await ctx.send("Your Switch with leading characters `{}` and identifier `{}` is definitely unpatched! Congrats!".format(leading, stringIdentifier))
            stringIdentifier = str[4:8]
            identifier = int(stringIdentifier)
            low, mid, high = serials[leading]
            if identifier < low:
                return await ctx.send("Your Switch with leading characters `{}` and identifier `{}` is definitely unpatched! Congrats!".format(leading, stringIdentifier))
            elif mid < identifier < high:
                return await ctx.send("It is very likely your Switch with leading characters `{}` and identifier `{}` is patched.".format(leading, stringIdentifier))
            return await ctx.send("Your Switch with leading characters `{}` and identifier `{}` is definitely patched.".format(leading, stringIdentifier))
        except KeyError:
            return await ctx.send("Invalid input!")
    
def setup(bot):
    bot.add_cog(Utility(bot))
