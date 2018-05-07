from connection import SFTPConnection

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
def run_consensus(leader, peers):
    print "Running consensus with leader", leader
    print "All IPs:", peers
    pass
