import csv 
import requests
from bs4 import BeautifulSoup
from utils import get_fetched_at

# 第一步： import reports_index.csv

# 第二步： 拿到每一个url, 打开Url - 拿到信息 - 写入csv

INDEX_CSV = "reports_index.csv"
OUTFILE = "reports_manifest.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# 拿到 r.text (response 的 text 形式 )
# note: 目前 None 可能用不上因为一旦有问题， 直接返回400等code 
def get_html_text(session: requests.Session, url: str) -> str:
    """
    Fetch HTML text from a page.
    Keep this function simple: success returns str; failure raises.
    """
    r = session.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    # print("status:", r.status_code)
    return r.text



def main():
    manifest_data = []
    # ✅ 关键优化：Session 复用连接（更快、更稳）什么意思？？？ 
    with requests.Session() as session:
        with open (INDEX_CSV, newline="", encoding="utf-8") as f: 
            reader = csv.DictReader(f)

            
            for row in reader:
                page_url = row.get("url")
                report_month = row.get("report_month")


                # 先放默认值：保证失败也能写入一条记录（status/notes 会说明原因）***** 
                title = None
                pdf_url = None
                status = "fail"
                notes = ""
                
                # fetch url中的html 信息 
                try: 
                    if not page_url:
                        raise ValueError("Missing page_url (row['url'] is empty)")
                    
                    # fetch url & parse html 
                    html = get_html_text(session, page_url)
                    soup = BeautifulSoup(html, "html.parser")

                    # ✅ title：h2.singleTitle（最稳定）
                    title_dom = soup.select_one("h2.singleTitle")
                    if not title_dom:
                        # 不一定要直接失败：你可以选择允许 title 缺失
                        raise ValueError("Title not found: h2.singleTitle")
                    
                    title = title_dom.get_text(strip=True)

                    # 稳定寻找：找 .pdf 结尾（如果页面将来多一个按钮，也更可控） 【未来如果有多个pdf文件怎么识别？？ - 报错再说吧】
                    pdf_url_dom = soup.select_one('div.post-textPad a[href$=".pdf"]')
                    if not pdf_url_dom: 
                        status = "fail"
                        notes = "PDF link not found in div.post-textPad (no a[href$='.pdf'])"
                    else:
                        pdf_url = pdf_url_dom.get("href")
                        if not pdf_url:
                            status = "fail"
                            notes = "PDF <a> found but href is empty"
                        else: 
                            status = "success"
                            notes = ""
                except requests.exceptions.RequestException as e:
                    # ✅ 网络层错误：超时、DNS、403/404/500 等
                    status = "fail"
                    notes = f"HTTP error: {type(e).__name__}: {e}"

                
                except Exception as e:
                    # ✅ 解析/逻辑错误：title缺失、结构变化等
                    status = "fail"
                    notes = f"Parse/logic error: {type(e).__name__}: {e}"


                # ✅ 永远 append：这样你能得到完整 manifest（含失败原因）
                # ⚠️ 注意 f-string 引号：外层用双引号，row 的 key 用单引号
                pdf_filename = None
                if report_month:
                    pdf_filename = f"nc_housing_{report_month}.pdf"
                    

                manifest_data.append({
                    "title": title,
                    "report_month": report_month,
                    "page_url": page_url,
                    "pdf_url": pdf_url,
                    "pdf_filename": pdf_filename,
                    "fetched_at": get_fetched_at(),
                    "status": status,
                    "notes": notes,
                })
            
    # 打印出来信息 - 3个row的案例
    # print(f"Total rows processed: {len(manifest_data)}")
    # print("Sample (first 3):")
    # for item in manifest_data[:3]:
    #     print(item)

    # write csv
    # filenames：表头
    fieldnames = ["title", "report_month", "page_url", 
                 "pdf_url", "pdf_filename", "fetched_at", "status", "notes"]
    # with 自动关闭文件
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_data)

    print(f"Saved {len(manifest_data)} rows to {OUTFILE}. ")


if __name__ == "__main__":
    main()
