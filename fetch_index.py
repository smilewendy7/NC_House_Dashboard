import re 
import csv 
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

INDEX_URL = "https://www.ncrealtors.org/category/market-statistics/"
OUTFILE = "reports_index.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

MONTHS = {
"january": "01", "february": "02", "march": "03", "april": "04",
"may": "05", "june": "06", "july": "07", "august": "08",
"september": "09", "october": "10", "november": "11", "december": "12"
}

def get_report_month(title: str) -> str | None: 
    """
    Try to extract YYYY-MM from titles like:
    'December 2025 NC Housing Report'
    """
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
                  title, flags=re.IGNORECASE)
    
    if not m :
        return None
    
    month_name = m.group(1).lower()
    year = m.group(2)
    mm = MONTHS.get(month_name)
    return f"{year}-{mm}" if mm else None


def main():

    # 第一步： 抓取网页内容，不是200报错
    r = requests.get(INDEX_URL, headers=headers, timeout=30)
    r.raise_for_status()
    print("status:", r.status_code)

    """
        第二步： 解析标题：  第一步返回的 返回的内容先用 BeautifulSoup 解析成dom[爷父子孙树层级形式
        beatufulsoup 返回一个list, 找到所有的 div.itemWrap → p → a   beautifulsoup.select 选中Html 标签 
    """

    # 用beautiful soup 解析 
    soup = BeautifulSoup(r.text, "html.parser")
    """ 
        第三步： 循环记下来每条目录的名字， 时间， url
        做成一个json格式的数据存储： 
        [{   
            date: 
            url:
            时间戳： 
            data source: 
        }, {...}, {...}]
    """
    rows = []

    for a in soup.select("div.itemWrap p a"):
        # print("a", a.get_text(strip=True))
        title = a.get_text(strip=True)
        report_month = get_report_month(title)
        url = a.get("href")
        rows.append({
            "title" : title,
            "url": url,
            "report_month": report_month,
            "fetched_at": datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S"),
            "source": "ncrealtors_market_statistics"
        })

    # write csv
    # filenames：表头
    fieldnames = ["title", "url", "report_month", "fetched_at", "source"]
    # with 自动关闭文件
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTFILE}")





# 如果直接run 这个文件， 就会直接运行main函数； 如果只是import 不跑main 函数
if __name__ == "__main__":
    main()
