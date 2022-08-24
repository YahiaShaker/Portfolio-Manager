import pytest
from project import Portfolio
import argparse
import sys

p = Portfolio()
def argv_input(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--buy", nargs=2)
    parser.add_argument("-s", "--sell", nargs=2)
    parser.add_argument("-p", "--portfolio", action="store_true")
    parser.add_argument("-v", "--validate", nargs=1)
    args = parser.parse_args(argv)
    return argv

def test_buy():
    with open("portfolio.csv",'r+') as file:
        file.truncate(0)

    args = argv_input(["-b","2","sol"])
    p.buy(args[2],args[1])
    file = open("portfolio.csv")
    assert file.read() == "Solana,sol,2.00\n"

    args = argv_input(["-b","3","btc"])
    p.buy(args[2],args[1])
    file = open("portfolio.csv")
    assert file.read() == "Solana,sol,2.00\nBitcoin,btc,3.00\n"

    args = argv_input(["--buy","3","btc"])
    p.buy(args[2],args[1])
    file = open("portfolio.csv")
    assert file.read() == "Solana,sol,2.00\nBitcoin,btc,6.00\n"


def test_sell():
    with open("portfolio.csv",'r+') as file:
        file.truncate(0)
        file.write("Bitcoin,btc,8.00\nSolana,sol,3.00\n")

    args = argv_input(["-s","3","btc"])
    p.sell(args[2],args[1])
    file = open("portfolio.csv")
    assert file.read() == "Bitcoin,btc,5.00\nSolana,sol,3.00\n"

    args = argv_input(["--sell","3","sol"])
    p.sell(args[2],args[1])
    file = open("portfolio.csv")
    assert file.read() == "Bitcoin,btc,5.00\nSolana,sol,0.00\n"

    with pytest.raises(SystemExit):
        args = argv_input(["-s","1","sol"])
        p.sell(args[2],args[1])
        file = open("portfolio.csv")

def test_validate():
    args = argv_input(["-v","sol"])
    assert p.validate_coin(args[1]) == "sol"

    args = argv_input(["--validate","btc"])
    assert p.validate_coin(args[1]) == "btc"

    with pytest.raises(SystemExit):
        args = argv_input(["--validate","CS50COIN"])
        p.validate_coin(args[1])