from discord.ext import commands

from snacc.common import MAIN_SERVER

USEFUL_LINKS_EMBED = 708435677511155782
USEFUL_LINKS_CHANNEL = 666738997468332032


class UsefulLinks(commands.Cog, name="Useful Links"):
	""" Set of commands to update the useful links Embed. """

	async def cog_check(self, ctx):
		return ctx.guild.id == MAIN_SERVER and ctx.author.guild_permissions.administrator

	@commands.command(name="addlink")
	async def add_useful_link(self, ctx, index: int, name: str, value: str):
		""" [Admin] Add a new field to the useful link embed. """

		channel = ctx.bot.get_channel(USEFUL_LINKS_CHANNEL)
		message = await channel.fetch_message(USEFUL_LINKS_EMBED)

		embed = message.pages[0]

		embed.insert_field_at(index, name=name, value=value)

		await message.edit(embed=embed)
		await ctx.send(f"Added the field.")

	@commands.command(name="rmlink")
	async def remove_useful_link(self, ctx, index: int):
		""" [Admin] Remove a field from the useful link embed. """

		channel = ctx.bot.get_channel(USEFUL_LINKS_CHANNEL)
		message = await channel.fetch_message(USEFUL_LINKS_EMBED)

		embed = message.pages[0]

		embed.remove_field(index)

		await message.edit(embed=embed)
		await ctx.send(f"Removed the field.")


def setup(bot):
	bot.add_cog(UsefulLinks())
