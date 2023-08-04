from server.knowledge_base.utils import (get_vs_path, get_kb_path, get_doc_path)
import os
import sqlite3
from configs.model_config import KB_ROOT_PATH
import datetime
import shutil

SUPPORTED_VS_TYPES = ["faiss", "milvus"]
DB_ROOT = os.path.join(KB_ROOT_PATH, "info.db")


# TODO: 知识库信息入库

def list_kbs_from_db():
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''SELECT KB_NAME
                  FROM KNOWLEDGE_BASE
                  WHERE FILE_COUNT>0  ''')
    kbs = [i[0] for i in c.fetchall() if i]
    conn.commit()
    conn.close()
    return kbs

def add_kb_to_db(kb_name, vs_type):
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    # Create table
    c.execute('''CREATE TABLE if not exists KNOWLEDGE_BASE
                 (ID INTEGER  PRIMARY KEY AUTOINCREMENT,
                 KB_NAME TEXT, 
                 VS_TYPE TEXT, 
                 FILE_COUNT INTEGER,
                 CREATE_TIME DATETIME) ''')
    # Insert a row of data
    c.execute(f"""INSERT INTO KNOWLEDGE_BASE 
                  (KB_NAME, VS_TYPE, FILE_COUNT, CREATE_TIME)
                  VALUES 
                  ('{kb_name}','{vs_type}',0,'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')""")
    conn.commit()
    conn.close()


def kb_exists(kb_name):
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''SELECT COUNT(*)
                  FROM KNOWLEDGE_BASE
                  WHERE KB_NAME="{kb_name}"  ''')
    status = True if c.fetchone()[0] else False
    conn.commit()
    conn.close()
    return status


def load_kb_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''SELECT KB_NAME, VS_TYPE
                  FROM KNOWLEDGE_BASE
                  WHERE KB_NAME="{kb_name}"  ''')
    resp = c.fetchone()
    if resp:
        kb_name, vs_type = resp
    else:
        kb_name, vs_type = None, None
    conn.commit()
    conn.close()
    return kb_name, vs_type


def delete_kb_from_db(kb_name):
    conn = sqlite3.connect(DB_ROOT)
    c = conn.cursor()
    c.execute(f'''DELETE
                  FROM KNOWLEDGE_BASE
                  WHERE KB_NAME="{kb_name}"  ''')
    conn.commit()
    conn.close()
    return True


class KnowledgeBase:
    def __init__(self,
                 knowledge_base_name: str,
                 vector_store_type: str,
                 ):
        self.kb_name = knowledge_base_name
        if vector_store_type not in SUPPORTED_VS_TYPES:
            raise ValueError(f"暂未支持向量库类型 {vector_store_type}")
        self.vs_type = vector_store_type
        self.kb_path = get_kb_path(self.kb_name)
        self.doc_path = get_doc_path(self.kb_name)
        if self.vs_type in ["faiss"]:
            self.vs_path = get_vs_path(self.kb_name)
        elif self.vs_type in ["milvus"]:
            pass

    def create(self):
        if not os.path.exists(self.doc_path):
            os.makedirs(self.doc_path)
        if self.vs_type in ["faiss"]:
            if not os.path.exists(self.vs_path):
                os.makedirs(self.vs_path)
            add_kb_to_db(self.kb_name, self.vs_type)
        elif self.vs_type in ["milvus"]:
            # TODO: 创建milvus库
            pass
        return True

    @classmethod
    def exists(cls,
               knowledge_base_name: str):
        return kb_exists(knowledge_base_name)

    @classmethod
    def load(cls,
             knowledge_base_name: str):
        kb_name, vs_type = load_kb_from_db(knowledge_base_name)
        return cls(kb_name, vs_type)

    @classmethod
    def delete(cls,
               knowledge_base_name: str):
        kb = cls.load(knowledge_base_name)
        if kb.vs_type in ["faiss"]:
            shutil.rmtree(kb.kb_path)
        elif kb.vs_type in ["milvus"]:
            # TODO: 删除milvus库
            pass
        status = delete_kb_from_db(knowledge_base_name)
        return status

    @classmethod
    def list_kbs(cls):
        return list_kbs_from_db()


if __name__ == "__main__":
    # kb = KnowledgeBase("123", "faiss")
    # kb.create()
    kb = KnowledgeBase.load(knowledge_base_name="123")
    print()
