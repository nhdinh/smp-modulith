from typing import List

from sqlalchemy import func
# from sqlalchemy.engine import RowProxy
from sqlalchemy.engine.row import RowProxy

from auctions.application.queries import AuctionDto, GetActiveAuctionsQuery, GetSingleAuctionQuery
from auctions_infrastructure import auctions
from db_infrastructure import SqlQuery

from foundation.value_objects.factories import get_dollars


class SqlGetActiveAuctionsQuery(GetActiveAuctionsQuery, SqlQuery):
    def query(self) -> List[AuctionDto]:
        return [
            _row_to_dto(row) for row in self._conn.execute(auctions.select().where(auctions.c.ends_at > func.now()))
        ]


class SqlGetSingleAuctionQuery(GetSingleAuctionQuery, SqlQuery):
    def query(self, auction_id: int) -> AuctionDto:
        row = self._conn.execute(auctions.select().where(auctions.c.id == auction_id)).first()
        return _row_to_dto(row)


def _row_to_dto(auction_proxy: RowProxy) -> AuctionDto:
    return AuctionDto(
        id=auction_proxy.id,
        title=auction_proxy.title,
        current_price=get_dollars(auction_proxy.current_price),
        starting_price=get_dollars(auction_proxy.starting_price),
        ends_at=auction_proxy.ends_at,
    )
