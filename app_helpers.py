# file helper_functions.py
import json

def load_inventory(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def get_base_ssh_command(host_data, inventory):
    # 1 get connection options (old, new clients)
    ssh_profile_key = host_data.get('ssh_profile', 'modern')
    ssh_profile = next((profile for profile in inventory['ssh_profiles'] if profile['profile'] == ssh_profile_key), None)

    if not ssh_profile:
        print(f"SSH profile {ssh_profile_key} not found!")
        return None

    # 2 get credentials for this exact host
    cred_name_key = host_data.get('credential', 'default_root')
    cred = next((cred for cred in inventory['credentials'] if cred['name'] == cred_name_key), None)
    
    if not cred:
        print(f"Credentials {cred_name_key} not found!")
        return None
    
    username = cred['username']
    password = cred['password']
    
    # ==================================FINALLY=====================================================
    base_cmd = [
            "sshpass", "-p", password,
            "ssh"
        ] + ssh_profile['options'] + [f"{username}@{host_data['ip']}"]
        
    return base_cmd


# =======================DATA HELPERS======================= #
# raise:
# 1. ValueError exception, if broken inventory
def get_type_config(host, inventory):
    type_name = host.get('type')

    if not inventory.get('types'):
        raise ValueError("No 'types' section in inventory!") 
    type_config = next((t for t in inventory['types'] if t['name'] == type_name), None)
    if not type_config:
        print(f"⚠️ Type '{type_name}' not found, using first")
        type_config = inventory['types'][0]
    return type_config

def get_credential(host, inventory):
    cred_name = host.get('credential', 'default_root')
    if not inventory.get('credentials'):
        raise ValueError("No 'credentials' section in inventory!")
    cred = next((c for c in inventory['credentials'] if c['name'] == cred_name), None)
    if not cred:
        print(f"⚠️ Credentials '{cred_name}' not found, using first")
        cred = inventory['credentials'][0]
    return cred

def get_ssh_profile(host, inventory):
    profile_name = host.get('ssh_profile', 'modern')
    if not inventory.get('ssh_profiles'):
        raise ValueError("No 'ssh_profiles' section in inventory!")
    profile = next((p for p in inventory['ssh_profiles'] if p['profile'] == profile_name), None)
    if not profile:
        print(f"⚠️ SSH profile '{profile_name}' not found, using first")
        profile = inventory['ssh_profiles'][0]
    return profile

