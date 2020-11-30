"""负责连接Tracker，解析tracker内容"""
import requests
import config
import bencodepy
import struct
import socket


class Tracker():

    def __init__(self, announce):
        self.announce = announce
        self.tracker_id = None

    def send_announce_request(self, torrent):
        url_param = {
            'info_hash': torrent.meta_info.info_hash,
            'peer_id': config.CONFIG['peer_id'],
            'port': 6881,
            'uploaded': '0',
            'downloaded': '0',
            'left': str(torrent.meta_info.info['length'])
        }
        print(url_param)
        url = self.announce
        http_resp, sock = None, None
        url = self.announce
        url = url.replace('udp', 'http')
        print('Tracker address: ', url)
        http_resp = requests.get(url, url_param)
        # if "http" in url:
        #     http_resp = requests.get(url, url_param)
        # else:
        #     # todo 当udp开头时，怎么构造请求
        #     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     sock.connect(url)
        #     data = bytes.decode(url_param)
        #     len_data = struct.pack('>', len(data))
        #     sock.send(len_data + data)
        #     http_resp = sock.recv()
        print('http_resp', http_resp)
        return self.handle_announce_responce(http_resp)

    def handle_announce_responce(self, http_resp):
        resp = bencodepy.decode(http_resp.text.encode('latin-1'))
        d = self.decode_announce_response(resp)

        peer_list = d['peers']
        return peer_list
        for peer_dict in d['peers']:
            # TODO: raise error or warning on port = 0?
            if peer_dict['ip'] and peer_dict['port'] > 0:
                # print(peer_dict)
                self.torrent.add_peer(peer_dict)

    @classmethod
    def decode_announce_response(cls, resp):
        d = {}

        if b'failure reason' in resp:
            raise AnnounceFailureError(resp[b'failure reason'].decode('utf-8'))

        d['interval'] = int(resp[b'interval'])
        d['complete'] = int(resp[b'complete']) if b'complete' in resp else None
        d['incomplete'] = (int(resp[b'incomplete'])
                           if b'incomplete' in resp else None)

        try:
            d['tracker_id'] = resp[b'tracker id'].decode('utf-8')
        except KeyError:
            d['tracker_id'] = None

        raw_peers = resp[b'peers']
        if isinstance(raw_peers, list):
            d['peers'] = cls.decode_dict_model_peers(raw_peers)
        elif isinstance(raw_peers, bytes):
            d['peers'] = cls.decode_binary_model_peers(raw_peers)
        else:
            raise AnnounceDecodeError('Invalid peers format: %s' % raw_peers)

        return d

    @staticmethod
    def decode_dict_model_peers(peers_dicts):
        return [{'ip': d[b'ip'].decode('utf-8'),
                 'port': d[b'port'],
                 'peer_id': d.get(b'peer id')}
                for d in peers_dicts]

    @staticmethod
    def decode_binary_model_peers(peers_bytes):
        fmt = '!BBBBH'
        fmt_size = struct.calcsize(fmt)
        if len(peers_bytes) % fmt_size != 0:
            raise AnnounceDecodeError('Binary model peers field length error')
        peers = [struct.unpack_from(fmt, peers_bytes, offset=ofs)
                 for ofs in range(0, len(peers_bytes), fmt_size)]

        return [{'ip': '%d.%d.%d.%d' % p[:4],
                 'port': int(p[4])}
                for p in peers]


class AnnounceFailureError(Exception):
    pass


class AnnounceDecodeError(Exception):
    pass
