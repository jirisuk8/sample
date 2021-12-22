# coding=utf-8

from typing import Set, Dict
from math import floor

from xxx.api import API
from xxx.entities import Pair
from xxx.api.binance import BinanceAPI
from xxx.order_book import OrderBook


class Trader:
    """
    Trading class
    """

    def __init__(self, api: API, order_books: Set[OrderBook]):
        self._api = api
        self.order_books = order_books

    @staticmethod
    def round_down(n: float, decimals: int) -> float:
        """
        Floors float to certain number of decimals

        :param n: float number
        :param decimals: number of decimals
        :return: float floored to to the certain number of decimals
        """
        multiplier = 10 ** decimals
        return floor(n * multiplier) / multiplier

    @staticmethod
    def previous_trade_fills_buy(trade_buy: Dict) -> float:
        """
        Calculates volume to be operated in the next step after buy order

        :param trade_buy: object returned by api after buy order
        :return: float sum of bought asset
        """
        return sum([(float(fill['qty'])) for fill in trade_buy['fills']])

    @staticmethod
    def previous_trade_fills_sell(trade_sell: Dict) -> float:
        """
        Calculates volume to be operated in the next step after sell order

        :param trade_sell: object returned by api after buy order
        :return: float sum of bought asset
        """
        return sum([(float(fill['qty']) * float(fill['price'])) for fill in trade_sell['fills']])

    def search_pair(self, coin_a: str, coin_b: str) -> Pair:
        """
        Method returns a Pair object from order books, order does not matter

        :param coin_a: First coin
        :param coin_b: Second coin
        :return: market pair
        """
        for ob in self.order_books:
            if (ob.pair.base == coin_a and ob.pair.quote == coin_b) or \
                    (ob.pair.quote == coin_a and ob.pair.base == coin_b):
                return ob.pair
        else:
            raise RuntimeError('Pair does not have its order book.')

    def trade(self, symbol: tuple, volume: float) -> None:
        """
        Method performing trade

        :param symbol: tuple representing trading symbol
        :param volume: volume of asset
        :return: None
        """

        # Checking if corresponding order book exist
        pair = self.search_pair(symbol[0], symbol[1])

        # SELL SIDE
        if symbol[0] == pair.base:
            try:
                # Selling a volume of first coin to sold in order to get certain volume of second coin
                sell_volume = self.round_down(volume, pair.decimals)
                order = self._api.market_order_sell(str(pair), sell_volume)
                final_volume = self.previous_trade_fills_sell(order)
                print(f"Sold {sell_volume} {str(pair.base)} and got {final_volume} {str(pair.quote)}")

            except Exception as e:
                print(f'Error {e} was caught while attempting to sell {str(pair.base)} at {symbol} market order')

        # BUY SIDE
        else:
            try:
                # Buying a volume of the second coin
                buy_volume_spent_quote = self.round_down(volume, pair.quote_precision)
                order = self._api.market_order_buy(str(pair), buy_volume_spent_quote)
                final_volume = self.previous_trade_fills_buy(order)
                print(f"Bought {final_volume} {str(pair.base)} for max {buy_volume_spent_quote} {str(pair.quote)}")

            except Exception as e:
                print(f'Error {e} was caught while attempting to buy {str(pair.quote)} at {symbol} market order')

        return None

