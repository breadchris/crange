import sqlite3

class Tag:
    def __init__(self, dbFile):
        self.db = sqlite3.connect(dbFile)
        self.headers = ("Location", "Line", "Kind", "Type", "Spelling", "Display", "USR")
        cursor = self.db.cursor()
        cursor.execute("PRAGMA synchronous = OFF;")
        cursor.execute("PRAGMA journal_mode = MEMORY;")

    def __del__(self):
        self.db.close()
    
    def find(self, name):
        cursor = self.db.cursor()
        cursor.execute("SELECT location, line, kind_name, type_name, spelling, display, usr FROM tags WHERE spelling=?", (name,))
        return cursor.fetchall()
        
    def find_refs(self, name):
        cursor = self.db.cursor()
        cursor.execute("SELECT location, line, kind_name, type_name, spelling, display, ref FROM tags WHERE ref IN (SELECT def FROM tags WHERE spelling=?) AND ref <> '' AND usr='' AND kind_name <> 'UNEXPOSED_EXPR' AND is_def=0", (name,))
        return cursor.fetchall()

    def find_kinds(self, tag_kind=None):
        cursor = self.db.cursor()
        if tag_kind is None:
            cursor.execute("SELECT DISTINCT kind_name FROM tags ORDER BY kind_name ASC")
        else:
            cursor.execute("SELECT location, line, kind_name, type_name, spelling, display FROM tags WHERE kind_name=?", (tag_kind,))
        return cursor.fetchall()
            
    def find_types(self, tag_type=None):
        cursor = self.db.cursor()
        if tag_type is None:
            cursor.execute("SELECT DISTINCT type_name FROM tags ORDER BY type_name ASC")
        else:
            cursor.execute("SELECT location, line, kind_name, type_name, spelling, display FROM tags WHERE type_name=?", (tag_type,))
        return cursor.fetchall()
