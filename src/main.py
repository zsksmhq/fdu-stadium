import time
import argparse

from reserver import Reserver

def parse_args():
    parser = argparse.ArgumentParser(description="args for script")

    parser.add_argument(
        "-s", "--username",
        type=str,
        help="Student Username",
        default=""
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        help="Student Password",
        default=""
    )
    parser.add_argument(
        "-d", "--daytime", 
        type=int,
        default=8,
        help="预约时间，e.g. 值为8就是预约8:00 - 9:00",
    )
    parser.add_argument(
        "-l", "--location",
        type=str,
        default="枫林综合体育馆排球场",
        help="服务项目名，请注意不要错字漏字"
    )
    parser.add_argument(
        "--date",
        type=str,
        default="",
        help="预约日期，不输入默认为选后天的，输入格式：YYYY-MM-DD"
    )
    parser.add_argument(
        "--wait_time",
        type=int,
        default=2,
        help="在7点抢场地时等候的时间(秒)，7点直接抢可能场地没放出来"
    )
    parser.add_argument(
        "--getnow",
        type=bool,
        default=False,
        help="设置为True就是直接预约场地"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    r = Reserver(username = args.username,
                 password = args.password,
                 daytime = args.daytime,
                 location = args.location,
                 date = args.date,
                 wait_time = args.wait_time,
                 getnow = args.getnow)
    r.run()