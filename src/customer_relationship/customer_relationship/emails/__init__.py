from abc import abstractmethod
from dataclasses import dataclass

from foundation.value_objects import Money


class Email:
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def html(self) -> str:
        pass

    @property
    @abstractmethod
    def text(self) -> str:
        pass


@dataclass
class Overbid(Email):
    auction_title: str
    new_price: Money

    @property
    def title(self) -> str:
        return "You have been overbid :("

    @property
    def text(self) -> str:
        return f'A new bid has been placed on the auction "{self.auction_title}". New price is {self.new_price}.'

    @property
    def html(self) -> str:
        return self.text


@dataclass
class Winning(Email):
    auction_title: str
    amount: Money

    @property
    def title(self) -> str:
        return "You are winning :)"

    @property
    def text(self) -> str:
        return f'Congratulations! Your bid {self.amount} is the winning one one the auction "{self.auction_title}"'

    @property
    def html(self) -> str:
        return self.text


@dataclass
class PaymentSuccessful(Email):
    auction_title: str
    paid_price: Money

    @property
    def title(self) -> str:
        return f"Payment for '{self.auction_title}' succeeded"

    @property
    def text(self) -> str:
        return f"Payment {self.paid_price} confirmed, your item is on its way!"

    @property
    def html(self) -> str:
        return self.text


@dataclass
class StoreRegistrationConfirmationEmail(Email):
    shop_name: str
    confirmation_token: str

    @property
    def title(self) -> str:
        return f'Confirm Store registration'

    @property
    def text(self) -> str:
        return f'Someone take your email to register for the store {self.shop_name}. If this is your registration, ' \
               f'please click the link below to confirm. {self.confirmation_token} '

    @property
    def html(self) -> str:
        return self.text


@dataclass
class StoreCreatedSuccessfulEmail(Email):
    shop_name: str
    admin_name: str

    @property
    def title(self) -> str:
        return f'Store created successfully'

    @property
    def text(self) -> str:
        return f'Your store {self.shop_name} has been created successfully. Now you can login to manage it'

    @property
    def html(self) -> str:
        return self.text


@dataclass
class PasswordResetTokenEmail(Email):
    username: str
    token: str

    @property
    def title(self) -> str:
        return 'Request to reset password'

    @property
    def text(self) -> str:
        return f'Hi {self.username}, someone has request to reset your password. If this is yours, please follow the ' \
               f'link to reset your password. {self.token} '

    @property
    def html(self) -> str:
        return self.text


@dataclass
class PasswordResettedNotificationEmail(Email):
    username: str

    @property
    def title(self) -> str:
        return 'Your password has been resetted'

    @property
    def text(self) -> str:
        return f'Hi {self.username}, your password has been resetted.'

    @property
    def html(self) -> str:
        return self.text
