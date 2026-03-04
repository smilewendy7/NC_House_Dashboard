import csv 
import requests
from utils import get_fetched_at
from pathlib import Path


"""
stage: 3 

创建reports_downloads.csv 

从 manifest.csv 里取出 pdf_url + pdf_filename 

下载

记录下载结果： 如果下载成功download_status success, 如果失败 download_status fail

""" 

MANIFEST_CSV = "reports_manifest.csv"
OUTFILE = "reports_downloads.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

def fetch_response(
    session: requests.Session, 
    url: str, 
    *,
    req_headers: dict,
    timeout: int = 30, 
    stream: bool = False, 
) -> requests.Response: 
    """
    Fetch URL and return Response (caller decides how to read).
    - raises on non-2xx
    """
    r = session.get(
        url, 
        headers=req_headers,
        timeout=timeout,
        allow_redirects=True,
        stream=stream,
    )
    r.raise_for_status()
    return r


# 得到本地pdf 文件地址
def get_local_pdf_path(file_name: str) -> Path:
    local_pdfs_path = Path("data") / "pdfs"
    local_pdfs_path.mkdir(parents=True, exist_ok=True)
    return local_pdfs_path / file_name

# 判断是不是pdf文件
def is_local_pdf(path: Path) -> bool:
    """
    Validate local file is a real PDF by checking header bytes.

    """
    try:
        # 判断是不是真的pdf文件
        if not path.exists() or path.stat().st_size < 5:
            return False
        with open(path, "rb") as f:
            #PDF 文件的开头有一个固定标记（signature）b- bytes
            head = f.read(5)
        return head == b"%PDF-"
    except OSError:
        # 系统层面的读写错误/ 比如有没权限读取； 文件正被别的程序占用... (读写冲突)
        return False



# 下载PDF文件
def download_pdf(
    session: requests.Session,
    pdf_url: str, 
    file_name: str,
    *, 
    req_headers: dict,
    timeout: int = 60
) -> tuple[str, str, str]: 
    """
    Ensure local PDF exists and is valid.
    Returns (download_status, download_notes, local_pdf_path)

    download_status: "success" | "fail"

    """

    out_path = get_local_pdf_path(file_name)
    local_path_str = str(out_path)

    # 1) 如果本地path打开已有且确实是 PDF：直接 success（不下载）
    if is_local_pdf(out_path):
        return "success", "already_valid_pdf", local_path_str

    # 2) 如果本地文件存在但不是 PDF：记录一下，准备重下（可选择先删） --- request地址重新写入
    existed_but_invalid = out_path.exists()
    
    # 把这个文件路径的“扩展名”换掉； 下载时先写到 .part （避免网络断了， 程序崩溃， 文件只写一半等）
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")

    try:
        r = fetch_response(
            session,
            pdf_url,
            req_headers=req_headers,
            timeout=timeout,
            stream=True,
        )

        content_type = (r.headers.get("Content-Type") or "").lower()

        # 先读第一块做判断（避免写入一堆 HTML）
        first_chunk = b""
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                first_chunk = chunk
                break

        looks_like_pdf = first_chunk.startswith(b"%PDF-")
        is_pdf_type = ("pdf" in content_type)

        # 重新写入如果不是pdf... 
        if not (looks_like_pdf or is_pdf_type):
            # !r 等价于 repr(x), 显示不可见字符
            note = f"not_pdf content_type={content_type or 'missing'} first_bytes={first_chunk[:20]!r}"
            if existed_but_invalid:
                note = "existing_file_not_pdf; " + note
            return "fail", note, ""

        # 写入临时文件，成功后再 replace，避免半截文件
        with open(tmp_path, "wb") as f:
            f.write(first_chunk)
            for chunk in r.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)

        # 写完再做本地验证（必须 %PDF-）
        if not is_local_pdf(tmp_path):
            # tmp 不是 pdf，删掉
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                # 清理失败了不值得让整个程序崩掉。
                pass
            note = "downloaded_but_local_not_pdf"
            if existed_but_invalid:
                note = "existing_file_not_pdf; " + note
            return "fail", note, ""

        # 当下载成功后，执行：xxx.pdf.part → 变成 → xxx.pdf
        tmp_path.replace(out_path)

        if existed_but_invalid:
            #✅下载成功
            #✅并且覆盖了原本那个“坏掉的旧文件”（invalid local file）
            return "success", "redownloaded_over_invalid_local_file", local_path_str
        return "success", "downloaded", local_path_str

    except requests.HTTPError as e:
        status_code = getattr(e.response, "status_code", None)
        note = f"http_error status_code={status_code} msg={str(e)}"
        if existed_but_invalid:
            note = "existing_file_not_pdf; " + note
        return "fail", note, ""

    except requests.Timeout:
        note = "timeout"
        if existed_but_invalid:
            note = "existing_file_not_pdf; " + note
        return "fail", note, ""

    except requests.RequestException as e:
        note = f"request_exception msg={str(e)}"
        if existed_but_invalid:
            note = "existing_file_not_pdf; " + note
        return "fail", note, ""

    except OSError as e:
        note = f"os_error msg={str(e)}"
        if existed_but_invalid:
            note = "existing_file_not_pdf; " + note
        return "fail", note, ""

    finally:
        # 清理残留 .part
        try:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass




def main():
    out_fields = [
        "fetched_at",
        "report_month",
        "page_url",
        "pdf_url",
        "pdf_filename",
        "local_pdf_path",
        "download_status",
        "download_notes",
    ]
    
    with requests.Session() as session:
        with open(OUTFILE, "w", newline="", encoding="utf-8") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=out_fields)
            writer.writeheader()

            with open(MANIFEST_CSV, newline="", encoding="utf-8") as in_f:
                reader = csv.DictReader(in_f)

                for row in reader:
                    fetched_at = get_fetched_at()
                    report_month = (row.get("report_month") or "").strip()
                    page_url = (row.get("page_url") or "").strip()
                    pdf_url = (row.get("pdf_url") or "").strip()
                    pdf_filename = (row.get("pdf_filename") or "").strip()

                    manifest_status = (row.get("status") or "").strip().lower()

                    # 1) manifest 层面失败：没有 pdf_url（或 status=fail）
                    if manifest_status != "success" or not pdf_url or not pdf_filename:
                        writer.writerow({
                            "fetched_at": fetched_at,
                            "report_month": report_month,
                            "page_url": page_url,
                            "pdf_url": pdf_url,
                            "pdf_filename": pdf_filename,
                            "local_pdf_path": "",
                            "download_status": "fail",
                            "download_notes": f"manifest_fail status={manifest_status or 'missing'}",
                        })
                        continue

                    # 2) manifest 成功：尝试保证本地有有效 pdf
                    d_status, d_notes, local_path = download_pdf(
                        session,
                        pdf_url,
                        pdf_filename,
                        req_headers=HEADERS,
                        timeout=60,
                    )

                    writer.writerow({
                        "fetched_at": fetched_at,
                        "report_month": report_month,
                        "page_url": page_url,
                        "pdf_url": pdf_url,
                        "pdf_filename": pdf_filename,
                        "local_pdf_path": local_path,
                        "download_status": d_status,
                        "download_notes": d_notes,
                    })




if __name__ == "__main__":
    main()

# 读取输入（manifest）
# 下一步：pdf 文件解析 