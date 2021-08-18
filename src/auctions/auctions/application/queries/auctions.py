import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List

from foundation.value_objects import Money


@dataclass
class AuctionDto:
    id: int
    title: str
    current_price: Money
    starting_price: Money
    ends_at: datetime

    def serialize(self) -> object:
        return {
            "id": self.id,
            "title": self.title,
            "current_price": self.current_price,
            "starting_price": self.starting_price,
            "ends_at": self.ends_at,
        }


class GetSingleAuctionQuery(abc.ABC):
    @abc.abstractmethod
    def query(self, auction_id: int) -> AuctionDto:
        pass


class GetActiveAuctionsQuery(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[AuctionDto]:
        pass
