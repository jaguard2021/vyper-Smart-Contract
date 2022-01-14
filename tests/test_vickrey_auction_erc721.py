import pytest

from brownie import (
    accounts,
    chain,
    reverts,
    Wei,
)

@pytest.fixture(scope="module", autouse=True)
def erc721(accounts, ERC721):
    c = accounts[0].deploy(
        ERC721,
        "Test Token",
        "TST",
        "https://www.test.com/",
        100,
        accounts[0],
        accounts[0]
    )

    # Mint 1 token
    c.mint(
        accounts[0],
        '1.json',
        {'from': accounts[0]}
    )
    yield c


@pytest.fixture(scope="module", autouse=True)
def auction(accounts, erc721, VickreyAuctionERC721):
    c = VickreyAuctionERC721.deploy(
        erc721.address,
        {'from': accounts[0]}
    )
    yield c


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.fixture
def initialise(accounts, erc721, auction):
    approve = erc721.approve(auction.address, 1, {'from': accounts[0]})

    start = auction.start_auction(
        Wei("1 ether"),
        chain.time() + 100000,
        1,
        {'from': accounts[0]}
    )

    yield start


@pytest.fixture
def a1_first_bid(accounts, auction):

    tx = auction.bid(
        {
            'from': accounts[1],
            'value': Wei("1.5 ether")
        }
    )
    return tx


@pytest.fixture
def a1_second_bid(accounts, auction, a1_first_bid):

    tx = auction.bid(
        {
            'from': accounts[1],
            'value': Wei("0.5 ether")
        }
    )

    return tx


@pytest.fixture
def a2_first_bid(accounts, auction, a1_second_bid):

    tx = auction.bid(
        {
            'from': accounts[2],
            'value': Wei("3 ether")
        }
    )

    return tx


@pytest.fixture
def close_auction(accounts, chain, auction, a2_first_bid):

    chain.sleep(100001)

    tx = auction.close({'from': accounts[0]})

    return tx


def test_start_state(auction):

    assert auction.is_started() == False


def test_auction_started(auction, erc721, initialise):

    assert auction.is_started() == True
    assert auction.start_price() == Wei("1 ether")
    assert auction.token_id() == 1

    assert erc721.ownerOf(1) == auction


def test_bid(accounts, auction, initialise, a1_first_bid):

    assert len(a1_first_bid.events) == 1
    assert a1_first_bid.events[0]['value'] == Wei("1.5 ether")
    assert a1_first_bid.events[0]['bidder'] == accounts[1]

    assert auction.get_highest_bid() == Wei("1.5 ether")
    assert auction.bids_to_bidder(Wei("1.5 ether")) == accounts[1]


def test_cumulative_bid_1(accounts, auction, initialise, a1_second_bid):

    assert len(a1_second_bid.events) == 1
    assert auction.get_highest_bid() == Wei("2 ether")
    assert a1_second_bid.events[0]['value'] == Wei("2 ether")
    assert a1_second_bid.events[0]['bidder'] == accounts[1]

    assert auction.get_highest_bid() == Wei("2 ether")
    assert auction.bids_to_bidder(Wei("2 ether")) == accounts[1]


def test_competing_bid(accounts, auction, initialise, a2_first_bid):

    assert len(a2_first_bid.events) == 1
    assert a2_first_bid.events[0]['value'] == Wei("3 ether")
    assert a2_first_bid.events[0]['bidder'] == accounts[2]

    assert auction.get_highest_bid() == Wei("3 ether")
    assert auction.bids_to_bidder(Wei("3 ether")) == accounts[2]
    assert auction.bidder_to_balance(accounts[1]) == Wei("2 ether")


def test_close(accounts, chain, erc721, auction, initialise, a2_first_bid):

    a0_balance = accounts[0].balance()

    chain.sleep(100001)

    tx = auction.close({'from': accounts[0]})

    assert erc721.ownerOf(1) == accounts[2]

    assert accounts[0].balance() == a0_balance + auction.get_second_highest_bid()
    assert auction.has_ended() == True


def test_refund_1(accounts, auction, initialise, close_auction):

    a1_balance = accounts[1].balance()

    refund_tx_1 = auction.refund({'from': accounts[1]})

    assert len(refund_tx_1.events) == 1
    assert refund_tx_1.events[0]['value'] == Wei("2 ether")
    assert refund_tx_1.events[0]['bidder'] == accounts[1]

    assert accounts[1].balance() == a1_balance + Wei("2 ether")
    assert auction.bidder_to_balance(accounts[1]) == 0


def test_refund_2(accounts, auction, initialise, close_auction):

    a1_balance = accounts[2].balance()

    refund_tx_1 = auction.refund({'from': accounts[2]})

    assert len(refund_tx_1.events) == 1
    assert refund_tx_1.events[0]['value'] == Wei("1 ether")
    assert refund_tx_1.events[0]['bidder'] == accounts[2]

    assert accounts[1].balance() == a1_balance + Wei("1 ether")
    assert auction.bidder_to_balance(accounts[2]) == 0


def test_single_bid_wins(accounts, auction, initialise, a1_first_bid):

    assert auction.get_second_highest_bid() == Wei("1 ether")

    a1_balance = accounts[1].balance()
    a0_balance = accounts[0].balance()

    chain.sleep(100001)

    close_tx = auction.close({'from': accounts[0]})

    assert accounts[0].balance() == a0_balance + auction.get_second_highest_bid()
    assert auction.has_ended() == True

    refund_tx = auction.refund({'from': accounts[1]})

    assert len(refund_tx.events) == 1
    assert refund_tx.events[0]['value'] == Wei("0.5 ether")
    assert refund_tx.events[0]['bidder'] == accounts[1]


def test_illegal_close_auction_1(accounts, auction, initialise):

    assert auction.has_ended() == False

    with reverts("Auction has not ended"):
        auction.close({'from': accounts[0]})

    assert auction.has_ended() == False


def test_illegal_close_auction_2(accounts, auction, initialise, a1_first_bid):

    assert auction.has_ended() == False

    with reverts("Auction has not ended"):
        auction.close({'from': accounts[0]})

    assert auction.has_ended() == False


def test_no_bid_close(accounts, chain, erc721, auction, initialise):

    chain.sleep(100001)

    close_tx = auction.close({'from': accounts[0]})

    assert erc721.ownerOf(1) == accounts[0]
    assert auction.has_ended() == True
