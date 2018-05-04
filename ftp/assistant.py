import paramiko

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
        ssh_client.connect(
            hostname=ip, 
            username=username, 
            key_filename=self.ssh_file
        )
        self.ssh_client = ssh_client

        ftp_client = ssh_client.open_sftp()
        self.ftp_client = ftp_client

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
            self.r_path + '/' + file,
            self.l_path + '/' + file
        )

    def put(self, file):
        if not self.ssh_client or not self.ftp_client:
            raise Exception

        self.ftp_client.put(
            self.l_path + '/' + file,
            self.r_path + '/' + file
        )