from bs4 import BeautifulSoup
from scrapy import Request
from scrapy_twrh.spiders.rental591 import Rental591Spider, util, list_mixin
from scrapy_twrh.items import RawHouseItem, GenericHouseItem
from scrapy_twrh.spiders import enums
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
  
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
            'price': '10000_17000',  # 租金範圍10000-17000  
            'shType': 'host', # 屋主直租
        }
        
        self.max_page = 1  # 限制爬取頁數 
    
    # 取得台中市的租屋列表請求
    def gen_list_request_args(self, rental_meta):  
        args = super().gen_list_request_args(rental_meta)  
          
        # 將URL參數添加到請求URL中  
        url = args['url']  
        filter_params = '&'.join([f"{k}={v}" for k, v in self.filter_params.items()])  
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
    
        # promotion_houses = self.gen_promotion_house(response)  
        regular_houses = self.gen_regular_house(response)  
    
        for house in regular_houses:  
            house_id = house['house_id']
            raw = house['raw']
            if house_id not in self.requested_houses:
                self.requested_houses.add(house_id)
                yield self.gen_house_info(raw)
    
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
            first_img = img_tag.find("img", attrs={"data-src":True})
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
        role_name = soup.find("div", class_="item-info-txt role-name ml-2px mt-2px mb-8px")
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
    
    # def gen_detail_request_args(self, rental_meta: util.DetailRequestMeta):
    #     # https://rent.591.com.tw/17122751
    #     url = "{}{}".format(util.DETAIL_ENDPOINT, rental_meta.id)

    #     # don't filter as 591 use 30x to indicate house status...
    #     return {
    #         'dont_filter': True,
    #         'url': url,
    #         'errback': self.error_handler,
    #         'meta': {
    #             'rental': rental_meta,
    #             'handle_httpstatus_list': [400, 404, 302, 301],
    #             'playwright': True,
    #             # 'playwright_include_page': True,
    #             'playwright_page_methods': [
    #                 PageMethod('wait_for_load_state', 'networkidle'),
    #             ],
    #             'playwright_page_init_callback': self.enable_playwright
    #         },
    #     }
    
    # def gen_list_request(self, rental_meta) -> Request:
    #     args = {
    #         'callback': self.parse_list,
    #         'meta': {
    #             'rental': rental_meta,
    #             'handle_httpstatus_list': [400, 404, 302, 301],
    #             'playwright': True,
    #             'playwright_page_methods': [
    #                 PageMethod('wait_for_load_state', 'networkidle'),
    #             ],
    #             'playwright_page_init_callback': self.enable_playwright,
    #         },
    #         'priority': self.DEFAULT_LIST_PRIORITY,
    #         **self.gen_list_request_args(rental_meta)  # 合併其他 args
    #     }
    #     return Request(**args)