"""单个torrent资源的解析类"""
from metainfo import Metainfo
from tracker import Tracker
import socket
from tools import Tools
from config import CONFIG


class Torrent():

    def __init__(self, metainfo: Metainfo):
        self.meta_info = metainfo
        self.tracker = Tracker(self.meta_info.announce)
        self.tracker_list = [Tracker(t_url) for t_url in self.meta_info.announce_list]

    def start_torrent(self):
        peers_list = self.tracker.send_announce_request(self)
        self.connect_peers(peers_list)
        # todo 这之中含有udp://开头的协议，暂不处理
        # for tracker in self.tracker_list:
        #     peers_list = tracker.send_announce_request(self)
        #     self.connect_peers(peers_list)

    def connect_peers(self, peers_list):
        print('获得的peer的地址', peers_list)
        for peer in peers_list:
            print('连接peer地址', peer)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            try:
                self.sock.connect((peer['ip'], peer['port']))
                msg = Tools.build_handshake(self.meta_info.info_hash, CONFIG['peer_id'])
                self.sock.send(msg)
                print('发送请求')
                try:
                    data = self.sock.recv(1024)
                    print(data)
                    print(self.parse_handshake(data))
                except Exception as e:
                    print('接收数据失败', e)
            except Exception as e:
                print('连接peer失败', e)

    def parse_handshake(self, data):
        """Parse a handshake and return bytes consumed, or raise exception."""
        # TODO: check for incomplete message
        pstrlen = int(data[0])
        handshake_data = data[1: 49 + pstrlen]
        handshake = Tools.decode_handshake(pstrlen, handshake_data)
        # self.handle_handshake_ok()
        # 检测

        return (1 + len(handshake_data))
