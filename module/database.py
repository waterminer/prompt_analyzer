import sqlite3

class Database():
    def __init__(self,file_path="./danbooru_tag_db/database.db") -> None:
        self.file_path = file_path
        self._database = None
    
    def _check_on_connect(func):
        def wrap(self,*args,**kwargs):
            if self._database is None:
                raise ConnectionClosedError
            return func(self,*args,**kwargs)
        return wrap

    def __enter__(self):
        self._database = sqlite3.connect(self.file_path)
        return self
    
    def  __exit__(self, exc_type, exc_value, traceback):
        self._database.close()
        self._database = None
    
    @_check_on_connect
    def query(self,sql):
        return self._database.execute(sql)

class ConnectionClosedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)