import random
import typing
import secrets

from bot import utils

from discord.ext import commands

from bot.common.emoji import SEmoji
from bot.common.queries import BankSQL
from bot.common.converters import Range, CoinSide


class Gambling(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="slot")
	async def slot_machine(self, ctx, bet: Range(0, 50_000) = 0):
		""" Use a slot machine. """

		bal = await utils.bank.get_author_bal(ctx)

		if bal["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		items = [
			SEmoji.APPLE, SEmoji.PINEAPPLE, SEmoji.STRAWBERRY,
			SEmoji.GRAPES, SEmoji.CHERRIES, SEmoji.WATERMELON,
			SEmoji.KIWI, SEmoji.LEMON
		]

		row = None

		# Animation
		for i in range(3):
			row = [secrets.choice(items) for _ in range(3)]

			if row[0] == row[1]:
				break

		won = True

		# Calculate winnings
		if row[0] == row[1] == row[2]:
			winnings = int(bet * 5.0)

		elif row[0] == row[1]:
			winnings = int(bet * 2.5)

		else:
			won, winnings = False, 0

		if won:
			if winnings > 0:
				await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

			await ctx.send(content=f"**[{''.join(row)}]** You won **${winnings:,}**!")

		else:
			if bet > 0:
				await self.bot.pool.execute(BankSQL.SUB_MONEY, ctx.author.id, bet)

			await ctx.send(content=f"**[{''.join(row)}]** You won nothing. Better luck next time!")

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="flip")
	async def flip(self, ctx, side: typing.Optional[CoinSide] = "heads", bet: Range(0, 50_000) = 0):
		""" Flip a coin and bet on which side it lands on. """

		bal = await utils.bank.get_author_bal(ctx)

		if bal["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		side_landed = secrets.choice(["heads", "tails"])
		correct_side = side_landed == side

		winnings = bet if correct_side else bet * -1

		if winnings != 0:
			await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(
			f"It's **{side_landed}**! "
			f"You {'won' if correct_side else 'lost'} **${abs(winnings):,}**!"
		)

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="lucky")
	async def lucky(self, ctx):
		""" Are you lucky enough to win? """

		def get_winning(amount) -> int:
			low, high = max(amount * -0.75, -750), min(amount * 2.0, 1000)

			return random.randint(int(low), int(high))

		bal = await utils.bank.get_author_bal(ctx)

		winnings = get_winning(bal["money"])

		await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(
			f"**{'Unlucky' if winnings < 0 else 'Lucky'}**! "
			f"You {'won' if winnings > 0 else 'lost'} **${abs(winnings):,}**!"
		)

	@commands.cooldown(1, 3, commands.BucketType.user)
	@commands.command(name="bet")
	async def bet(self, ctx, bet: Range(0, 50_000) = 0, sides: Range(6, 100) = 6, side: Range(6, 100) = 6):
		""" Roll a die and bet on which side the die lands on. """

		bal = await utils.bank.get_author_bal(ctx)

		if bal["money"] < bet:
			raise commands.CommandError("You do not have enough money.")

		elif side > sides:
			raise commands.CommandError("You made an impossible to win bet.")

		side_landed = random.randint(1, sides)
		correct_side = side_landed == side

		winnings = bet * (sides - 1) if correct_side else bet * -1

		if winnings != 0:
			await self.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, winnings)

		await ctx.send(
			f":1234: You {'won' if correct_side else 'lost'} **${abs(winnings):,}**! "
			f"The dice landed on `{side_landed}`"
		)




def setup(bot):
	bot.add_cog(Gambling(bot))
