import os
import sqlite3
import json
from dotenv import load_dotenv
from scrapy.exceptions import DropItem
from supabase import create_client


class HouseDedupPipeline:
    def open_spider(self, spider):
        # 建立 supabase 連線
        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.supabase.table('rental_house').insert({
            "house_id": item['house_id'],
            "url": item.get('url', ''),
            "title": item.get('title', ''),
            "img_url": item.get('img_url', ''),
            "price": item.get('price', ''),
            "room_type": item.get('room_type', ''),
            "tag_list": json.dumps(item.get('tag_list', [])),
            "owner_info": item.get('owner_info', ''),
        }).execute()
        return item
