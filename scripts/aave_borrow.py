
# AAVE converts ETH to wETH
# we need to first access AAVE contract that does this conversion
# This will allow us to lend ETH to AAVE platform
from pkg_resources import require
from scripts.get_weth import get_weth
from scripts.helpful_scripts import get_account, FORKED_LOCAL_ENVIRONMENTS
from brownie import network, config, interface
from web3 import Web3

''' main function that lends Weth, borrows DAI and repays DAI on AAVE'''
def aave_borrow():
    account = get_account()
    weth_erc20_address = config["networks"][network.show_active()]["weth_token"]
    amount = Web3.toWei(0.1, "ether")
    # if network is a mainnet, then we will first min 0.1 Eth equivalent weth
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        get_weth()

    # get lending pool contract
    lending_pool_contract = get_lending_pool()
    print(lending_pool_contract)

    # # approve weth token usage
    # approve = approve_erc20_token(amount, lending_pool_contract.address, weth_erc20_address, account)

    # # next step is to deposit weth to Aave

    # if approve:
    #     print ('depositing')
    #     tx = lending_pool_contract.deposit(weth_erc20_address,  amount, account.address, 0, {"from": account})
    #     tx.wait(1)
    #     print('deposited')
    
    (borrowable_eth, total_debt) = get_aave_account_details(lending_pool_contract, account)

    # borrow DAI
    # first we need to get the price of ETH/DAI 
    # we use V#PriceAggregator
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_address"])
    print(f"current DAI/ETH price is {dai_eth_price}")

    # calculate the amount of dai to borrow
    # keep it at 50% the limit to make sure we are not liquidated

    dai_to_borrow = (1/dai_eth_price) * borrowable_eth * 0.5
    print(f"we are going to borrow {dai_to_borrow} DAI")


    # # inputs to borrow function
    # # asset - address of the underlying asset - in our case its DAI
    # # amount in Wei
    # # interest rate mode - 0 - Variable, 1 Fixed
    # # referral code - 0
    # # on behalf of will be account address
    # dai_token_address = config["networks"][network.show_active()]["dai_token_address"]
    # tx = lending_pool_contract.borrow(dai_token_address,Web3.toWei(dai_to_borrow, "ether"),1,0, account.address, {"from": account})
    # tx.wait(1)

    # print("borrowed DAI successfully at a fixed rate")

    # get_aave_account_details(lending_pool_contract, account)

    repay(dai_to_borrow, lending_pool_contract, account)
    get_aave_account_details(lending_pool_contract, account)

'''
    function to approve use of a ERC token in an account
    amount is amount in wei
    spender is smart contract that wants to access the erc_20 token
    erc20_address - contract Address for generating contract
'''
def approve_erc20_token(amount, spender, erc20_address, account):
    print("approving ERC 20 token")
    erc_20 = interface.IERC20(erc20_address)
    approve = erc_20.approve(spender, amount, {"from": account})
    approve.wait(1)
    print('Approved')
    return True

'''
    gets the Aave lending pool contract
    we use getLendingPool() function in LendingPoolAddressesProvider
'''
def get_lending_pool():
    lending_pool_address_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addresses_provider"])
    lending_pool_address = lending_pool_address_provider.getLendingPool()
    lending_pool_contract = interface.ILendingPool(lending_pool_address)
    return lending_pool_contract

''' gets our account details on Aave
    how much collateral we have
    how much debt we have
    what is health factor etc
    
    note : all amount in Eth'''

def get_aave_account_details(lending_pool, account):
     (total_collateral_eth, total_debt_eth, available_borrow_eth, current_liquidation_threshold, ltv, health_factor) = lending_pool.getUserAccountData(account.address)

     total_collateral_eth  = Web3.fromWei(total_collateral_eth, "ether")
     total_debt_eth  = Web3.fromWei(total_debt_eth, "ether")
     available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")

     print(f"You have {total_collateral_eth} worth ether as collateral")   
     print(f"You have {total_debt_eth} worth ether as debt")
     print(f"You have {available_borrow_eth} worth ether available for borrowing")       
     print(f"Your current liquidity threshold is {current_liquidation_threshold}")       
     print(f"Your Loan to Value ratiois {ltv}")
     print(f"Your health factor is {health_factor}")
     return (float(available_borrow_eth), float(total_debt_eth))


''' gets the asset price for a currency pair Eth/Dai'''
def get_asset_price(price_feed_address):
    price_feed_contract = interface.IAggregatorV3Interface(price_feed_address)
    price = price_feed_contract.latestRoundData()[1]
    converted_price = Web3.fromWei(price, "ether")
    return float(converted_price)

''' repays the current amount in the contract. amount in ether'''
def repay(amount, lending_pool, account):
    #(available_borrow_eth, total_debt_eth) = get_aave_account_details(lending_pool, account)
    # require(amount <=  Web3.toWei(total_debt_eth, "ether"), "Amount to repay should be le"

    dai_token_address = config["networks"][network.show_active()]["dai_eth_address"]
    dai_repay_amount = Web3.toWei(amount,"ether")
    print(f'dai to be repaid: {dai_repay_amount}')
    print(f'lending pool address: {lending_pool.address}')
    print(f'dai token address: {dai_token_address}')
    print(f'account address: {account}')
    # First thing we need to do is to approve the amount to be accessed from our address
    approve_erc20_token(dai_repay_amount, lending_pool, dai_token_address, account )
    
    # call the repay function
    repay_tx = lending_pool.repay(dai_token_address, amount, account.address, {"from": account} )
    repay_tx.wait(1)
    print("repaid")


def main():
    aave_borrow()



