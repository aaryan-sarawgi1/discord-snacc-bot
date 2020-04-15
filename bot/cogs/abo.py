import discord

from discord.ext import commands

from datetime import datetime

from bot.structures import ABOLeaderboard

from bot.common import (
	checks,
	utils
)

from bot.common import (
	AboSQL,
	RoleTags,
	IntegerRange,
	DBConnection,
)


class ABO(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return checks.author_has_tagged_role(ctx, RoleTags.ABO)

	@commands.command(name="me", help="Display stats")
	async def get_stats(self, ctx: commands.Context):
		""" Show your last recorded ABO stats """
		with DBConnection() as con:
			con.cur.execute(AboSQL.SELECT_USER, (ctx.author.id,))

			user = con.cur.fetchone()

		if user is None:
			return await ctx.send(f"**{ctx.author.display_name}**, I found no stats for you")

		embed = self.bot.create_embed(title=ctx.author.display_name, thumbnail=ctx.author.avatar_url)
		text = f":joystick: **{user.lvl}**\n:trophy: **{user.trophies:,}**"

		embed.add_field(name="ABO Stats", value=text)

		return await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], usage="<level> <trophies>")
	async def set_stats(self, ctx, level: IntegerRange(0, 150), trophies: IntegerRange(0, 5000)):
		""" Set your ABO stats, which are visible on the leaderboard """
		with DBConnection() as con:
			params = (ctx.author.id, level, trophies, datetime.now())

			con.cur.execute(AboSQL.UPDATE, params)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@checks.author_has_tagged_role(tag=RoleTags.LEADER)
	@commands.command(name="setuser", aliases=["su"], usage="<user> <level> <trophies>")
	async def set_user(self, ctx, user: discord.Member, level: IntegerRange(0, 150), trophies: IntegerRange(0, 5000)):
		""" Set another members ABO stats """
		with DBConnection() as con:
			params = (user.id, level, trophies, datetime.now())

			con.cur.execute(AboSQL.UPDATE, params)

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@checks.author_has_tagged_role(tag=RoleTags.LEADER)
	@commands.command(name="shame", help="Shame others")
	async def shame(self, ctx: commands.Context):
		""" Mention everyone who has not updated their stats in the last 7 days """
		member_role = utils.get_tagged_role(self.bot.svr_cache, ctx.guild, RoleTags.ABO)

		with DBConnection() as con:
			con.cur.execute(AboSQL.SELECT_ALL)

			all_data = con.cur.fetchall()

		msg = "**__Lacking Activity__**\n"

		for user in all_data:
			member = ctx.guild.get_member(user.userid)

			days_since_update = (datetime.now() - user.dateset).days

			if member is not None and days_since_update >= 7 and member_role in member.roles:
				msg += f"{member.mention} ({days_since_update}) | "

		return await ctx.send(msg)

	@commands.command(name="alb", help="Leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		""" Show the trophy leaderboard for the ABO game """
		if self.leaderboards.get(ctx.guild.id, None) is None:
			self.leaderboards[ctx.guild.id] = ABOLeaderboard(ctx.guild, self.bot)

		lb = self.leaderboards[ctx.guild.id]

		return await ctx.send(lb.get(ctx.author))


def setup(bot):
	bot.add_cog(ABO(bot))
