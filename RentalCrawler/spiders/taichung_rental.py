from bs4 import BeautifulSoup
from scrapy_twrh.spiders.rental591 import Rental591Spider, util
import requests
import os
from dotenv import load_dotenv
from supabase import create_client, Client


class TaichungRentalSpider(Rental591Spider):
    name = 'taichung_rental'

    def __init__(self):
        # 指定台中市作為目標城市
        super().__init__(
            target_cities=['台中市'],
        )

        # 指定要爬取的區域、價格範圍和屋主直租
        self.filter_params = {
            'section': '103,102,101,98,99',  # 中區,西區,北屯區,東區,北區的代碼
            'price': '10000_15000',  # 租金範圍10000-15000
            'shType': 'host',  # 屋主直租
        }

        self.max_page = 1  # 限制爬取頁數

        self.dup_house_ids = set()

        load_dotenv()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(
            self.supabase_url, self.supabase_key)

        # 從 supabase 撈出全部 house_id
        data = self.supabase.table('rental_house').select('house_id').execute()
        for row in data.data:
            self.dup_house_ids.add(row['house_id'])

        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    # 取得台中市的租屋列表請求
    def gen_list_request_args(self, rental_meta):
        args = super().gen_list_request_args(rental_meta)

        # 將URL參數添加到請求URL中
        url = args['url']
        filter_params = '&'.join(
            [f"{k}={v}" for k, v in self.filter_params.items()])
        args['url'] = f"{url}&{filter_params}"

        return args

    # 只取第一頁的資料
    def default_parse_list(self, response):
        meta = response.meta['rental']

        if meta.page >= self.max_page:
            return

        yield self.gen_list_request(util.ListRequestMeta(
            meta.id,
            meta.name,
            1,
        ))

        regular_houses = self.gen_regular_house(response)

        for house in regular_houses:
            house_id = house['house_id']
            raw = house['raw']
            if house_id not in self.dup_house_ids:
                self.dup_house_ids.add(house_id)
                info = self.gen_house_info(raw)
                info['house_id'] = house_id
                if self.discord_webhook_url:
                    self.send_discord_webhook(self.discord_webhook_url, info)
                yield info

    def gen_house_info(self, raw):
        soup = BeautifulSoup(raw, "lxml")

        # 物件網址
        url = ""
        link_tag = soup.find("a", class_="link v-middle")
        if link_tag and link_tag.get("href"):
            url = link_tag.get("href").strip()

        # 標題
        title = ""
        if link_tag:
            title = link_tag.text.strip()

        # 第一張圖片網址
        img_url = ""
        img_tag = soup.find("ul", class_="image-list")
        if img_tag:
            first_img = img_tag.find("img", attrs={"data-src": True})
            if first_img:
                img_url = first_img["data-src"]

        # 價格
        price = ""
        price_tag = soup.find("strong", class_="text-26px font-arial")
        if price_tag:
            price = price_tag.text.strip()
        unit_tag = soup.find("span", class_="text-14px ml-2px")
        if unit_tag:
            unit = unit_tag.text.strip()
            price += unit

        # 物件房型描述
        room_type = ""
        room_type_tag = soup.find("div", class_="item-info-txt")
        if room_type_tag:
            tmp = room_type_tag.text.strip()
            if tmp:
                room_type = tmp

        # Tag 標籤（可選擇性提取）
        tag_list = []
        for t in soup.select('.item-info-tag .tag'):
            tag_list.append(t.text.strip())

        # 屋主與更新時間
        owner_info = ""
        role_name = soup.find(
            "div", class_="item-info-txt role-name ml-2px mt-2px mb-8px")
        if role_name:
            owner_info = " ".join([t.text for t in role_name.find_all("span")])

        return {
            'url': url,
            'title': title,
            'img_url': img_url,
            'price': price,
            'room_type': room_type,
            'tag_list': tag_list,
            'owner_info': owner_info,
        }

    def send_discord_webhook(self, webhook_url, info):
        data = {
            "embeds": [
                {
                    "title": info['title'],
                    "url": info['url'],
                    "description": f"💰{info['price']}  \n\n{info['room_type']} \n\n{' '.join(info['tag_list'])}",
                    "image": {"url": info['img_url']} if info['img_url'] else {},
                }
            ]
        }
        resp = requests.post(webhook_url, json=data)
        if not resp.ok:
            print("Failed to send Discord webhook:",
                  resp.status_code, resp.text)
