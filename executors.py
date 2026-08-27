# file executors.py
import executors_helpers

# =======================FILE EXECUTORS======================= #
def upload_files(ip, options, username, password, local_dir, remote_dir):
    import os, subprocess

    # raises:
    # 1. FileNotFoundError — local_dir does not exist
    # 2. subprocess.CalledProcessError — scp command failed
    # 3. subprocess.TimeoutExpired — scp timed out after 60s

    # 1 local config path check + rasing
    if not os.path.isdir(local_dir):
        raise FileNotFoundError(f"❌ Local {local_dir} is non-existent, skip")

    # 2 CLEAN BEFORE UPLOAD
    clean_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "rm", "-rf", remote_dir]

    result_cleaning = subprocess.run(
        clean_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        # check=True,
        check=False,  # <-- НЕ падаем, а смотрим ошибку
    )
    
    # 3 CREATE CATALOG BEFORE UPLOAD
    mkdir_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mkdir", "-p", remote_dir]

    result_mkdir = subprocess.run(
        mkdir_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        # check=True,
        check=False,  # <-- НЕ падаем, а смотрим ошибку
    )

    # 4 UPLOAD
    scp_cmd = [
        "sshpass", "-p", password,
        "scp"
    ] + options + [
        "-r", 
        f"{local_dir}/.", 
        f"{username}@{ip}:{remote_dir}/"
    ]
    
    result_upload = subprocess.run(
        scp_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        # check=True,
        check=False,
    )

    # TODO debug!
    if result_upload.returncode != 0:
        print(f"❌ SCP STDOUT: {result_upload.stdout}")
        print(f"❌ SCP STDERR: {result_upload.stderr}")
        print(f"❌ SCP RETURNCODE: {result_upload.returncode}")
        return False

    print(f"--> ✅ OK FILES {local_dir} to {remote_dir}")
    # TODO debug vvv
    # print(result_cleaning)
    # print(result_mkdir)
    # print(result_upload)
    # TODO debug ^^^
    return True


# =======================HP EXECUTORS======================= #
def deploy_hp_deprecated(ip, options, username, password, local_dir, remote_dir):
    import os, subprocess, glob, time


    ## COMMIT EXACT 
#     root@HPTC-reception1:~# mclient commit /root/ConnectionType/freerdp/connections
# root@HPTC-reception1:~# mclient get /root/ConnectionType/freerdp/connections
# Manticore key does not exist or is irrelevant
# root@HPTC-reception1:~# mclient get root/ConnectionType/freerdp/connections
# dir root/ConnectionType/freerdp/connections/{1d08e3e4-7513-4758-a39a-13713cb5fa73}
# dir root/Conne[[[[ctionType/freerdp/connections/{47ac1a0e-cc17-42f9-a9cb-ae135cd1e8fe}
# dir root/ConnectionType/freerdp/connections/{7c5103b3-de0f-4e4f-bd37-2147b633fd8a}
# dir root/ConnectionType/freerdp/connections/{b795a793-0a81-4cec-b9b2-ffaf4e6b63a0}
# dir root/ConnectionType/freerdp/connections/{d81c5b39-d705-4877-97af-63415fd59790}
# dir root/ConnectionType/freerdp/connections/{f78e524c-3eed-45f9-b57f-ed25e7ea700b}
# dir root/ConnectionType/freerdp/connections/{ff73ff73-7513-4758-a39a-13713cb5fa73}
# root@HPTC-reception1:~# mclient delete root/ConnectionType/freerdp/connections
# root@HPTC-reception1:~# mclient commit root/ConnectionType/freerdp/connections
# root@HPTC-reception1:~# mclient get root/ConnectionType/freerdp/connections
# root@HPTC-reception1:~# mclient commit 
# Manticore key does not exist or is irrelevant
# root@HPTC-reception1:~# 


    # raises:
    # 1. FileNotFoundError — local_dir does not exist or empty
    # 2. subprocess.TimeoutExpired — any command timed out (10s)

    if not os.path.isdir(local_dir):
        raise FileNotFoundError(f"❌ Local {local_dir} is non-existent, skip")

    # 1 DELETE
    delete_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient delete root/ConnectionType/freerdp/connections"]
    
    result_delete = subprocess.run(
        delete_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    time.sleep(1)


    # 3 COMMIT
    commit_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient commit root/ConnectionType/freerdp/connections"]
    # ] + options + [f"{username}@{ip}", "mclient commit"]


    result_commit = subprocess.run(
        commit_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    time.sleep(1)

    # 4 DELETE CHECK
    check_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient get root/ConnectionType/freerdp/connections"]

    result_delete_check = subprocess.run(
        check_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    result_lines = result_delete_check.stdout.strip().split('\n')
    profiles_count = len([line for line in result_lines if line.strip()])

    print(f"--> 🗑 HP subprocess: profile purge results -- Profiles count: {profiles_count} ")


    # 2 IMPORT EACH XML
    xml_files = sorted(glob.glob(os.path.join(local_dir, "*.xml")))
    if not xml_files:
        raise FileNotFoundError(f"❌ Local {local_dir} is empty, skip")

    for xml_file in xml_files:
        filename = os.path.basename(xml_file)
        import_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"mclient import {remote_dir}/{filename}"]
        
        subprocess.run(
            import_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    time.sleep(1)


    # 3 COMMIT
    commit_cmd = [
        "sshpass", "-p", password,
        "ssh"
    # ] + options + [f"{username}@{ip}", "mclient commit root/ConnectionType/freerdp/connections"]
    ] + options + [f"{username}@{ip}", "mclient commit"]

    result_commit = subprocess.run(
        commit_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    time.sleep(1)


    # 4 AFTER CHECK
    check_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient get root/ConnectionType/freerdp/connections"]

    result_check = subprocess.run(
        check_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    result_lines = result_check.stdout.strip().split('\n')
    profiles_count = len([line for line in result_lines if line.strip()])

    print(f"--> ✅ HP subprocess done! Profiles count: {profiles_count} ")

def deploy_hp(ip, options, username, password, local_dir, remote_dir):
    import os, subprocess, glob, time

    # raises:
    # 1. RuntimeError — can't list /home or get users on remote host
    # 2. RuntimeError — no valid users with home dirs found
    # 3. subprocess.TimeoutExpired — any ssh/subprocess command timed out (10s)

    # 1 purge installed profiles inside the same CONTEXT
    # intermediate validation !!!
    # 2 import profiles one by one
    # final validation !!!

    # !!0!! PREFLIGHT checks
    if not os.path.isdir(local_dir):
            raise FileNotFoundError(f"❌ Local {local_dir} is non-existent, skip")

    # !!1!! PURGING (same context this time)
    executors_helpers.hp_purge_profiles(ip, options, username, password)

    # !!2!! INTERMEDIATE VALIDATION 
    profiles_count = executors_helpers.hp_get_profiles_count(ip, options, username, password)
    print(f"--> 🗑 HP subprocess: profile purge results -- Profiles count: {profiles_count} ")
    
    # !!3!! IMPORT EACH XML
    xml_files = sorted(glob.glob(os.path.join(local_dir, "*.xml")))
    if not xml_files:
        raise FileNotFoundError(f"❌ Local {local_dir} is empty, skip")

    for xml_file in xml_files:
        filename = os.path.basename(xml_file)
        import_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"mclient import {remote_dir}/{filename}"]
        
        subprocess.run(
            import_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    # !!4!! FINAL COMMIT
    commit_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient commit"]

    subprocess.run(
        commit_cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    # !!5!! FINAL VALIDATION
    profiles_count = executors_helpers.hp_get_profiles_count(ip, options, username, password)
    print(f"--> ✅ HP subprocess done! Profiles count: {profiles_count} ")

# ======================LINUX EXECUTORS===================== #
def deploy_linux_common(ip, options, username, password, local_dir, remote_dir):
    import subprocess

    # raises:
    # 1. RuntimeError — can't list /home or get users on remote host
    # 2. RuntimeError — no valid users with home dirs found
    # 3. subprocess.TimeoutExpired — any ssh/subprocess command timed out (10s)

    # local_dir -- aint used! idiotic abstraction

    # 1. Get /home dirs list via find
    find_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "find /home -maxdepth 1 -mindepth 1 -type d -printf '%f\\n'"]

    result_find = subprocess.run(find_cmd, capture_output=True, text=True, timeout=10, check=False)
    if result_find.returncode != 0:
        raise RuntimeError(f"Can't list /home on {ip}: {result_find.stderr}")

    dirs = [line.strip() for line in result_find.stdout.split('\n') if line.strip()]

    # 2. Get users list (UID>=1000) via getent
    users_cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "getent passwd | awk -F: '$3>=1000 {print $1}'"]

    result_users = subprocess.run(users_cmd, capture_output=True, text=True, timeout=10, check=False)
    if result_users.returncode != 0:
        raise RuntimeError(f"Can't get users on {ip}: {result_users.stderr}")

    users = [line.strip() for line in result_users.stdout.split('\n') if line.strip()]

    # 3. Intersect dirs & users -> target_users
    target_users = list(set(dirs) & set(users))

    if not target_users:
        raise RuntimeError(f"No valid users with home dirs on {ip}")

    # 4. For each user: handle /home/{user}/.local/share/remmina
    for user in target_users:
        remmina_dir = f"/home/{user}/.local/share/remmina"

        # OPTIMISITC: safe
        # CREATE A DIR FULL PATH
        # CLEAN IT

        # 4.1
        mkdir_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"mkdir -p {remmina_dir}"]

        subprocess.run(mkdir_cmd, capture_output=True, text=True, timeout=10, check=False)

        # 4.2
        clean_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"rm -rf {remmina_dir}/*"]

        subprocess.run(clean_cmd, capture_output=True, text=True, timeout=10, check=False)

        # 5. Copy /tmp/import_rdp/* -> /home/{user}/.local/share/remmina/
        # !!! files already on remote in /tmp/import_rdp
        cp_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"cp -r {remote_dir}/* {remmina_dir}/"]

        result_cp = subprocess.run(cp_cmd, capture_output=True, text=True, timeout=10, check=False)

        # 6. chown -R user:user on remmina dir
        chown_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"chown -R {user}:{user} {remmina_dir}"]

        subprocess.run(chown_cmd, capture_output=True, text=True, timeout=10, check=False)

        # 7. chmod 664 on each file
        chmod_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"chmod -R 664 {remmina_dir}/*"]

        subprocess.run(chmod_cmd, capture_output=True, text=True, timeout=10, check=False)

        # 8. Count files in remmina_dir and print per-user result
        count_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + options + [f"{username}@{ip}", f"ls -1 {remmina_dir}/*.remmina 2>/dev/null | wc -l"]

        result_count = subprocess.run(count_cmd, capture_output=True, text=True, timeout=10, check=False)

        if result_count.returncode == 0 and result_count.stdout.strip():
            count = result_count.stdout.strip()
            print(f"--> ✅ LINUX subprocess for user {user} done! Profiles count: {count}")
        else:
            print(f"--> ⚠️ Can't count profiles on {ip}")


    # 1. Get /home dirs list via find
    # 2. Get users list (UID>=1000) via getent
    # 3. Intersect dirs & users -> target_users
    # 4. For each user: handle /home/{user}/.local/share/remmina
    #    4a. If exists -> clean contents
    #    4b. If not -> mkdir -p
    # 5. Copy /tmp/import_rdp/* -> /home/{user}/.local/share/remmina/
    # 6. chown -R user:user on remmina dir
    # 7. chmod 664 on each file
    # 8. Count files -> print "profiles now N"