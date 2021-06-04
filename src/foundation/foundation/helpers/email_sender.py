#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from typing import Tuple

from foundation.email import Email


@dataclass(repr=False)
class DefaultEmailConfig:
    email_host: str
    email_port: int
    email_username: str
    email_password: str
    email_from: Tuple[str, str]

    @property
    def formatted_from(self) -> str:
        return f"{self.email_from[0]} <{self.email_from[1]}>"


class EmailSender:
    def __init__(self, config: DefaultEmailConfig) -> None:
        self._config = config

    def send(self, recipient: str, email: Email) -> None:
        with smtplib.SMTP(self._config.email_host, self._config.email_port) as server:
            server.login(self._config.email_username, self._config.email_password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email.title
            msg["From"] = self._config.formatted_from
            msg["To"] = recipient
            msg.attach(MIMEText(email.text, "plain"))
            msg.attach(MIMEText(email.html, "html"))

            server.sendmail(self._config.formatted_from, recipient, msg.as_string())
