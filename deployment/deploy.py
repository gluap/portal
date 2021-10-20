#!/usr/bin/env python3
import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

__confvalues__ = {
    "hostname": ["portal.example.com", "the hostname of your instance", "portal\.example\.com"],
    "MAIL_HOST": ["mail.example.com", "the mail server to be used by portal"],
    "MAIL_PORT": ["465", "the port to be used on the mail server"],
    "MAIL_USER": ["sender@example.com", "the username to be used by portal to send mails."],
    "MAIL_PASSWORD": ["changeme", "the mail users password used to send mails."],
    "MAIL_SENDER": ["changeme", "the mail users sender address, e.g. e.g. @example.com."],
    "PORTAL_CLIENT_ID": ["changeme"],
    "UPLOAD_CLIENT_ID": ["changeme"],
    "COOKIE_SECRET": ["changeme"],
    "JWT_SECRET": ["changeme"],
}



def main(args):
    parser = argparse.ArgumentParser(description='Prepare OBS portal deployment.')
    parser.add_argument('--path', type=Path, help='target path, default: .', default=Path("./portal"), required=False)
    parser.add_argument('--repo', type=str, help='source repo, default: https://github.com/openbikesensor/portal',
                        default="https://github.com/openbikesensor/portal", required=False)
    parser.add_argument('--overwrite', type=bool, help="force overwrite of target", required=False, default=False)
    parser.add_argument('--branch', type=str, help='source branch, default: main',
                        default="main", required=False)

    args = parser.parse_args()
    target = args.path

    if not git_available():
        print("git executable not found on path, please install git first.")
        exit()

    if target.exists() and not args.overwrite:
        print(f"The target {target.absolute()} already exists. Supply a nonexisting target with --path=PATH.")
        exit()
    elif target.exists() and args.overwrite:
        if not (target / "data").exists():
            shutil.rmtree(target)
        else:
            print("The data directory does exist, please remove target manually and restart")

    if not ask_yes_no(f"Will create directory {target.absolute()} and deploy portal inside, OK?"):
        print("Aborting, you can chose a different path by supplying a --path=PATH argument")
        exit()

    target.mkdir(parents=True, exist_ok=True)
    source = target / "source"

    conf = get_conf_values()

    git_clone_to(source, args.repo, args.branch)

    copy_configs(source, target)

    apply_settings(target, conf)

    store_settings(target, conf)


def store_settings(target, conf):
    n = datetime.datetime.now()
    (target / f"settings_{n.strftime('%Y-%m-%d_%H-%M-%S')}.json").write_text(json.dumps(conf), "utf-8")


def apply_settings(target, conf):
    for f in [target / "docker-compose.yaml", target / "config" / "api.json", target / "config" / "frontend.json"]:
        content = f.read_text("utf-8")
        for key, value in conf.items():
            if len(__confvalues__[key]) > 2:
                content = re.sub(__confvalues__[key][2], value, content)
            else:
                content = re.sub(f"!!!<<<CHANGEME_{key}>>>!!!", value, content)
        f.write_text(content, "utf-8")


def get_conf_values():
    result = {}
    for k, v in __confvalues__.items():
        if len(v) < 2:
            result[k] = str(uuid.uuid4())
            continue
        print(f"Please enter {v[1]}, example value {v[0]}")
        result[k] = input().strip()
    print("\n\nSummarizing config: ")
    for k, v in result.items():
        print(f"{k}: {v}")
    if not ask_yes_no("everything correct?"):
        return get_conf_values()
    return result


def copy_configs(source: Path, target: Path):
    config = target / "config"
    config.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source / "deployment" / "examples" / "traefik.toml", config / "traefik.toml")
    shutil.copyfile(source / "deployment" / "examples" / "docker-compose.yaml", target / "docker-compose.yaml")
    shutil.copyfile(source / "frontend" / "config.example.json", config / "frontend.json")
    shutil.copyfile(source / "api" / "config.json.example", config / "api.json")


def git_available():
    try:
        subprocess.run(["git", "--version"], capture_output=True)
        return True
    except subprocess.SubprocessError:
        return False


def git_clone_to(target: Path, giturl: str, branch: str):
    try:
        subprocess.run(["git", "clone", "-b", branch, "--recursive", giturl, target.absolute()])
    except subprocess.SubprocessError:
        print("Error while cloning from git")
        exit()


def ask_yes_no(message: str):
    y = ["y", "yes"]
    n = ["n", "no"]
    print(message)
    answer = input("choose [y]es/[n]o:").lower()
    if answer in y:
        return True
    if answer in n:
        return False
    else:
        print(f"{answer} is not a valid input, please choose [y]es/[n]o or pres [ctrl]+c to abort")
        return ask_yes_no(message)


if __name__ == "__main__":
    main(sys.argv)
