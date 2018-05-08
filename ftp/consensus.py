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
    '''
    # TODO
    for folder in sorted(lambda d: d.count("/"), folders):
        # leader is wrong
        if len(folders[folder]['conflict']) < n_peers / 2:     
            pass
        # leader is correct    
        else:
            if folders[folder]['leader_has']:
                shutil.rmtree(folder)
            else:
                os.makedirs(folder)
    for file in files:
        # leader is wrong
        if len(files[file]['conflict']) < n_peers / 2:
            pass
        # leader is correct
        else:
            if files[file]['leader_has']:
                os.remove(file)
            for peer in files[file]['conflict']:
                s = SFTPConnection(BACKUP_DIR, "../ssh/google_compute_engine")
                if not s.connect(server_ip, BACKUP_DIR, username):
                    continue
                s.get(file)