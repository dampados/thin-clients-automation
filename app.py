#!/usr/bin/env python3
import subprocess
from icmplib import ping

from app_helpers import load_inventory, get_credential, get_ssh_profile, get_type_config
import executors


def main():
    # PREPARATION
    inventory = load_inventory("./inventory.json")

    # CALLBACK MAPPING!!!!
    EXECUTOR_MAP = {
        "hp": executors.deploy_hp,
        "linux_common": executors.deploy_linux_common,
    }
    # CALLBACK MAPPING!!!!

    # =======================MAIN ITERATOR======================= #
    for host in inventory['hosts']:
        # 1. get args for this next host:
        # little helpers for readability
        # we need all three, so any exception SKIPS a host!
        try:
            type_config = get_type_config(host, inventory)
            cred = get_credential(host, inventory)
            ssh_profile = get_ssh_profile(host, inventory)
        except ValueError as valueError:
            print(f"inventory is broken, see the {valueError.stderr.strip()}")
                # !!! #
            continue # skip this host
                # !!! #

        # 2. health check!
        alive = ping(host['ip'], count=1, timeout=2, privileged=False)
        if not alive or alive.packets_received == 0:
            print(f"\n❌ [{type_config["name"]}] {host['ip']} offline, skipping")
            continue
        print(f"\n🚀 [{type_config["name"]}] {host['ip']} online, diving")

        # 3. prep host with config files!:
        print(f"--> 📄 [{type_config["name"]}] {host['ip']} files upload to {type_config['config_remote_dir']}")
        try:
            executors.upload_files(
                ip=host['ip'],
                options=ssh_profile['options'],
                username=cred['username'],
                password=cred['password'],
                local_dir=type_config['config_local_dir'],
                remote_dir=type_config['config_remote_dir']
            )
        except FileNotFoundError as e:
            print(f"❌ Cant upload configs: {e}")
            continue
        except subprocess.CalledProcessError as e:
            print(f"❌ SCP error (most probably): {e}")
            continue
        except subprocess.TimeoutExpired as e:
            print(f"❌ SCP timeout. Host offline? : {e}")
            continue

        # 4. execute import/deployment ABSTRACT
        print(f"--> ⏩ [{type_config["name"]}] {host['ip']} importing")
        executor = EXECUTOR_MAP.get(type_config["name"])
        if not executor:
            print(f"❌ No executor for type {type_config["name"]}, skipping")
            continue

        try:
            executor(
                ip=host['ip'],
                options=ssh_profile["options"],
                username=cred["username"],
                password=cred["password"],
                local_dir=type_config["config_local_dir"],
                remote_dir=type_config["config_remote_dir"]
            )
        except FileNotFoundError as e:
            print(f"❌ File transaction broken?: {e}")
            continue
        except subprocess.TimeoutExpired as e:
            print(f"❌ SSH commands timeout. Host offline? : {e}")
            continue
        except RuntimeError as e:
            print(f"❌ Runtime error: {e}")
            continue
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main()