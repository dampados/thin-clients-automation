# =======================HP HELPERS======================= #
def hp_purge_profiles(ip, options, username, password):
    import subprocess
    
    commands = (
        "mclient delete root/ConnectionType/freerdp/connections\n"
        "mclient commit"
    )
    
    cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", commands]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    
    return result

def hp_get_profiles_count(ip, options, username, password):
    import subprocess
    
    cmd = [
        "sshpass", "-p", password,
        "ssh"
    ] + options + [f"{username}@{ip}", "mclient get root/ConnectionType/freerdp/connections"]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    
    lines = result.stdout.strip().split('\n')
    return len([line for line in lines if line.strip()])
