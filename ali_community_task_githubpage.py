# -*- coding: utf-8 -*-
import requests
import json
import datetime
import os
from urllib.parse import urlparse

# ==================== 配置区域 ====================
SITE_DOMAIN = "pages.auralife.top"  # <-- 务必修改！
# =================================================

# 固定的礼品分类及对应的 itemId 列表（除1积分礼品和活动礼品外）
FIXED_GIFT_CATEGORIES = {
    "乘风者博主礼品": [
        748731893994, 748925463669, 748894219550
    ],
    "社区周边专区": [
        681579803637, 680959365681, 681580123137, 681580107350,
        681257098834, 681579523495, 684138568679, 705326882004
    ]
}


# ==================== 活动数据获取 ====================
def fetch_activity_data():
    """获取活动列表（原有功能）"""
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
        if data.get("success") and data.get("code") == "200":
            return data["data"]["list"]
        else:
            return []
    except Exception as e:
        print(f"获取活动数据错误: {e}")
        return []


# ==================== 1积分礼品ID获取 ====================
def fetch_one_point_product_ids():
    """从接口获取1积分礼品的itemId列表"""
    url = "https://developer.aliyun.com/developer/api/product/getOnePointProductShowIds"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://developer.aliyun.com/score"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("code") == "200":
            return data.get("data", [])
        else:
            print("获取1积分礼品ID失败，使用默认空列表")
            return []
    except Exception as e:
        print(f"获取1积分礼品ID错误: {e}")
        return []


# ==================== 活动礼品获取 ====================
def fetch_activity_gifts(page_size=100):
    """
    获取常规活动礼品（lm/getGroupItems 接口）
    默认请求100条，避免分页
    """
    url = f"https://developer.aliyun.com/developer/api/lm/getGroupItems?pageNum=1&pageSize={page_size}"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://developer.aliyun.com/score"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("code") == "200":
            return data.get("data", {}).get("list", [])
        else:
            print("获取活动礼品失败")
            return []
    except Exception as e:
        print(f"获取活动礼品错误: {e}")
        return []


# ==================== 礼品数据获取（统一接口，用于按ID查询）====================
def fetch_gift_data_by_ids(item_ids):
    """
    通过 getListByIds 接口获取礼品详情
    参数 item_ids: list of int
    返回: list of gift dict
    """
    if not item_ids:
        return []

    ids_str = ",".join(str(i) for i in item_ids)
    url = f"https://developer.aliyun.com/developer/api/product/getListByIds?itemIds={ids_str}&userPropertyOrder=true"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Google Chrome\";v=\"145\", \"Chromium\";v=\"145\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "Referer": "https://developer.aliyun.com/score"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("success") and data.get("code") == "200":
            return data.get("data", [])
        else:
            print(f"获取礼品详情失败: {data.get('message')}")
            return []
    except Exception as e:
        print(f"获取礼品数据错误: {e}")
        return []


# ==================== 获取所有分类的礼品数据 ====================
def fetch_all_gifts():
    """获取所有分类的礼品数据，返回字典 {分类名: [礼品列表]}"""
    all_gifts = {}

    # 1. 获取动态的1积分礼品
    one_point_ids = fetch_one_point_product_ids()
    if one_point_ids:
        one_point_gifts = fetch_gift_data_by_ids(one_point_ids)
        all_gifts["1积分礼品"] = one_point_gifts
    else:
        all_gifts["1积分礼品"] = []

    # 2. 获取固定分类的礼品
    for category_name, ids in FIXED_GIFT_CATEGORIES.items():
        gifts = fetch_gift_data_by_ids(ids)
        all_gifts[category_name] = gifts

    # 3. 获取活动礼品（直接使用lm接口返回的数据，无需再次查询）
    activity_gifts = fetch_activity_gifts()
    all_gifts["活动礼品"] = activity_gifts

    return all_gifts


# ==================== 原有活动数据处理函数 ====================
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


# ==================== HTML 生成函数 ====================
def generate_activity_table(data, title):
    """生成活动表格（用于活动标签页）"""

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
    <div class="table-container" id="activities">
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


def generate_gift_tabs(gifts_data):
    """生成礼品内部的分类标签页HTML，并加入礼品统计栏，图片支持点击放大"""
    # 计算统计信息
    total_gifts = 0
    category_counts = {}
    for cat, gifts in gifts_data.items():
        count = len(gifts)
        category_counts[cat] = count
        total_gifts += count

    # 生成统计卡片HTML
    stats_items = f"""
    <div class="stat-item">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"><i class="fas fa-gift"></i></div>
        <div class="stat-info">
            <h3>礼品总数</h3>
            <p>{total_gifts}</p>
        </div>
    </div>
    """
    for cat, count in category_counts.items():
        stats_items += f"""
        <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #34b1aa 0%, #1e847f 100%);"><i class="fas fa-tag"></i></div>
            <div class="stat-info">
                <h3>{cat}</h3>
                <p>{count}</p>
            </div>
        </div>
        """

    gift_stats_card = f"""
    <div class="stats-card gifts-stats">
        {stats_items}
    </div>
    """

    # 标签页导航
    tabs_nav = '<div class="tabs-nav gift-tabs">'
    tabs_content = '<div class="tabs-content">'

    for i, (category_name, gifts) in enumerate(gifts_data.items()):
        active_class = ' active' if i == 0 else ''
        tabs_nav += f'<button class="tab-btn{active_class}" data-tab="gift-tab-{i}">{category_name}</button>'

        # 生成该分类的礼品表格
        if gifts:
            rows = ''
            for gift in gifts:
                main_pic = gift.get('mainPicUrl', '')
                if main_pic and not main_pic.startswith('http'):
                    main_pic = 'https:' + main_pic

                points = gift.get('discountPoints') or gift.get('points', 0)
                redeem_count = gift.get('redeemCount', 0)

                # 图片单元格：添加 onclick 点击放大
                rows += f"""
                <tr>
                    <td><img src="{main_pic}" alt="{gift.get('itemTitle', '')}" class="gift-img" onclick="openModal(this.src)" onerror="this.style.display='none'"></td>
                    <td>{gift.get('itemTitle', '')}</td>
                    <td><span class="badge badge-points">{points}</span></td>
                    <td>{redeem_count}</td>
                    <td><a href="https://developer.aliyun.com/score" target="_blank" class="btn-link">去兑换 →</a></td>
                </tr>
                """

            table = f"""
            <table class="gift-table">
                <thead>
                    <tr>
                        <th>图片</th>
                        <th>礼品名称</th>
                        <th>所需积分</th>
                        <th>已兑换</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            """
        else:
            table = '<p class="no-data">暂无礼品数据</p>'

        tabs_content += f'<div class="tab-pane{active_class}" id="gift-tab-{i}">{table}</div>'

    tabs_nav += '</div>'
    tabs_content += '</div>'

    return f"""
    <div class="gifts-section" id="gifts">
        <h2 class="section-title">🎁 积分礼品兑换</h2>
        {gift_stats_card}
        {tabs_nav}
        {tabs_content}
    </div>
    """


def generate_html_report():
    # 获取活动数据
    today_data = fetch_activity_data()
    marked_data = mark_new_and_invalid_activities(today_data) if today_data else []

    # 获取礼品数据
    gifts_data = fetch_all_gifts()

    # 统计数据
    total_count = len(marked_data)
    valid_count = sum(1 for act in marked_data if act['status'] == '有效')
    new_count = sum(1 for act in marked_data if act['is_new'] == '是')

    # 生成各部分HTML
    activities_html = generate_activity_table(marked_data,
                                              f"今日活动 ({datetime.date.today()})") if marked_data else "<p class='no-data'>今日没有活动数据。</p>"
    gifts_html = generate_gift_tabs(gifts_data)

    # 活动统计卡片
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

    # 主标签页导航
    main_tabs_nav = """
    <div class="main-tabs">
        <button class="main-tab-btn active" data-main="activities-tab"><i class="fas fa-calendar-alt"></i> 今日活动</button>
        <button class="main-tab-btn" data-main="gifts-tab"><i class="fas fa-gift"></i> 积分礼品</button>
    </div>
    """

    main_tabs_content = f"""
    <div id="activities-tab" class="main-tab-pane active">
        {stats_card}
        <div class="subtitle">每小时更新一次 · 没更新则代表数据无变化</div>
        {activities_html}
    </div>
    <div id="gifts-tab" class="main-tab-pane">
        {gifts_html}
    </div>
    """

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

    busuanzi_script = '<script src="//cdn.busuanzi.cc/busuanzi/3.6.9/busuanzi.min.js" defer></script>'

    busuanzi_cards = '''
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

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日活动报告 · 积分礼品</title>
    {google_analytics}
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

        /* 主标签页样式 */
        .main-tabs {{
            display: flex;
            gap: 0.5rem;
            margin: 1.5rem 0 1rem;
            background: white;
            padding: 0.5rem;
            border-radius: 50px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            width: fit-content;
        }}
        .main-tab-btn {{
            padding: 0.8rem 2rem;
            border: none;
            background: none;
            font-size: 1.1rem;
            font-weight: 600;
            color: #64748b;
            cursor: pointer;
            border-radius: 40px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .main-tab-btn i {{
            font-size: 1.2rem;
        }}
        .main-tab-btn:hover {{
            background: #f1f5f9;
            color: #334155;
        }}
        .main-tab-btn.active {{
            background: #667eea;
            color: white;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        .main-tab-pane {{
            display: none;
        }}
        .main-tab-pane.active {{
            display: block;
        }}

        /* 不蒜子卡片 */
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

        /* 统计卡片（通用） */
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
        /* 礼品统计卡片专用样式（支持换行） */
        .stats-card.gifts-stats {{
            flex-wrap: wrap;
            gap: 1rem;
            padding: 1rem;
        }}
        .stats-card.gifts-stats .stat-item {{
            min-width: 150px;
            flex: 1 1 auto;
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

        /* 通用标题 */
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

        /* 表格容器 */
        .table-container {{
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(10px);
            border-radius: 28px;
            padding: 1.5rem;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.7);
            overflow-x: auto;
            margin-bottom: 2rem;
        }}

        /* 活动表格 */
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
        .activity-table tbody tr:hover {{
            background-color: #f8fafc;
            transform: scale(1.001);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }}

        /* 礼品区域 */
        .gifts-section {{
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(10px);
            border-radius: 28px;
            padding: 1.5rem;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.7);
            margin-bottom: 2rem;
        }}

        /* 礼品内部标签页导航 */
        .gift-tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }}
        .gift-tabs .tab-btn {{
            padding: 0.6rem 1.5rem;
            border: none;
            background: none;
            font-size: 1rem;
            font-weight: 500;
            color: #64748b;
            cursor: pointer;
            border-radius: 30px;
            transition: all 0.2s;
        }}
        .gift-tabs .tab-btn:hover {{
            background: #f1f5f9;
            color: #334155;
        }}
        .gift-tabs .tab-btn.active {{
            background: #667eea;
            color: white;
        }}
        .tab-pane {{
            display: none;
        }}
        .tab-pane.active {{
            display: block;
        }}

        /* 礼品表格 */
        .gift-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        .gift-table th {{
            background: #f1f4f9;
            color: #334155;
            font-weight: 600;
            padding: 1rem 0.75rem;
            text-align: left;
            border-bottom: 2px solid #d1d9e6;
        }}
        .gift-table td {{
            padding: 1rem 0.75rem;
            border-bottom: 1px solid #e2e8f0;
            vertical-align: middle;
            background: white;
        }}
        .gift-img {{
            width: 60px;
            height: 60px;
            object-fit: contain;
            border-radius: 8px;
            background: #f8fafc;
            padding: 4px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .gift-img:hover {{
            transform: scale(1.1);
        }}
        .badge-points {{
            background: #fef3c7;
            color: #92400e;
            padding: 0.35rem 0.9rem;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 600;
            border-left: 3px solid #f59e0b;
        }}

        /* 通用徽章 */
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
        .subtitle {{
            color: #64748b;
            margin-bottom: 1rem;
            font-size: 0.95rem;
            border-left: 4px solid #3b82f6;
            padding-left: 1rem;
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

        /* 图片放大模态框 */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
            overflow: auto;
            cursor: pointer;
        }}
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            object-fit: contain;
        }}
        .close {{
            position: absolute;
            top: 20px;
            right: 35px;
            color: #fff;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 1001;
        }}
        .close:hover,
        .close:focus {{
            color: #ccc;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1><i class="fas fa-calendar-alt"></i> 每日活动报告 · 积分礼品</h1>

        <!-- 不蒜子统计 -->
        {busuanzi_cards}

        <!-- 主标签页导航 -->
        {main_tabs_nav}

        <!-- 主标签页内容 -->
        {main_tabs_content}

        <footer>
            <i class="far fa-clock"></i> 最后更新：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </footer>
    </div>

    <!-- 图片放大模态框 -->
    <div id="imageModal" class="modal" onclick="this.style.display='none'">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <button class="back-to-top" id="backToTop" title="返回顶部"><i class="fas fa-arrow-up"></i></button>

    <script>
        // 返回顶部
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

        // 主标签页切换
        document.querySelectorAll('.main-tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                document.querySelectorAll('.main-tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.main-tab-pane').forEach(p => p.classList.remove('active'));
                this.classList.add('active');
                const tabId = this.getAttribute('data-main');
                document.getElementById(tabId).classList.add('active');
            }});
        }});

        // 礼品内部标签页切换
        document.querySelectorAll('.gift-tabs .tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const tabsContainer = this.closest('.gift-tabs');
                tabsContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                const panesContainer = tabsContainer.nextElementSibling;
                panesContainer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                this.classList.add('active');
                const tabId = this.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            }});
        }});

        // 图片放大功能
        function openModal(src) {{
            document.getElementById('modalImage').src = src;
            document.getElementById('imageModal').style.display = 'block';
        }}
        // 点击模态框背景关闭（已在div上设置onclick）
    </script>

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
