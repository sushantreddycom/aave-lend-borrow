from scripts.aave_borrow import approve_erc20_token, get_account,  get_lending_pool, get_asset_price, get_aave_account_details
from brownie import config, network
from scripts.helpful_scripts import FORKED_LOCAL_ENVIRONMENTS, TESTNET_ENVIRONMENTS
import pytest
from web3 import Web3

''' test if eth-dai price is fetched by function get_asset_rpcie'''
def test_get_asset_price():
    if network.show_active() not in FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    dai_eth_address = config["networks"][network.show_active()]["dai_eth_address"]

    # Act
    price = get_asset_price(dai_eth_address)

    # Assert
    assert price > 0

'''test if we get a lending pool contract'''
def test_get_lending_pool():
    if network.show_active() not in FORKED_LOCAL_ENVIRONMENTS:
        pytest.skip()
    
    # Arrange # Act
    lending_pool_contract = get_lending_pool()
    
    # Assert
    assert lending_pool_contract != None


''' test if we can approve a ERC20 token '''
''' do this test in a Kovan network'''
def test_approve_ERC20():
    if network.show_active() not in TESTNET_ENVIRONMENTS:
        pytest.skip()
    # Arrange   
    erc20_address = config["networks"][network.show_active()]["dai_token_address"]
    account = get_account()
    amount = Web3.toWei(1, "ether")
    lending_pool_contract = get_lending_pool()

    # Act
    approve = approve_erc20_token(amount, lending_pool_contract.address, erc20_address, account)

    # Assert
    assert approve is True

