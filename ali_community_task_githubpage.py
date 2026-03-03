# -*- coding: utf-8 -*-

import requests
import json
import datetime
import os
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
    # 生成状态徽章的样式
    def status_badge(status):
        if status == '有效':
            return '<span class="badge badge-success">有效</span>'
        elif status == '失效':
            return '<span class="badge badge-danger">失效</span>'
        else:
            return f'<span class="badge badge-secondary">{status}</span>'

    def new_badge(is_new):
        if is_new == '是':
            return '<span class="badge badge-new">新增</span>'
        else:
            return '<span class="badge badge-old">已有</span>'

    rows = ''
    for activity in data:
        gifts = ", ".join(activity.get('giftList', {}).get('awardList', []))
        rows += f"""
        <tr>
            <td>{activity['title']}</td>
            <td>{activity['description']}</td>
            <td>{gifts}</td>
            <td>{activity['gmtStart']}</td>
            <td>{activity['gmtEnd']}</td>
            <td>{new_badge(activity['is_new'])}</td>
            <td>{status_badge(activity['status'])}</td>
            <td>{activity['task_category']}</td>
            <td><a href="{activity['url']}" target="_blank" class="btn-link">查看详情 →</a></td>
        </tr>
        """

    html = f"""
    <div class="table-container">
        <h2 class="section-title">{title}</h2>
        <table class="activity-table">
            <thead>
                <tr>
                    <th>活动标题</th>
                    <th>描述</th>
                    <th>奖品</th>
                    <th>开始时间</th>
                    <th>结束时间</th>
                    <th>是否新增</th>
                    <th>活动状态</th>
                    <th>任务类别</th>
                    <th>活动链接</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """
    return html


def generate_html_report():
    today_data = fetch_data()
    today_html = generate_html_table(
        mark_new_and_invalid_activities(today_data),
        f"今日活动 ({datetime.date.today()})"
    ) if today_data else "<p class='no-data'>今日没有活动数据。</p>"

    google_analytics = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-VCQTMFWDT9"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-VCQTMFWDT9');
    </script>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日活动报告</title>
    {google_analytics}
    <!-- Google Fonts & Font Awesome -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f7fb;
            color: #1e293b;
            line-height: 1.5;
            padding: 2rem 1rem;
        }}
        .report-container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        h1 i {{
            color: #3b82f6;
        }}
        .subtitle {{
            color: #64748b;
            margin-bottom: 2rem;
            font-size: 1rem;
            border-left: 4px solid #3b82f6;
            padding-left: 1rem;
        }}
        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            color: #1e293b;
        }}
        .table-container {{
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.02);
            overflow-x: auto;
        }}
        .activity-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            min-width: 1000px; /* 保证表格在宽屏上完整显示，小屏滚动 */
        }}
        .activity-table th {{
            background: #f8fafc;
            color: #334155;
            font-weight: 600;
            padding: 1rem 0.75rem;
            text-align: left;
            border-bottom: 2px solid #e2e8f0;
            white-space: nowrap;
        }}
        .activity-table td {{
            padding: 1rem 0.75rem;
            border-bottom: 1px solid #e9edf2;
            vertical-align: middle;
        }}
        .activity-table tbody tr:hover {{
            background-color: #f8fafc;
            transition: background 0.2s;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: 500;
            text-align: center;
            white-space: nowrap;
        }}
        .badge-success {{
            background: #dff9e6;
            color: #0b5e42;
        }}
        .badge-danger {{
            background: #fee9e7;
            color: #b91c1c;
        }}
        .badge-secondary {{
            background: #e9eef4;
            color: #4b5565;
        }}
        .badge-new {{
            background: #dbeafe;
            color: #1e40af;
        }}
        .badge-old {{
            background: #f1f5f9;
            color: #475569;
        }}
        .btn-link {{
            text-decoration: none;
            color: #2563eb;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: color 0.2s;
        }}
        .btn-link:hover {{
            color: #1e40af;
            text-decoration: underline;
        }}
        .no-data {{
            background: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            color: #64748b;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            color: #94a3b8;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1><i class="fas fa-calendar-alt"></i> 每日活动报告</h1>
        <div class="subtitle">每小时更新一次 · 没更新则代表数据无变化</div>
        {today_html}
        <footer>
            <i class="far fa-clock"></i> 最后更新：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </footer>
    </div>
</body>
</html>"""
    return full_html

if __name__ == "__main__":
    try:
        html_report = generate_html_report()
        open("report.html", "w", encoding="utf-8").write(html_report)
    except Exception as e:
        print(f"生成报告时发生错误: {e}")
