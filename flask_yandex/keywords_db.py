import sqlite3

# texts
# text_id | txt

# keywords
# keyword_id | keyword

# texts_keywords
# text_id | keyword_id


DB_NAME = 'keywords.db'


class KeywordsDB():

    def __init__(self):
        self.db_connection = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
        self.__create_tables()

    def __del__(self):
        self.db_connection.close()

    def add(self, text, keywords):
        self.db_cursor.execute("INSERT OR IGNORE INTO texts (txt) VALUES (?)", (text,))
        for keyword in keywords:
            self.db_cursor.execute("INSERT OR IGNORE INTO keywords (keyword) VALUES (?)", (keyword,))
        self.db_connection.commit()

        self.db_cursor.execute('SELECT text_id FROM texts WHERE txt=?', (text,))
        text_id = self.db_cursor.fetchone()[0]

        for keyword in keywords:
            self.db_cursor.execute(
                '''INSERT OR IGNORE INTO texts_keywords (text_id,keyword_id)
                VALUES (?, (SELECT keyword_id FROM keywords WHERE keyword=?))''',
                (text_id, keyword)
            )
        self.db_connection.commit()

        # self.db_cursor.execute(
        #     '''SELECT t.txt, k.keyword FROM texts_keywords as tk
        #     JOIN texts as t ON tk.text_id=t.text_id
        #     JOIN keywords as k ON tk.keyword_id=k.keyword_id'''
        # )
        # for row in self.db_cursor.fetchall():
        #     print(row)

    def __create_tables(self):
        self.db_cursor.execute(
            '''CREATE TABLE IF NOT EXISTS texts (
                text_id INTEGER PRIMARY KEY AUTOINCREMENT,
                txt TEXT UNIQUE )'''
        )
        self.db_cursor.execute(
            '''CREATE TABLE IF NOT EXISTS keywords (
                keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword VARCHAR(255) UNIQUE )'''
        )
        self.db_cursor.execute(
            '''CREATE TABLE IF NOT EXISTS texts_keywords (
                text_id INTEGER NOT NULL,
                keyword_id INTEGER NOT NULL,
                CONSTRAINT texts_keywords_pk PRIMARY KEY (text_id, keyword_id),
                FOREIGN KEY (text_id) REFERENCES texts (text_id),
                FOREIGN KEY (keyword_id) REFERENCES keywords (keyword_id))'''
        )
        self.db_connection.commit()
