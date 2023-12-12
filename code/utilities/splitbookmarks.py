import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDFをインポート
import os
import re

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def get_bookmarks(doc):
    bookmarks = []
    outline = doc.get_toc(simple=False)
    for item in outline:
        title, page_num, _ = item[1], item[2], item[0]
        if page_num >= 0:  # Ensure the page number is valid
            # タイトル、最初のページ番号をdict型で追加
            bookmarks.append({
                "title": title,
                "start_page": page_num - 1
            })

    return bookmarks

def split_and_save_pdf(doc, bookmark, folder):
    # start_page = bookmark[1]
    start_page = bookmark['start_page']
    end_page = bookmark['end_page']
    # print("----------------------------- スタートページ -----------------------------")
    # print(start_page)

    # ファイル名に無効な文字を置き換える
    valid_filename = re.sub(r'[\\/*?:"<>|]', '', bookmark["title"])
    output_filename = os.path.join(folder, f"{valid_filename}.pdf")

    # 保存先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    new_doc = fitz.open()  # 新しいPDFドキュメントを作成
    # start_pageとend_pageが同じ場合は、1ページのみのPDFを作成
    if start_page == end_page:
        page = doc.load_page(start_page)
        rect = page.rect
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.show_pdf_page(rect, doc, start_page)
    # start_pageとend_pageが異なる場合は、複数ページのPDFを作成
    else:
        for start_page in range(start_page, end_page):
            page = doc.load_page(start_page)  # 元のドキュメントからページを読み込む
            # print(" ----------------------------- page numger ----------------------------- ")
            # print(start_page)
            # print(" ----------------------------- page text ----------------------------- ")
            # print(page)
            rect = page.rect  # ページサイズを取得
            new_page = new_doc.new_page(width=rect.width, height=rect.height)  # 同じサイズの新しいページを作成
            new_page.show_pdf_page(rect, doc, start_page)  # 新しいページに元のページの内容を表示
    
    print(type(new_doc))

    if new_doc.page_count > 0:
        new_doc.save(output_filename)  # ページがある場合のみ保存
        new_doc.close()


def split_pdf_by_bookmarks(pdf_url):
    if not pdf_url:
        return

    # doc = fitz.open(pdf_path)  # ドキュメントを開く
    # blob storageからpdfを開く
    doc = fitz.open(pdf_url)
    bookmarks = get_bookmarks(doc)
    print("ブックマーク一覧")
    print(bookmarks)

    base_folder, original_filename = os.path.split("C:/Users/ryuseioya/Downloads/jpn-jpn-StyleGuide.pdf")
    new_folder = os.path.join(base_folder, f"分割PDF_{original_filename[:-4]}")
    os.makedirs(new_folder, exist_ok=True)

    for i, bookmark in enumerate(bookmarks):
        # このセクションの終了ページを定義
        end_page = bookmarks[i + 1]['start_page'] if i + 1 < len(bookmarks) else len(doc)
        bookmark['end_page'] = end_page
        split_and_save_pdf(doc, bookmark, new_folder)

    doc.close()
    return bookmarks

# if __name__ == "__main__":
#     pdf_file = select_pdf_file()
#     split_pdf_by_bookmarks(pdf_file)
