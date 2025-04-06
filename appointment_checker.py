import argparse
from playwright.sync_api import sync_playwright
import urllib.parse

def check_appointment_status(id_number, birthday):
    """查詢預約狀態
    
    Args:
        id_number (str): 身分證字號
        birthday (str): 生日格式為 YYYY-MM-DD (如 1970-01-01)
    """
    # 預約查詢 URL
    base_url = "https://techgroup.com.tw/ConsultingStatus/inquire"
    params = {
        'id': '3812040086',
        'name': urllib.parse.quote('李如英中醫診所')
    }
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"

    with sync_playwright() as p:
        # 啟動瀏覽器 (headless=False 可看到瀏覽器操作)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 訪問預約查詢頁面
            page.goto(url, timeout=10000)
            
            # 等待頁面加載完成
            page.wait_for_selector('body')
            page.wait_for_timeout(1000)  # 額外等待1秒確保完全加載
            
            try:
                # 填寫表單
                year, month, day = birthday.split('-')
                # 等待表單完全加載
                page.wait_for_timeout(3000)
                
                # 保存更多的調試信息
                with open('page_content.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                page.screenshot(path='full_page.png')
                print("已保存頁面HTML和截圖供調試")
                
                # 嘗試通過完整XPath定位
                page.fill('xpath=//div[@id="id_content"]//input[@type="text"]', id_number)
                print("通過完整XPath結構找到並填寫身分證輸入框")
                print(f"已輸入身分證末四碼: {id_number[-4:]}")
                
                page.wait_for_selector('select:nth-of-type(1)')
                page.select_option('select:nth-of-type(1)', value=year)
                
                page.wait_for_selector('select:nth-of-type(2)')
                page.select_option('select:nth-of-type(2)', value=month)
                
                page.wait_for_selector('select:nth-of-type(3)') 
                page.select_option('select:nth-of-type(3)', value=day)
            except Exception as e:
                print(f"表單填寫錯誤: {e}")
                raise
            
            # 點擊查詢按鈕
            page.click('button:has-text("確定查詢")')
            
            # 等待結果加載
            page.wait_for_timeout(2000)
            
            # 獲取頁面內容
            content = page.content()
            
            # 從頁面中提取特定資訊
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找通知訊息
            note_div = soup.find('div', class_='note')
            
            # 輸出格式化結果
            print("\n預約資訊:")
            if note_div:
                print(note_div.get_text(strip=True))
            else:
                print("未找到預約相關資訊")
            
            # 查找並輸出表單元素
            form_elements = soup.find_all(['input', 'select', 'button'])
            print("\n表單項目檢測到:")
            for element in form_elements:
                element_type = element.name
                element_text = element.get_text(strip=True)
                
                if element_type == 'input':
                    print(f"輸入框: placeholder='{element.get('placeholder', '')}' type='{element.get('type', 'text')}'")
                elif element_type == 'select':
                    print(f"下拉選單: {'必填' if element.get('required') else '選填'}")
                elif element_type == 'button':
                    print(f"按鈕: {element_text}")
            
        except Exception as e:
            print(f"查詢過程中發生錯誤: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    # 設定命令列參數解析
    parser = argparse.ArgumentParser(
        description='李如英中醫診所預約查詢工具',
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('--id', required=True, 
                       help='身分證字號 (必填)')
    parser.add_argument('--birthday', required=True,
                       help='生日 (格式: YYYY-MM-DD，如 1970-01-01)')

    args = parser.parse_args()
    
    print(f"\n開始查詢身分證末四碼: {args.id[-4:]}")
    print(f"生日: {args.birthday}\n")
    
    check_appointment_status(args.id, args.birthday)
    
    print("\n查詢完成")
