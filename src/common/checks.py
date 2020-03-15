

import discord
import random

from discord.ext import commands
from discord.ext.commands import CommandError

from src.common import FileReader


def requires_channel_tag(tag):
	async def predicate(ctx):
		with FileReader("server_settings.json") as server_settings:
			channels = server_settings.get_inner_key((str(ctx.guild.id)), "channels", {})

		if ctx.channel.id not in channels.get(tag, []):
			raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

		return True

	return predicate


async def is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True


async def has_member_role(ctx):
	with FileReader("server_settings.json") as server_settings:
		role = server_settings.get_inner_key(str(ctx.guild.id), "roles", {}).get("member", None)

	member_role = discord.utils.get(ctx.guild.roles, id=role)

	if member_role is None:
		raise CommandError("Member role is invalid or has not been set")

	elif member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{member_role.name}** role.")

	return True


def has_minimum_coins(file, amount):
	async def predicate(ctx):
		with FileReader(file) as f:
			balance = f.get_inner_key(str(ctx.author.id), "coins", 0)

		if balance < amount:
			raise CommandError(f"**{ctx.author.display_name}** you do you not enough coins to do that :frowning:")

		return True

	return commands.check(predicate)
