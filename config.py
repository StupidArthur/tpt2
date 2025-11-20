# encoding: utf-8

import base64


class Config(object):

    host: str
    https_header: str
    wss_header: str
    user: str
    pwd: str
    cookie: str


    def __init__(self):
        self.host = "tpt.supcon.com"
        self.https_header = f"http://{self.host}"
        self.wss_header = f"ws://{self.host}"
        self.user = "15700078644"
        self.pwd = base64.b64encode("arthur".encode()).decode()
        self.cookie = "tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B"

    def set_user(self, user: str, pwd: str):
        self.user = user
        self.pwd = base64.b64encode(pwd.encode()).decode()

    def set_host(self, s: str):
        self.host = s
        self.https_header = f"http://{self.host}"
        self.wss_header = f"ws://{self.host}"

    def set_env(self, env_name: str):
        """

        Args:
            env_name: saas, x86

        Returns:

        """
        if env_name == 'saas':
            self.set_user(user='15700078644', pwd='arthur')
            self.set_host('tpt.supcon.com')
            self.cookie = "tenant-id=ATL43NW8; TptSaasUserTenantryId=ATL43NW8; JSESSIONID=14F14333BF90F5FAE1B94575EA14CD4B;"
        elif env_name == 'x86':
            self.set_user(user='arthur', pwd='arthur')
            self.set_host('10.16.11.45:31501')
            self.cookie = "_ga=GA1.1.739637345.1762146720; _ga_YFKNQX5E65=GS2.1.s1762218416$o5$g1$t1762218416$j60$l0$h0;"
        elif env_name == 'arm':
            self.set_user(user='arthur', pwd='arthur')
            self.set_host('10.16.11.46:31501')
            self.cookie = ''


o_config = Config()