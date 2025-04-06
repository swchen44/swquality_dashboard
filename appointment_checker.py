from playwright.sync_api import sync_playwright
import urllib.parse

def check_appointment_status():
    # 預約查詢 URL
    base_url = "https://techgroup.com.tw/ConsultingStatus/inquire"
    params = {
        'id': '3812040086',
        'name': urllib.parse.quote('李如英中醫診所'),
        'PID': '3B407B88-C904-4501-985F-E97770C51BE3'
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
    check_appointment_status()
