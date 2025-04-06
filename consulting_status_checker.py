from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 測試用假身份證
test_id = "A123456789"

def check_appointment_status():
    url = "https://techgroup.com.tw/ConsultingStatus/inquire"
    
    try:
        # 設定 Chrome 選項
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 無頭模式
        options.add_argument('--disable-gpu')
        
        # 初始化瀏覽器
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        
        # 等待頁面完全載入
        time.sleep(5)
        
        # 調試: 獲取頁面源代碼和元素狀態
        print("頁面標題:", driver.title)
        print("頁面URL:", driver.current_url)
        print("頁面HTML片段:", driver.page_source[:500])  # 輸出前500字符幫助診斷
        
        # 嘗試點擊可能的查詢按鈕來觸發表單顯示         
        try:
            query_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'查詢') or contains(text(),'Query')]"))
            )
            query_btn.click()
            time.sleep(3)  # 等待表單顯示
        except:
            print("警告: 找不到明確的查詢按鈕")
        
        # 嘗試找到輸入欄位 - 擴展搜索條件
        try:
            id_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, 
                    "//input[@type='text' and (contains(@placeholder,'身份證') or contains(@placeholder,'ID') or contains(@id,'id') or contains(@name,'id') or contains(@class,'id-input'))]"))
            )
            id_input.send_keys(test_id)
            print("成功輸入身份證號碼")
        except Exception as e:
            print("所有輸入元素:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, input in enumerate(inputs):
                print(f"{i+1}. Type: {input.get_attribute('type')}, Name: {input.get_attribute('name')}, "
                      f"ID: {input.get_attribute('id')}, Placeholder: {input.get_attribute('placeholder')}")
            return f"錯誤: 無法找到身份證輸入欄位 - {str(e)}"
            
        # 嘗試提交表單
        try:
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
        except:
            return "錯誤: 無法找到提交按鈕"
            
        # 等待結果載入
        time.sleep(3)
        
        # 嘗試獲取結果
        try:
            result = driver.find_element(By.CLASS_NAME, "result").text  # 假設結果在class="result"的元素中
            return result if result else "查詢完成，但結果為空"
        except:
            return "錯誤: 無法解析查詢結果"
            
    except Exception as e:
        return f"錯誤: {str(e)}"
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    result = check_appointment_status()
    print(result)
