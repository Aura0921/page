---
aliases: 
tags: 
author: Aura Service
created: 2025-01-17T10:20:13
updated: 2025-02-15T10:34:16
---
**免责声明：** 本程序仅用于学习目的，严禁用于任何商业或非法用途。

**隐私保护提示：** 文章中已对敏感信息进行脱敏处理。如果您发现任何潜在的隐私泄露问题，请不吝告知，以便我及时进行修改或删除。感谢您的理解和支持！

--- 
阿里云经常有一些实物活动白嫖，但是不是每一个我都需要，故而整理了一个脚本，一眼可见我想要和不想要参加的活动。

（因为生成的页面没有做优化，故手机看会很别扭）

---

# 使用github page

## 1 效果展示
![](https://www.helloimg.com/i/2025/01/16/6788d9f8a42dc.png)
## 2 部署流程
### 2.1 将每日活动报告部署到 GitHub Pages

在本节中，我们将详细介绍如何将你的 Python 脚本生成的 HTML 活动报告部署到 GitHub Pages，以便通过浏览器在线访问报告。

#### 2.1.1 创建 GitHub 仓库

1. 登录你的 GitHub 账户。
2. 点击页面右上角的 **+** 按钮，然后选择 **New repository**。
3. 创建一个新的仓库，选择公开（Public），并为仓库命名（例如：`daily-activity-report`）。
4. 点击 **Create repository** 完成仓库创建。

#### 2.1.2 克隆仓库到本地

在你的本地计算机上，使用 Git 克隆刚创建的 GitHub 仓库。

```bash
git clone https://github.com/your-username/daily-activity-report.git
```

请确保将 `your-username` 替换为你的 GitHub 用户名，`daily-activity-report` 替换为你创建的仓库名称。

#### 2.1.3 将 python代码文件添加到仓库

1. 在你本地克隆的仓库目录中，把文件daily-activity-report.py放到这个目录，将代码贴入该文件。
    
2. 将 report.html 放入仓库中，并确保脚本的输出（即 `report.html` 文件）也保存在仓库目录内。
    

#### 2.1.4 配置 GitHub Pages

1. 在 GitHub 仓库页面，点击 **Settings** 标签。
    
2. 滚动到页面底部，找到 **GitHub Pages** 部分。
    
3. 在 **Source** 部分，选择 **main** 分支，选择根目录 **/** 目录。
    
    - **Source**: `main` 分支
    - **Folder**: `/` 目录
4. 保存设置后，GitHub 会为你的仓库创建一个 GitHub Pages 网站，通常会在以下地址显示：
    
    ```
    https://your-username.github.io/daily-activity-report/report.html
    ```
    
    请注意，你需要替换 `your-username` 为你的 GitHub 用户名，`daily-activity-report` 为你的仓库名。
    

#### 2.1.5 步骤 5: 提交并推送更改

1. 在仓库目录下，使用 Git 添加和提交更改：
    
    ```bash
    git add .
    git commit -m "Add daily activity report HTML"
    ```
    
2. 将更改推送到 GitHub 仓库：
    
    ```bash
    git push origin main
    ```
    

#### 2.1.6 步骤 6: 自动化生成和部署报告（可选）

为了实现自动化，可以使用 GitHub Actions 每天运行 Python 脚本并自动推送更新的 HTML 报告。以下是创建 GitHub Action 工作流的步骤：

1. 在你的 GitHub 仓库中，创建一个目录 `.github/workflows`。
2. 在该目录下创建一个新的工作流文件（例如：`deploy.yml`），并在文件中添加以下内容（参考）：

```yaml
name: Update GitHub Pages

# 触发条件：每天定时执行
on:
  schedule:
    - cron: '0 0,8,13,18 * * *'  # 每天 UTC 时间 00:00 执行，可以根据需要修改时间
  workflow_dispatch:
  
permissions:
  contents: write  

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'  # 安装 Python 3.x

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests  # 安装需要的 Python 包

    - name: Run script to generate HTML
      run: |
        python daily-activity-report.py  # 运行你的 Python 脚本来生成 report.html

    - name: Check if report.html is generated
      run: |
        if [ -f "./report.html" ]; then
          echo "报告文件已生成：report.html"
        else
          echo "报告文件未生成：report.html"
          exit 1  # 如果文件未生成，终止工作流
        fi

    - name: Commit and push the changes
      run: |
        git config --global user.name "github-actions"
        git config --global user.email "github-actions@github.com"
        git add report.html
        git commit -m "Update report.html with new activity data" || echo "No changes to commit"
        git push origin main
```

该工作流会在每天的零点自动运行 Python 脚本，并将生成的 `report.html` 文件推送到 GitHub Pages。

3. 提交并推送工作流配置：

```bash
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Action for daily report generation"
git push origin main
```

#### 2.1.7 步骤 7: 查看报告

完成上述步骤后，你的报告将通过 GitHub Pages 部署，并且你可以通过以下 URL 查看每日活动报告：

```
https://your-username.github.io/daily-activity-report/report.html
```

该 URL 将自动展示每天生成的 HTML 报告。

---

代码  daily-activity-report.py  :
```Python
# -*- coding: utf-8 -*-  
"""  
@File       : ali_task_page.py  
@Project    : pythonToolsProject  
@Author     : Aura Service  
@CreateTime : 2025/1/15 15:02  
@Description:  
解析阿里云社区为 表格形式html  标记有效、活动  
用于githubpage  
"""
  
import requests  
import datetime  
from urllib.parse import urlparse  
  
# 请求API并获取数据  
def fetch_data():  
    url = "https://developer.aliyun.com/developer/api/task/getMissionPage?taskLevel=-1&taskType=-1&giftType=all&pageNum=1&pageSize=50"  
    headers = {  
        "accept": "application/json, text/plain, */*",  
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",  
        "bx-v": "2.5.26",  
        "priority": "u=1, i",  
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",  
        "sec-ch-ua-mobile": "?0",  
        "sec-ch-ua-platform": "\"Windows\"",  
        "sec-fetch-dest": "empty",  
        "sec-fetch-mode": "cors",  
        "sec-fetch-site": "same-origin",  
        "Referrer-Policy": "no-referrer-when-downgrade"  
    }  
  
    try:  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  
        data = response.json()  
        if data["success"] and data["code"] == "200":  
            return data["data"]["list"]  
        else:  
            return []  
    except requests.exceptions.RequestException as e:  
        print(f"请求错误: {e}")  
        return []  
  
  
# 解析URL，提取任务类别（即域名后面的第一个值）  
def parse_task_category(url):  
    try:  
        parsed_url = urlparse(url)  
        path_segments = parsed_url.path.strip("/").split("/")  
        if path_segments:  
            return path_segments[0]  
        return ""  
    except Exception as e:  
        print(f"解析URL失败: {e}")  
        return ""  
  
  
# 标记新增和失效活动  
def mark_new_and_invalid_activities(today_data):  
    # 获取今天的日期  
    today_date = datetime.date.today()  
  
    marked_today_data = []  
    for activity in today_data:  
        # 标记是否新增  
        activity_start_date = datetime.datetime.strptime(activity['gmtStart'], "%Y-%m-%d %H:%M:%S").date()  
        is_new = '是' if activity_start_date == today_date else '否'  
  
        # 标记是否有效  
        current_time = datetime.datetime.now()  
        gmt_end = datetime.datetime.strptime(activity['gmtEnd'], "%Y-%m-%d %H:%M:%S")  
        is_valid = '有效' if gmt_end > current_time else '失效'  
  
        # 提取任务类别  
        task_category = parse_task_category(activity.get('url', ''))  
  
        # 添加标记  
        activity['is_new'] = is_new  
        activity['status'] = is_valid  
        activity['task_category'] = task_category  # 新增字段，展示任务类别  
  
        marked_today_data.append(activity)  
  
    return marked_today_data  
  
  
# 生成HTML表格  
def generate_html_table(data, title):  
    html = f"<h2>{title}</h2><style>.col-title{{width:200px;}}.col-description{{width:200px;}}.col-gift{{width:100px;}}.col-start{{width:150px;}}.col-end{{width:150px;}}.col-new{{width:100px;}}.col-status{{width:100px;}}.col-task{{width:100px;}}.col-url{{width:100px;}}table{{border-collapse:collapse;}}th,td{{border:1px solid black;padding:10px;}}</style><table><thead><tr><th class='col-title'>活动标题</th><th class='col-description'>描述</th><th class='col-gift'>奖品</th><th class='col-start'>开始时间</th><th class='col-end'>结束时间</th><th class='col-new'>是否新增</th><th class='col-status'>活动状态</th><th class='col-task'>任务类别</th><th class='col-url'>活动链接</th></tr></thead><tbody>"  
  
    for activity in data:  
        gifts = ", ".join(activity.get('giftList', {}).get('awardList', []))  
        html += f"<tr><td>{activity['title']}</td><td>{activity['description']}</td><td>{gifts}</td><td>{activity['gmtStart']}</td><td>{activity['gmtEnd']}</td><td>{activity['is_new']}</td><td>{activity['status']}</td><td>{activity['task_category']}</td><td><a href='{activity['url']}' target='_blank'>查看详情</a></td></tr>"  
  
    html += "</tbody></table>"  
    return html  
  
  
def generate_html_report():  
    today_data = fetch_data()  
  
    # 标记新增和失效活动  
    today_html = generate_html_table(mark_new_and_invalid_activities(today_data),  
                                     f"今日活动 ({datetime.date.today()})") if today_data else "<p>今日没有活动数据。</p>"  
  
    full_html = f"<html><head><title>活动报告</title></head><body><h1>每日活动报告</h1>{today_html}</body></html>"  
  
    return full_html  
  
  
if __name__ == "__main__":  
    try:  
        html_report = generate_html_report()  
        open("report.html", "w", encoding="utf-8").write(html_report)  
    except Exception as e:  
        print(f"生成报告时发生错误: {e}")
```


# 使用push_plus

## 1 效果展示（电脑端）

![](https://www.helloimg.com/i/2025/01/16/6788d8600211e.png)
## 2 部署说明

1. 修改 push_plus_token 
2. 定时执行即可


```Python
# -*- coding: utf-8 -*-  
"""  
@File       : ali_task_ql.py  
@Project    : pythonToolsProject  
@Author     : Aura Service  
@CreateTime : 2025/1/15 15:02  
@Description:  
解析阿里云社区为 表格形式html  标记有效、活动  
push_plus推送  
"""
  
import requests  
import datetime  
from urllib.parse import urlparse  
  
push_plus_token = 'push_plus_token'  
push_plus_topic = ''

# 请求API并获取数据  
def fetch_data():  
    url = "https://developer.aliyun.com/developer/api/task/getMissionPage?taskLevel=-1&taskType=-1&giftType=all&pageNum=1&pageSize=50"  
    headers = {  
        "accept": "application/json, text/plain, */*",  
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",  
        "bx-v": "2.5.26",  
        "priority": "u=1, i",  
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",  
        "sec-ch-ua-mobile": "?0",  
        "sec-ch-ua-platform": "\"Windows\"",  
        "sec-fetch-dest": "empty",  
        "sec-fetch-mode": "cors",  
        "sec-fetch-site": "same-origin",  
        "Referrer-Policy": "no-referrer-when-downgrade"  
    }  
  
    try:  
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  
        data = response.json()  
        if data["success"] and data["code"] == "200":  
            return data["data"]["list"]  
        else:  
            return []  
    except requests.exceptions.RequestException as e:  
        print(f"请求错误: {e}")  
        return []  
  
  
# 解析URL，提取任务类别（即域名后面的第一个值）  
def parse_task_category(url):  
    try:  
        parsed_url = urlparse(url)  
        path_segments = parsed_url.path.strip("/").split("/")  
        if path_segments:  
            return path_segments[0]  
        return ""  
    except Exception as e:  
        print(f"解析URL失败: {e}")  
        return ""  
  
  
# 标记新增和失效活动  
def mark_new_and_invalid_activities(today_data):  
    # 获取今天的日期  
    today_date = datetime.date.today()  
  
    marked_today_data = []  
    for activity in today_data:  
        # 标记是否新增  
        activity_start_date = datetime.datetime.strptime(activity['gmtStart'], "%Y-%m-%d %H:%M:%S").date()  
        is_new = '是' if activity_start_date == today_date else '否'  
  
        # 标记是否有效  
        current_time = datetime.datetime.now()  
        gmt_end = datetime.datetime.strptime(activity['gmtEnd'], "%Y-%m-%d %H:%M:%S")  
        is_valid = '有效' if gmt_end > current_time else '失效'  
  
        # 提取任务类别  
        task_category = parse_task_category(activity.get('url', ''))  
  
        # 添加标记  
        activity['is_new'] = is_new  
        activity['status'] = is_valid  
        activity['task_category'] = task_category  # 新增字段，展示任务类别  
  
        marked_today_data.append(activity)  
  
    return marked_today_data  
  
  
# 生成HTML表格  
def generate_html_table(data, title):  
    html = f"<h2>{title}</h2><style>.col-title{{width:200px;}}.col-description{{width:200px;}}.col-gift{{width:100px;}}.col-start{{width:150px;}}.col-end{{width:150px;}}.col-new{{width:100px;}}.col-status{{width:100px;}}.col-task{{width:100px;}}.col-url{{width:100px;}}table{{border-collapse:collapse;}}th,td{{border:1px solid black;padding:10px;}}</style><table><thead><tr><th class='col-title'>活动标题</th><th class='col-description'>描述</th><th class='col-gift'>奖品</th><th class='col-start'>开始时间</th><th class='col-end'>结束时间</th><th class='col-new'>是否新增</th><th class='col-status'>活动状态</th><th class='col-task'>任务类别</th><th class='col-url'>活动链接</th></tr></thead><tbody>"  
  
    for activity in data:  
        gifts = ", ".join(activity.get('giftList', {}).get('awardList', []))  
        html += f"<tr><td>{activity['title']}</td><td>{activity['description']}</td><td>{gifts}</td><td>{activity['gmtStart']}</td><td>{activity['gmtEnd']}</td><td>{activity['is_new']}</td><td>{activity['status']}</td><td>{activity['task_category']}</td><td><a href='{activity['url']}' target='_blank'>查看详情</a></td></tr>"  
  
    html += "</tbody></table>"  
    return html  
  
  
def generate_html_report():  
    today_data = fetch_data()  
  
    # 标记新增和失效活动  
    today_html = generate_html_table(mark_new_and_invalid_activities(today_data),  
                                     f"今日活动 ({datetime.date.today()})") if today_data else "<p>今日没有活动数据。</p>"  
  
    full_html = f"<html><head><title>活动报告</title></head><body><h1>每日活动报告</h1>{today_html}</body></html>"  
  
    return full_html  
  
  
# 发送到PushPlus或其他推送服务  
def send_to_pushplus(html_content):  
    topic = push_plus_topic  
    title = '阿里云社区活动报告'  
    token = push_plus_token  
    url = 'http://www.pushplus.plus/send'  
    if topic == '':  
        data = {  
            'token': token,  
            'title': title,  
            'content': html_content  
        }  
    else:  
        data = {  
            'token': token,  
            'title': title,  
            'content': html_content,  
            'topic': topic  
        }  
    response = requests.post(url, json=data)  
    print(response.text)  
  
  
if __name__ == "__main__":  
    try:  
        html_report = generate_html_report()  
        # open("report.html", "w", encoding="utf-8").write(html_report)  
        send_to_pushplus(html_report)  
    except Exception as e:  
        print(f"生成报告时发生错误: {e}")
```
