import os
from enum import Enum

import requests
from bs4 import BeautifulSoup

ASTRODX_TESTFLIGHTS = {
    "Group A": "https://testflight.apple.com/join/rACTLjPL",
    "Group B": "https://testflight.apple.com/join/ocj3yptn"
}

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PUSH_TARGET = os.environ.get("PUSH_TARGET")


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
    status_text = "All TestFlights status:\n"
    open_flag = False
    for group, url in ASTRODX_TESTFLIGHTS.items():
        status = get_flight_status(url)
        status_text += f"[{group}]({url}): This test is {status.name}\n"
        if status == TestFlightStatu.OPEN:
            open_flag = True
    print(status_text)
    if open_flag:
        resp = requests.post(
            "https://www.kookapp.cn/api/v3/direct-message/create",
            headers={"Authorization": f"Bot {BOT_TOKEN}"},
            data={
                "content": status_text,
                "target_id": PUSH_TARGET,
                "type": 9
            }
        )
        if resp.json()["code"] != 0:
            print("Message Push Filed")


if __name__ == '__main__':
    main()
