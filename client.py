"""torrent客户端"""
# 控制下载开始与暂停，控制相关参数
class WbtClient():

    def __init__(self):
        self.torrent_list = []

    def add_torrent(self, torrent):
        self.torrent_list.append(torrent)