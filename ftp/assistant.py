import paramiko
import os

class SFTPAssistant:
    def __init__(self, local, ssh):
        '''
            Utility class; connects to a remote host given the appropriate local
            and remote folder prefixes. For the Google Cloud instances, the 
            prefix is probably "../backup"; the client prefix shouldn't be known 
            except by the client.
        '''
        self.l_path = local
        self.ssh_file = ssh

    def connect(self, ip, remote, username):
        self.host = ip
        self.r_path = remote
        self.u_name = username
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname=ip,
                username=username,
                key_filename=self.ssh_file
            )
            self.ssh_client = ssh_client

            ftp_client = ssh_client.open_sftp()
            self.ftp_client = ftp_client
            return 1
        except:
            return 0

    def close(self):
        if self.ssh_client:
            self.ssh_client.close()
        if self.ftp_client:
            self.ftp_client.close()
        
        self.host = None
        self.r_path = None
        self.u_name = None
        self.ssh_client = None
        self.ftp_client = None

    def get(self, file):
        if not self.ssh_client or not self.ftp_client:
            raise Exception

        self.ftp_client.get(
            os.path.join(self.r_path, file),
            os.path.join(self.l_path, file)
        )

    def put(self, file):
        if not self.ssh_client or not self.ftp_client:
            raise Exception

        self.ftp_client.put(
            os.path.join(self.l_path, file),
            os.path.join(self.r_path, file)
        )

    def mkdir(self, dir):
        if not self.ssh_client or not self.ftp_client:
            raise Exception

        self.ftp_client.mkdir(
            os.path.join(self.r_path, dir)
        )

    def upload_all(self):
        for root, dirs, files in os.walk(self.l_path, topdown=True):
            # go through all files and transfer them to remote
            for dir_file in files:
                path = os.path.join(root, dir_file)
                self.put(path[len(self.l_path):])

            # go through all directories and create them on remote
            for sub_dir in dirs:
                sub_dir_path = os.path.join(root, sub_dir)
                self.mkdir(sub_dir_path[len(self.l_path):])

    def download_all(self):
        raise Exception