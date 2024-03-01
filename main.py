import os
from enum import Enum

import requests
from bs4 import BeautifulSoup

ASTRODX_TESTFLIGHTS = {
    "Group A": "https://testflight.apple.com/join/rACTLjPL",
    "Group B": "https://testflight.apple.com/join/ocj3yptn"
}
STATUS_BODY = """
<h1 style=\"text-align: center\">All TestFlights status</h1>
<h2 style="text-align: center">
%s
</h2>
"""
LINK_TEMPLATE = "    <a href=\"%s\">%s</a> is %s"

APP_TOKEN = os.environ.get("APP_TOKEN")


class TestFlightStatu(Enum):
    FULL = "full"
    CLOSED = "closed"
    OPEN = "open"


def get_flight_status(url: str) -> TestFlightStatu:
    content = requests.get(url, headers={"Accept-Language": "en-us"}).text
    bs = BeautifulSoup(content, "lxml")
    status_text = bs.select("#status > div.beta-status > span")[0].text.strip()
    if "This beta is full." in status_text:
        return TestFlightStatu.FULL
    if "This beta isn't accepting" in status_text:
        return TestFlightStatu.CLOSED
    return TestFlightStatu.OPEN


def main():
    status_text = ""
    open_flag = False
    for group, url in ASTRODX_TESTFLIGHTS.items():
        status = get_flight_status(url)
        status_text += LINK_TEMPLATE % (url, group, status.value) + "<br>\n"
        if status == TestFlightStatu.OPEN:
            open_flag = True

    body = STATUS_BODY % status_text.strip('\n')
    print(body)
    if open_flag:
        resp = requests.post(
            'https://wxpusher.zjiecode.com/api/send/message',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'appToken': APP_TOKEN,
                'summary': '有可用的 AstroDX 测试',
                'content': body,
                'contentType': 2,
                'topicIds': [
                    25948
                ],
                'verifyPay': 'false'
            }
        )
        print(resp.json()["msg"])


if __name__ == '__main__':
    main()
