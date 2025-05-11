import sqlite3
import json

class HouseDedupPipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect('rental_house.sqlite3')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS rental_house (
                house_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                img_url TEXT,
                price TEXT,
                room_type TEXT,
                tag_list TEXT,
                owner_info TEXT
            );
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.c.execute('SELECT house_id FROM rental_house WHERE house_id=?', (item['house_id'],))
        if self.c.fetchone():
            raise DropItem(f"Duplicate house_id {item['house_id']}")
        self.c.execute('INSERT INTO rental_house VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
            item['house_id'],
            item.get('url', ''),
            item.get('title', ''),
            item.get('img_url', ''),
            item.get('price', ''),
            item.get('room_type', ''),
            json.dumps(item.get('tag_list', [])),
            item.get('owner_info', '')
        ))
        self.conn.commit()
        return item