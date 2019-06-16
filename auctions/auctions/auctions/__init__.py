import injector

from auctions.application.queries import GetActiveAuctions, GetSingleAuction
from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases.placing_bid import PlacingBid, PlacingBidOutputBoundary
from auctions.application.use_cases.withdrawing_bids import WithdrawingBids
from auctions.domain.events import AuctionEnded, BidderHasBeenOverbid, WinningBidPlaced

__all__ = [
    # module
    "Auctions",
    # events
    "AuctionEnded",
    "WinningBidPlaced",
    "BidderHasBeenOverbid",
    # repositories
    "AuctionsRepository",
    # use cases
    "PlacingBid",
    "PlacingBidOutputBoundary",
    "WithdrawingBids",
    # queries
    "GetActiveAuctions",
    "GetSingleAuction",
]


class Auctions(injector.Module):
    @injector.provider
    def placing_bid_uc(self, boundary: PlacingBidOutputBoundary, repo: AuctionsRepository) -> PlacingBid:
        return PlacingBid(boundary, repo)

    @injector.provider
    def withdrawing_bids_uc(self, repo: AuctionsRepository) -> WithdrawingBids:
        return WithdrawingBids(repo)
