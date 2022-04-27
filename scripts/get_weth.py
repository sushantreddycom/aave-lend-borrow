# function here converts ETH to wETH
# wETH is an ERC-20 based token

from scripts.helpful_scripts import get_account
from brownie import interface, config, network
from web3 import Web3

def get_weth():
    """
        Mints wETH by depositing ETH
    """

    # get account
    account = get_account()

    # get weth contract from network
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])

    tx = weth.deposit({"from": account, "value": Web3.toWei(0.1, "ether")})
    tx.wait(1)

    print("Received 0.1 weth in our address")

    return tx

def main():
    get_weth()
