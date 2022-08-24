import argparse
import csv
import fileinput
import sys

from pycoingecko import CoinGeckoAPI
from rich import box
from rich.console import Console
from rich.table import Table

# Uses a cached version of coins list to validate coins to reduce API calls and avoid rate limiting.
import json
cfile = open("coins.json")
data = json.load(cfile)

# Remove the hash in line 17 to enable dynamic coin list fetching
#data = cg.get_coins_list()

# Creates file "portfolio.csv" if it doesn't exist
with open("portfolio.csv", "a") as file:
    pass

port = "portfolio.csv"
cg = CoinGeckoAPI()

class Portfolio:

    # Validates coins input to make sure that they are real cryptocurrencies, uses list of coins from CoinGecko
    def validate_coin(self, asset):
        for coin in range(len(data)):
            if data[coin]["symbol"] == asset:
                return asset
        sys.exit("Invalid asset")

    def coin_name(self, asset):
        for coin in range(len(data)):
            if data[coin]["symbol"] == asset:
                return data[coin]["name"]

    def coin_sym(self, asset):
        for coin in range(len(data)):
            if data[coin]["symbol"] == asset:
                return data[coin]["symbol"]

    def coin_id(self, asset):
        for coin in range(len(data)):
            if data[coin]["symbol"] == asset:
                return data[coin]["id"]

    # Increments the amount held of an asset
    def buy(self, asset, n):
        coin = self.validate_coin(asset).lower()
        amount = float(n)
        with open(port, "r") as file:
            for line in file:
                if line.__contains__(coin):
                    if amount < 0:
                        sys.exit("Invalid amount")
                    new = float(line.split(",")[2]) + amount
                    self.replace(port, line, f"{new:.2f}")
                    return self.portfolio_view
            self.add_missing_asset(coin)
            with open(port, "r") as file:
                for line in file:
                    if line.__contains__(coin):
                        if amount < 0:
                            sys.exit("Invalid amount")
                        new = float(line.split(",")[2]) + amount
                        self.replace(port, line, f"{new:.2f}")
                        self.portfolio_view

    # Decrements the amount held of an asset
    def sell(self, asset, n):
        coin = self.validate_coin(asset).lower()
        with open(port, "r") as file:
            for line in file:
                if line.__contains__(coin):
                    amount = float(n)
                    if amount < 0:
                        sys.exit("Invalid amount")
        with open(port, "r") as file:
            for line in file:
                if line.__contains__(coin):
                    if (float(line.split(",")[2]) - amount) < 0:
                        sys.exit(f"You don't have that much {self.coin_name(coin)}")
                    new = float(line.split(",")[2]) - amount
                    self.replace(port, line, f"{new:.2f}")
                    return self.portfolio_view
            sys.exit(f"You don't own any {self.coin_name(coin)}")

    # Function to add an asset to portfolio.csv if the asset isn't already in the file
    def add_missing_asset(self, asset):
        with open(port, "a") as file:
            writer = csv.writer(file)
            writer.writerow([self.coin_name(asset), asset, 0])

    # Function to replace asset amount held in portfolio.csv file
    def replace(self, file, searchExp, replaceExp):
        for line in fileinput.input(file, inplace=1):
            if searchExp in line:
                line = line.replace(searchExp.split(",")[2], f"{replaceExp}\n")
            sys.stdout.write(line)

    # Get total value of all assets in your portfolio in USD
    @property
    def total_value(self):
        total = 0
        with open(port, "r") as file:
            for line in file:
                coin, amount = line.split(",")[1:]
                id = self.coin_id(coin)
                price = cg.get_price(ids=id, vs_currencies="usd")[id]["usd"]
                value = price * float(amount)
                total += value
        return f"{total:.2f}"

    # Get value in USD of the holdings of an asset
    def value(self, coin):
        with open(port, "r") as file:
            for line in file:
                if line.__contains__(coin):
                    id = self.coin_id(coin)
                    price = cg.get_price(ids=id, vs_currencies="usd")[id]["usd"]
                    value = price * float(line.split(",")[2])
                    return f"{value:.2f}"

    # Sort list of assets from highest value holding to lowest
    def Sort(self, list):
        return sorted(list, key=lambda asset: float(asset[2].replace("$","")), reverse=True)

    # Return a table with each row containg asset name and symbol, amount, and USD value of holdings
    @property
    def portfolio_view(self):
        table = Table(
            title=f"Total portfolio value: ${self.total_value}",
            box=box.HEAVY_EDGE,
            padding=(0, 3, 0, 3),
            style="cyan",
            title_style="green bold"
        )
        rows = []
        table.add_column("Name", justify="center", style="bold")
        table.add_column("Amount", justify="center", style="bold")
        table.add_column("Value", justify="center", style="green bold")
        with open(port, "r") as file:
            for line in file:
                name, symbol, amount = line.split(",")
                rows.append([f"{name} ({symbol.upper()})", amount, f"${self.value(symbol)}"])
            rows = self.Sort(rows)
            for i in range(len(rows)):
                table.add_row(rows[i][0], rows[i][1], rows[i][2])
        print("\n\n")
        Console().print(table)
        print("\n\n")


def main():
    if len(sys.argv) == 1:
        sys.exit("Too few arguments")
    if len(sys.argv) > 4:
        sys.exit("Too many arguments")
    p = Portfolio()
    parser = argparse.ArgumentParser(description="Manages your crypto portfolio holdings")
    parser.add_argument("-b","--buy", help="Increases holdings, format: {-b/--buy} {digit} {coin symbol}", nargs=2)
    parser.add_argument("-s", "--sell", help="Decreases holdings, format: {-s/--sell} {digit} {coin symbol}", nargs=2)
    parser.add_argument("-p", "--portfolio", help="Shows portfolio.", action="store_true")
    args = parser.parse_args()
    match sys.argv[1].lower():
        case "-b" | "--buy":
            if args.buy[1].isalpha() == False:
                sys.exit("Wrong format, use: {-b/--buy} {digit} {coin}")
            p.buy(args.buy[1], args.buy[0])
        case "-s" | "--sell":
            if args.sell[1].isalpha() == False:
                sys.exit("Wrong format, use: {-s/--sell} {digit} {coin}")
            p.sell(args.sell[1], args.sell[0])
        case "-p" | "--portfolio":
            p.portfolio_view


if __name__ == "__main__":
    main()