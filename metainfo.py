import bencodepy, os, hashlib,copy

"""定义解析torrent文件类"""


class Metainfo():

    def __init__(self, file_name):
        """参数定义"""
        self.announce = None  # Tracker服务器地址
        self.info = None  # torrent文件中的info0字节内容
        self.info_hash = None  # info字节内容的sha1 hash值
        self.name = None  # 资源若为单个资源文件，则为文件名称，若为资源文件夹，则为最顶层目录名称

        """读取torrent文件内容"""
        with open(file_name, 'rb') as f:
            content = f.read()
        content = bencodepy.decode(content)
        self.announce = content[b'announce'].decode('utf-8')
        self.announce_list = [t.decode('utf-8') for t in self.parse_list(content[b'announce-list'])]
        self.info = self._decode_info_dict(content[b'info'])
        self.info_hash = hashlib.sha1(bencodepy.encode(content[b'info'])).digest()

    def _decode_info_dict(self, d):
        info = {}

        info['piece_length'] = d[b'piece length']

        SHA_LEN = 20
        pieces_shas = d[b'pieces']
        info['pieces'] = [pieces_shas[i:i + SHA_LEN]
                          for i in range(0, len(pieces_shas), SHA_LEN)]

        self.name = d[b'name'].decode('utf-8')

        files = d.get(b'files')  # 有files则为多文件资源，否则为单文件资源
        if not files:
            info['format'] = 'SINGLE_FILE'
            info['files'] = None
            info['length'] = d[b'length']
        else:
            info['format'] = 'MULTIPLE_FILE'
            info['files'] = []
            for f in d[b'files']:
                path_segments = [v.decode('utf-8') for v in f[b'path']]
                info['files'].append({
                    'length': f[b'length'],
                    'path': os.path.join(*path_segments)
                })
            info['length'] = sum(f['length'] for f in info['files'])

        return info

    # def get_piece_length(self, index):
    #     num_pieces = len(self.info['pieces'])
    #     piece_length = self.info['piece_length']
    #     if index == num_pieces - 1:     # last piece
    #         return (self.info['length'] - (num_pieces - 1) * piece_length)
    #     return piece_length

    def divide_ele_list(self,t_list):
        """
        划分两个
        :param t_list:
        :return:[ele1,...,eleN],[list1,...,listN]
        """
        ele_list = []
        list_list = []
        for i in t_list:
            if type([]) == type(i):
                list_list.append(i)
            else:
                ele_list.append(i)
        return ele_list,list_list

    def parse_list(self,t_list):
        """
        解析嵌套的list为单个元素的list
        :param t_list:嵌套列表或者单个元素
        :return:
        """

        r = []
        ele_list,list_list = self.divide_ele_list(t_list)
        r += ele_list
        while len(list_list) > 0:
            t = []
            for i in list_list:
                a,b = self.divide_ele_list(i)
                r += a
                t += b
            list_list = copy.deepcopy(t)
        return r