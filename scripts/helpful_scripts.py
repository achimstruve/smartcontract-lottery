from brownie import (
    config,
    network,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
    Contract,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

# Mock contract information
DECIMALS = 8
INITIAL_VALUE = 200000000000


def get_account(index=0, id=None):
    # accounts[0] - brownie ganache accounts
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined,
    otherwise it will deploy a mock version of that contract, and return that mock contract.

        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract. Example: MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mock deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=5 * 10**17
):  # 0.5 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address) # usage of the interface (possible with brownie)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract!")
    return tx
