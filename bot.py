import os
import numpy as np
import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import yahoofinancials as yfs
from yahoofinancials import YahooFinancials
import alpaca_trade_api as tradeapi
alpaca_endpoint = 'https://paper-api.alpaca.markets'

TOKEN = 'bot_token'

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(
        f'{bot.user.name} is connected to discord'
    )

@bot.command(name='buy', help='buys stocks')
async def buy(ctx, symbol: str, qty: int):
    pb = pythonBuyBot()
    response = pb.buyOrder(symbol, qty, 'buy')
    await ctx.send(response)
    await ctx.send(file=discord.File('plot.png'))
    os.remove('plot.png')

@bot.command(name='sell', help='sells stocks')
async def sell(ctx, symbol: str, qty: int):
    pb = pythonBuyBot()
    response = pb.sellOrder(symbol, qty, 'sell')
    await ctx.send(response)

@bot.command(name='progress', help='check balance change from last market close')
async def progress(ctx):
    pb = pythonBuyBot()
    response = pb.progress()
    await ctx.send(response)

@bot.command(name='balance', help='check current balance')
async def balance(ctx):
    pb = pythonBuyBot()
    response = pb.balance()
    await ctx.send(response)

@bot.command(name='history', help='displays list of past orders')
async def history(ctx):
    pb = pythonBuyBot()
    #print out array problem
    await ctx.send(pb.orderHistory())


class pythonBuyBot():
    def __init__(self):
        self.alpaca = tradeapi.REST('APCA_API_KEY_ID','APCA_API_SECRET_KEY', alpaca_endpoint)
        self.stockUniverse = ['DOMO', 'TLRY', 'SQ', 'MRO', 'AAPL', 'GM', 
                'SNAP', 'SHOP', 'SPLK', 'BA', 'AMZN', 'SUI', 
                'SUN', 'TSLA', 'CGC', 'SPWR', 'NIO', 'CAT', 
                'MSFT', 'PANW', 'OKTA', 'TWTR', 'TM', 'RTN', 
                'ATVI', 'GS', 'BAC', 'MS', 'TWLO', 'QCOM']

    def balance(self):
        account = self.alpaca.get_account()

        curr = float(account.equity)
        response = f'Current Balance: ${curr}'
        return response

    def progress(self):
        account = self.alpaca.get_account()

        balance_change = float(account.equity) - float(account.last_equity)
        response = f'Today\'s portfolio balance change: ${balance_change}'
        return response

    def buyOrder(self, symbol, qty, side):
        try:
            yfs = YahooFinancials(symbol)

            if qty!=0:
                self.alpaca.submit_order(symbol, qty, side, "market", "gtc")
                response = f'Market order to {str(side)} {str(qty)} shares of {symbol} placed for ${str(yfs.get_current_price())}'
            else:
                response = f'Share quantity is 0: Market order to {str(side)} {str(qty)} shares of {symbol} unfulfilled.'
            
            bar = self.alpaca.get_barset(symbol, 'day', limit=5)
            day1_close = bar[symbol][0].c
            day2_close = bar[symbol][1].c
            day3_close = bar[symbol][2].c
            day4_close = bar[symbol][3].c
            day5_close = bar[symbol][4].c

            xList = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
            yList = [day1_close, day2_close, day3_close, day4_close, day5_close]

            xList.sort()
            yList.sort()
            x = np.array(xList)
            y = np.array(yList)
            arr = np.vstack((x, y))

            plt.clf()
            plt.plot(arr[0], arr[1])
            plt.title(f'{symbol} Previous Closes')
            plt.savefig(fname='plot')

        except:
            response = "Error Occurred, please make sure you have entered valid input."
        return response

    def sellOrder(self, symbol, qty, side):
        try:
            yfs = YahooFinancials(symbol)

            if qty!=0:
                self.alpaca.submit_order(symbol, qty, side, "market", "gtc")
                response = f'Market order to {str(side)} {str(qty)} shares of {symbol} placed for ${str(yfs.get_current_price())}'
            else:
                response = f'Share quantity is 0: Market order to {str(side)} {str(qty)} shares of {symbol} unfulfilled.'
        except:
            response = f'Error: Market order to {str(side)} {str(qty)} shares of {symbol} unfulfilled. Please check you have entered valid input.'
            
        return response

    def orderHistory(self):
        closed_orders = self.alpaca.list_orders(
            status='closed',
            limit=100,
            nested=True  # show nested multi-leg orders
        )
        return closed_orders

bot.run(TOKEN)