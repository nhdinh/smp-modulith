from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from auctions import AuctionBegan, BeginningAuction
from auctions.application.use_cases.beginning_auction import BeginningAuctionInputDto
from auctions.domain.exceptions import AuctionEndingInThePast
from auctions.tests.in_memory_repo import InMemoryAuctionsRepo
from foundation.events import EventBus
from foundation.value_objects.factories import get_money


@pytest.fixture()
def event_bus_mock() -> Mock:
    return Mock(spec_set=EventBus)


@pytest.fixture()
def repo(event_bus_mock: Mock) -> InMemoryAuctionsRepo:
    return InMemoryAuctionsRepo(event_bus_mock)


@pytest.fixture()
def beginning_auction_uc(repo: InMemoryAuctionsRepo) -> BeginningAuction:
    return BeginningAuction(repo)


def test_BeginningAuction_SocksFor10DollarsEndingInFuture_emitsEvent(
        beginning_auction_uc: BeginningAuction, event_bus_mock: Mock
) -> None:
    input_dto = BeginningAuctionInputDto(1, "Socks", get_money("10.00"), datetime.now() + timedelta(days=7))
    beginning_auction_uc.execute(input_dto)

    event_bus_mock.post.assert_called_once_with(AuctionBegan(1, get_money("10.00"), "Socks"))


def test_BeginningAuction_EndsAtInThePast_raisesException(beginning_auction_uc: BeginningAuction) -> None:
    yesterday = datetime.now() - timedelta(days=1)
    with pytest.raises(AuctionEndingInThePast):
        beginning_auction_uc.execute(BeginningAuctionInputDto(1, "Foo", get_money("1.00"), yesterday))
