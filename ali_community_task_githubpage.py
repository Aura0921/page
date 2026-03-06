# -*- coding: utf-8 -*-
import requests
import json
import datetime
import os
from urllib.parse import urlparse

# ==================== 配置区域 ====================
# 请将以下域名替换为你的 GitHub Pages 实际域名（例如：yourname.github.io）
SITE_DOMAIN = "pages.auralife.top"  # <-- 务必修改！
# =================================================

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


# 解析URL，提取任务类别
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
    today_date = datetime.date.today()
    marked_today_data = []
    for activity in today_data:
        activity_start_date = datetime.datetime.strptime(activity['gmtStart'], "%Y-%m-%d %H:%M:%S").date()
        is_new = '是' if activity_start_date == today_date else '否'

        current_time = datetime.datetime.now()
        gmt_end = datetime.datetime.strptime(activity['gmtEnd'], "%Y-%m-%d %H:%M:%S")
        is_valid = '有效' if gmt_end > current_time else '失效'

        task_category = parse_task_category(activity.get('url', ''))

        activity['is_new'] = is_new
        activity['status'] = is_valid
        activity['task_category'] = task_category

        marked_today_data.append(activity)

    return marked_today_data


# 生成HTML表格
def generate_html_table(data, title):
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
    marked_data = mark_new_and_invalid_activities(today_data) if today_data else []

    total_count = len(marked_data)
    valid_count = sum(1 for act in marked_data if act['status'] == '有效')
    new_count = sum(1 for act in marked_data if act['is_new'] == '是')

    today_html = generate_html_table(marked_data, f"今日活动 ({datetime.date.today()})") if marked_data else "<p class='no-data'>今日没有活动数据。</p>"

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

    # ========== 新版不蒜子统计代码（官方） ==========
    busuanzi_script = '<script src="//cdn.busuanzi.cc/busuanzi/3.6.9/busuanzi.min.js" defer></script>'

    # 计数器卡片网格（四个核心指标）
    busuanzi_cards = f'''
    <div class="bsz-grid">
        <div class="bsz-card">
            <div class="bsz-label"><i class="fas fa-calendar-day"></i> 今日访问</div>
            <div class="bsz-number"><span id="busuanzi_today_pv">加载中...</span> <small>次</small></div>
        </div>
        <div class="bsz-card">
            <div class="bsz-label"><i class="fas fa-user-clock"></i> 今日访客</div>
            <div class="bsz-number"><span id="busuanzi_today_uv">加载中...</span> <small>人</small></div>
        </div>
        <div class="bsz-card">
            <div class="bsz-label"><i class="fas fa-chart-line"></i> 总访问量</div>
            <div class="bsz-number"><span id="busuanzi_site_pv">加载中...</span> <small>次</small></div>
        </div>
        <div class="bsz-card">
            <div class="bsz-label"><i class="fas fa-users"></i> 总访客数</div>
            <div class="bsz-number"><span id="busuanzi_site_uv">加载中...</span> <small>人</small></div>
        </div>
    </div>
    '''

    # 统计卡片（原有，显示今日活动数据）
    stats_card = f"""
    <div class="stats-card">
        <div class="stat-item">
            <div class="stat-icon"><i class="fas fa-tasks"></i></div>
            <div class="stat-info">
                <h3>今日活动总数</h3>
                <p>{total_count}</p>
            </div>
        </div>
        <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #34b1aa 0%, #1e847f 100%);"><i class="fas fa-check-circle"></i></div>
            <div class="stat-info">
                <h3>有效活动</h3>
                <p>{valid_count}</p>
            </div>
        </div>
        <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f6b83e 0%, #e68a2e 100%);"><i class="fas fa-star"></i></div>
            <div class="stat-info">
                <h3>新增活动</h3>
                <p>{new_count}</p>
            </div>
        </div>
    </div>
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
            background: linear-gradient(135deg, #f5f7fa 0%, #e9edf5 100%);
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

        /* ===== 不蒜子卡片网格 ===== */
        .bsz-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.2rem;
            margin-bottom: 2rem;
        }}
        .bsz-card {{
            background: white;
            border-radius: 20px;
            padding: 1.2rem 1rem;
            box-shadow: 0 10px 20px -5px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(5px);
            transition: transform 0.2s;
        }}
        .bsz-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 25px -8px rgba(102, 126, 234, 0.3);
        }}
        .bsz-label {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}
        .bsz-label i {{
            color: #667eea;
            font-size: 1rem;
        }}
        .bsz-number {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1.2;
        }}
        .bsz-number small {{
            font-size: 0.9rem;
            font-weight: 400;
            color: #64748b;
            margin-left: 0.2rem;
        }}
        /* 统计图标 */
        .bsz-icon {{
            display: inline-block;
            margin-bottom: 1rem;
            opacity: 0.8;
            transition: opacity 0.2s;
        }}
        .bsz-icon:hover {{
            opacity: 1;
        }}

        /* ===== 统计卡片（原有，微调） ===== */
        .stats-card {{
            background: white;
            border-radius: 24px;
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            display: flex;
            gap: 3rem;
            box-shadow: 0 15px 30px -12px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.5);
            backdrop-filter: blur(10px);
        }}
        .stat-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .stat-icon {{
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.8rem;
            box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.3);
        }}
        .stat-info h3 {{
            font-size: 0.9rem;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 0.2rem;
            letter-spacing: 0.5px;
        }}
        .stat-info p {{
            font-size: 2.2rem;
            font-weight: 700;
            color: #0f172a;
            line-height: 1;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .section-title:after {{
            content: '';
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, #cbd5e1, transparent);
        }}
        .table-container {{
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(10px);
            border-radius: 28px;
            padding: 1.5rem;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.7);
            overflow-x: auto;
        }}
        .activity-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            min-width: 1000px;
        }}
        .activity-table th {{
            background: #f1f4f9;
            color: #334155;
            font-weight: 600;
            padding: 1rem 0.75rem;
            text-align: left;
            border-bottom: 2px solid #d1d9e6;
            white-space: nowrap;
        }}
        .activity-table td {{
            padding: 1rem 0.75rem;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: middle;
            background: white;
        }}
        .activity-table tbody tr {{
            transition: all 0.2s ease;
        }}
        .activity-table tbody tr:hover {{
            background-color: #f8fafc;
            transform: scale(1.001);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }}
        .badge {{
            display: inline-block;
            padding: 0.35rem 0.9rem;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
            white-space: nowrap;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .badge-success {{
            background: #dcfce7;
            color: #166534;
            border-left: 3px solid #22c55e;
        }}
        .badge-danger {{
            background: #fee2e2;
            color: #991b1b;
            border-left: 3px solid #ef4444;
        }}
        .badge-secondary {{
            background: #f1f5f9;
            color: #334155;
            border-left: 3px solid #94a3b8;
        }}
        .badge-new {{
            background: #dbeafe;
            color: #1e40af;
            border-left: 3px solid #3b82f6;
        }}
        .badge-old {{
            background: #f1f5f9;
            color: #475569;
            border-left: 3px solid #94a3b8;
        }}
        .btn-link {{
            text-decoration: none;
            color: #2563eb;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            transition: all 0.2s;
            padding: 0.3rem 0.6rem;
            border-radius: 30px;
            background: #eff6ff;
        }}
        .btn-link:hover {{
            background: #2563eb;
            color: white;
            transform: translateX(3px);
        }}
        .no-data {{
            background: white;
            padding: 3rem;
            border-radius: 28px;
            text-align: center;
            color: #64748b;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            font-size: 1.1rem;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            padding: 1rem;
            background: rgba(255,255,255,0.5);
            border-radius: 50px;
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }}
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: white;
            width: 54px;
            height: 54px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            color: #667eea;
            font-size: 1.6rem;
            cursor: pointer;
            transition: all 0.3s;
            opacity: 0;
            visibility: hidden;
            border: none;
            z-index: 999;
        }}
        .back-to-top.show {{
            opacity: 1;
            visibility: visible;
        }}
        .back-to-top:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1><i class="fas fa-calendar-alt"></i> 每日活动报告</h1>

        <!-- 不蒜子统计区域（最上层） -->
        {busuanzi_cards}

        <!-- 原有活动统计卡片 -->
        {stats_card}

        <div class="subtitle">每小时更新一次 · 没更新则代表数据无变化</div>
        {today_html}

        <footer>
            <i class="far fa-clock"></i> 最后更新：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            <!-- 可在此处放置其他页脚信息 -->
        </footer>
    </div>

    <!-- 返回顶部按钮 -->
    <button class="back-to-top" id="backToTop" title="返回顶部"><i class="fas fa-arrow-up"></i></button>
    <script>
        // 返回顶部逻辑
        window.addEventListener('scroll', function() {{
            var btn = document.getElementById('backToTop');
            if (window.scrollY > 300) {{
                btn.classList.add('show');
            }} else {{
                btn.classList.remove('show');
            }}
        }});
        document.getElementById('backToTop').addEventListener('click', function() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    </script>

    <!-- 不蒜子脚本（defer 加载） -->
    {busuanzi_script}
</body>
</html>"""
    return full_html


if __name__ == "__main__":
    try:
        html_report = generate_html_report()
        with open("report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("报告生成成功：report.html")
        print("请检查 report.html 文件，并确保已将 SITE_DOMAIN 替换为你的真实域名。")
    except Exception as e:
        print(f"生成报告时发生错误: {e}")
