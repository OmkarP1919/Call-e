import json
from pathlib import Path
from datetime import datetime


FILE = Path("data/calls.json")


def save_call(
    phone_number,
    objective,
    result,
    gathered_information
):

    FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if FILE.exists():

        with open(
            FILE,
            "r",
            encoding="utf-8"
        ) as f:

            calls = json.load(f)

    else:

        calls = []

    record = {

        "timestamp":
            datetime.now().isoformat(),

        "phone_number":
            phone_number,

        "objective":
            objective,

        "call_status":
            result.get("status"),

        "completion_confidence":
            result.get(
                "completion_confidence"
            ),

        "gathered_information":
            gathered_information
    }

    calls.append(record)

    with open(
        FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            calls,
            f,
            indent=4,
            ensure_ascii=False
        )