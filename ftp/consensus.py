import json, shutil
from connection import InfoConnection, SFTPConnection
from json_helper import Crawler, diff

'''
    Consensus algorithm to be run on any server.

    Given the leader (this server) and peers, this algorithm does the following:
    1. Opens a connection to all peers
    2. Grabs a Crawler JSON description of all peers' backup directories
    3. Calculates the majority consensus for any and all files
    4. Updates itself to be correct
    5. Updates its peers to be correct

    We accomplish this by maintaining two dictionary objects; one for files and
    one for folders. Keys are paths to files and folders. Values take the form 
    of a dictionary describing if the leader has the file and the peers that
    disagree with the leader.
    
    {
        <path>: {
            leader_has: <boolean>,
            conflict: [ <ips> ]
        }
    }

    This allows us to easily calculate the consensus for this object: out of n
    peers, if `len(conflict)` > n/2, then this object is "correct".  Otherwise,
    the object should not be retained.

    Note that, by default, peers not listed in `conflict` are assumed to agree
    with the leader -- the object will not show up in the diff vs. peers that do
    agree. We also make one final optimization: we reduce n to the number of 
    peers that were reachable (not simply the list of all peers). This ensures 
    that we have a true majority where applicable.
'''
def run_consensus(leader, peers, username):
    print "Running consensus with leader", leader
    print "All IPs:", peers
    peers = filter(lambda k: k != leader, peers)

    BACKUP_DIR = "/home/" + username + "/backup"
    SSH_FILE = SSH_FILE

    '''
        Steps 1 and 2: connect to each peer and obtain the JSON descriptors.
    '''
    descriptors = {}
    for peer in peers:
        c = InfoConnection(peer)
        if not c.connect():
            continue
        descriptors[peer] = json.loads(c.get_json().replace("\'", "\""))

    '''
        Step 3: Calculate the majority consensus.
    '''
    n_peers = 1 + len(descriptors)
    leader_json = Crawler().dump(BACKUP_DIR)
    differences = {
        peer: diff(leader_json, descriptors[peer])
        for peer in descriptors
    }
    files = {}
    folders = {}
    for peer, difference in differences.items():
        (leader_files, leader_dirs) = differences[0]
        (server_files, server_dirs) = differences[1]
        for leader_file in leader_files:
            if leader_file not in files:
                files[leader_file] = {
                    'leader_has': True,
                    'conflict': []
                }
        for leader_dir in leader_dirs:
            if leader_dir not in folders:
                folders[leader_dir] = {
                    'leader_has': True,
                    'conflict': []
                }
        for server_file in server_files:
            if server_file not in files:
                files[server_file] = {
                    'leader_has': False,
                    'conflict': [peer]
                }
            else:
                files[server_file]['conflict'].append(peer)
            if server_dir not in folders:
                folders[server_dir] = {
                    'leader_has': False,
                    'conflict': [peer]
                }
            else:
                folders[server_file]['conflict'].append(peer)
    
    '''
        Steps 4 and 5: Update the leader and peers to be correct.

        4 intermediate steps:
            1. Remove files from any servers that shouldn't have them
            2. Remove folders from any servers that shouldn't have them
            3. Add folders for any servers that should have them
            4. Add files for any servers that should have them

        We need to remove objects when:
            1. Leader is correct and doesn't have the object
            2. Leader is wrong and does have the object
        We need to add objects when:
            1. Leader is correct and does have the object
            2. Leader is wrong and doesn't have the object
    '''
    all_folders = sorted(lambda d: d.count("/"), folders.keys())
    for file in files:
        if len(files[file]['conflict']) < n_peers / 2 == files[file]['leader_has']:
            continue
        for peer in peers:
            if files[file]['leader_has'] == peer in files[file]['conflict']:
                continue
            s = SFTPConnection(BACKUP_DIR, SSH_FILE)
            if not s.connect(peer, BACKUP_DIR, username):
                print "Couldn't remove", file, "from peer", peer
                continue
            s.rm(file)
        if files[file]['leader_has']:
            os.remove(file)
    for folder in reversed(all_folders):
        if len(folders[folder]['conflict']) < n_peers / 2 == folders[folder]['leader_has']:
            continue
        for peer in peers:
            if folders[folder]['leader_has'] == peer in folders[folder]['conflict']:
                continue
            s = SFTPConnection(BACKUP_DIR, SSH_FILE)
            if not s.connect(peer, BACKUP_DIR, username):
                print "Couldn't remove", folder, "from peer", peer
                continue
            s.rmdir(folder)
        if folders[folder]['leader_has']:
            os.rmdir(folder)
    for folder in all_folders:
        if len(files[file]['conflict']) < n_peers / 2 != folders[folder]['leader_has']:
            continue
        for peer in peers:
            if folders[folder]['leader_has'] != peer in folders[folder]['conflict']:
                continue
            s = SFTPConnection(BACKUP_DIR, SSH_FILE)
            if not s.connect(peer, BACKUP_DIR, username):
                print "Couldn't add", folder, "to peer", peer
                continue
            s.mkdir(folder)
        if not folders[folder]['leader_has']:
            os.mkdir(folder)
    for file in files:
        if len(files[file]['conflict']) < n_peers / 2 != files[file]['leader_has']:
            continue
        if not files[file]['leader_has']:
            received = False
            for peer in peers:
                if peer not in files[file]['conflict']:
                    continue
                s = SFTPConnection(BACKUP_DIR, SSH_FILE)
                if not s.connect(peer, BACKUP_DIR, username):
                    continue
                s.get(file)
                received = True
                break
            if not received:
                print "Couldn't get file", file, "from any peers"
                continue
        for peer in peers:
            if files[file]['leader_has'] != peer in files[file]['conflict']:
                continue
            s = SFTPConnection(BACKUP_DIR, SSH_FILE)
            if not s.connect(peer, BACKUP_DIR, username):
                print "Couldn't add", file, "to peer", peer
                continue
            s.put(file)