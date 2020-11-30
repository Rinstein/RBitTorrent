from torrent import Torrent
from metainfo import Metainfo

if __name__ == '__main__':
    torrent_name = './resource/Haywyre-Panorama_Form.torrent'
    torrent_name = './resource/Berklee Online.torrent'
    torrent_name = './resource/BLUMBROS X MAKJ - LS6.torrent'
    #metainfo = Metainfo(torrent_name)
    #print(metainfo.info)
    torrent = Torrent(Metainfo(torrent_name))
    torrent.start_torrent()