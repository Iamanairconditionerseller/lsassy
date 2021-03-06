# Author:
#  Romain Bentz (pixis - @hackanddo)
# Website:
#  https://beta.hackndo.com


class ImpacketFile:
    def __init__(self):
        self._conn = None
        self._fpath = None
        self._currentOffset = 0
        self._total_read = 0
        self._tid = None
        self._fid = None
        
        self._buffer_min_size = 1024 * 8
        self._buffer_data = {
            "offset": 0,
            "size": 0,
            "buffer": ""
        }

    def open(self, connection, share_name, fpath):
        self._conn = connection
        self._fpath = fpath
        self._tid = self._conn.connectTree(share_name)
        self._fid = self._conn.openFile(self._tid, self._fpath)
        self._fileInfo = self._conn.queryInfo(self._tid, self._fid)
        self._endOfFile = self._fileInfo.fields["EndOfFile"]


    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def read(self, size):
        if size == 0:
            return b''

        if (self._buffer_data["offset"] <= self._currentOffset <= self._buffer_data["offset"] + self._buffer_data["size"]
                and self._buffer_data["offset"] + self._buffer_data["size"] > self._currentOffset + size):
            value = self._buffer_data["buffer"][self._currentOffset - self._buffer_data["offset"]:self._currentOffset - self._buffer_data["offset"] + size]
        else:
            self._buffer_data["offset"] = self._currentOffset

            """
            If data size is too small, read self._buffer_min_size bytes and cache them
            """
            if size < self._buffer_min_size:
                value = self._conn.readFile(self._tid, self._fid, self._currentOffset, self._buffer_min_size)
                self._buffer_data["size"] = self._buffer_min_size
                self._total_read += self._buffer_min_size
                
            else:
                value = self._conn.readFile(self._tid, self._fid, self._currentOffset, size + self._buffer_min_size)
                self._buffer_data["size"] = size + self._buffer_min_size
                self._total_read += size
            
            self._buffer_data["buffer"] = value

        self._currentOffset += size

        return value[:size]

    def close(self):
        self._conn.close()

    def seek(self, offset, whence=0):
        if whence == 0:
            self._currentOffset = offset
        elif whence == 1:
            self._currentOffset += offset
        elif whence == 2:
            self._currentOffset = self._endOfFile - offset
        else:
            raise Exception('Seek function whence value must be between 0-2')

    def tell(self):
        return self._currentOffset