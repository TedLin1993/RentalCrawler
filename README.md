# RentalCrawler - 591 租屋自動化爬蟲

這是一個基於 Python Scrapy 框架開發的租屋爬蟲工具，專門用於監控 **591 租屋網**上的台中市租屋物件。當偵測到符合條件的新物件時，系統會自動儲存至資料庫並透過 Discord 發送即時通知。

## 核心功能

* **精準篩選**：預設鎖定台中市特定區域（中區、西區、北屯區、東區、北區）、租金範圍 10,000 - 15,000 元且為屋主直租的物件。
* **即時通知**：整合 Discord Webhook，發現新物件時立即推送詳細資訊與圖片。
* **資料去重**：串接 Supabase (PostgreSQL) 資料庫，自動比對物件 ID，確保不會重複抓取或發送通知。
* **API 觸發**：內建 Flask 伺服器，提供 API 接口可遠端啟動爬蟲任務。
* **容器化支援**：提供 Dockerfile，支援快速部署至雲端環境。

## 技術棧

* **Language**: Python 3.11
* **Framework**: Scrapy
* **Libraries**: BeautifulSoup4, Requests, Flask, Supabase Python Client
* **Database**: Supabase (PostgreSQL)

## 環境設定

在執行專案前，請先建立 `.env` 檔案並設定以下環境變數：

```env
SUPABASE_URL=你的_Supabase_專案網址
SUPABASE_KEY=你的_Supabase_API_金鑰
DISCORD_WEBHOOK_URL=你的_Discord_Webhook_網址

```

## 安裝與執行

### 本地開發

1. **安裝依賴套件**：
```bash
pip install -r requirements.txt

```


2. **啟動 API 伺服器**：
```bash
python main.py

```


3. **觸發爬蟲**：
發送一個 POST 請求至 `http://localhost:8080/run-crawler`。

### 使用 Docker 部署

1. **構建映像檔**：
```bash
docker build -t rental-crawler .

```


2. **執行容器**：
```bash
docker run -p 8080:8080 --env-file .env rental-crawler

```



## 租屋條件自定義

您可以編輯 `RentalCrawler/spiders/taichung_rental.py` 中的 `self.filter_params` 來修改搜尋條件：

* `section`: 區域代碼。
* `price`: 租金範圍（例如 `5000_10000`）。
* `shType`: 物件類型（預設 `host` 為屋主直租）。

## 專案結構

* `main.py`: Flask 入口點，負責管理爬蟲進程。
* `RentalCrawler/spiders/taichung_rental.py`: 主要爬蟲邏輯與 Discord 通知功能。
* `RentalCrawler/pipelines.py`: 負責將資料存入 Supabase。
* `Dockerfile`: 定義映像檔構建流程。
