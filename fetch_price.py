#!/usr/bin/env python3
"""
抓取优先级：1.鼎顺寄售  2.永盛珠宝  3.融通金
逐级降级抓取，全部失败空值返回，前端显示--
"""

import json
import re
import requests
from datetime import datetime
from typing import Dict, Any
import os

# ==================== 固定回收差价&系数 请勿修改 ====================
DIFF_GOLD      = 20
DIFF_PLATINUM  = 60
DIFF_PALLADIUM = 80
DIFF_SILVER    = 4

K22_RATIO      = 0.900
K18_RATIO      = 0.740
# =====================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 第一优先级：鼎顺寄售
def get_dingshun():
    try:
        url = "https://vip.zdxerp.cn/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        html = res.text

        gold_match   = re.search(r"黄金\s*[:：]\s*(\d+\.?\d*)", html)
        silver_match = re.search(r"白银\s*[:：]\s*(\d+\.?\d*)", html)
        pt_match     = re.search(r"铂金\s*[:：]\s*(\d+\.?\d*)", html)
        pd_match     = re.search(r"钯金\s*[:：]\s*(\d+\.?\d*)", html)

        return {
            "gold": float(gold_match.group(1)) if gold_match else None,
            "silver": float(silver_match.group(1)) if silver_match else None,
            "pt": float(pt_match.group(1)) if pt_match else None,
            "pd": float(pd_match.group(1)) if pd_match else None
        }
    except:
        return None

# 第二优先级：永盛珠宝
def get_yszb():
    try:
        url = "https://www.yszb9999.com/"
        res = requests.get(url, headers=HEADERS, timeout=8)
        html = res.text

        gold_match   = re.search(r"黄金\s*[:：]\s*(\d+\.?\d*)", html)
        silver_match = re.search(r"白银\s*[:：]\s*(\d+\.?\d*)", html)
        pt_match     = re.search(r"铂金\s*[:：]\s*(\d+\.?\d*)", html)
        pd_match     = re.search(r"钯金\s*[:：]\s*(\d+\.?\d*)", html)

        return {
            "gold": float(gold_match.group(1)) if gold_match else None,
            "silver": float(silver_match.group(1)) if silver_match else None,
            "pt": float(pt_match.group(1)) if pt_match else None,
            "pd": float(pd_match.group(1)) if pd_match else None
        }
    except:
        return None

# 第三优先级：融通金
def get_rtj():
    try:
        url = "https://www.rtj999.com/"
        res = requests.get(url, headers=HEADERS, timeout=6)
        html = res.text

        gold_match   = re.search(r"黄金\s*[:：]\s*(\d+\.?\d*)", html)
        silver_match = re.search(r"白银\s*[:：]\s*(\d+\.?\d*)", html)
        pt_match     = re.search(r"铂金\s*[:：]\s*(\d+\.?\d*)", html)
        pd_match     = re.search(r"钯金\s*[:：]\s*(\d+\.?\d*)", html)

        return {
            "gold": float(gold_match.group(1)) if gold_match else None,
            "silver": float(silver_match.group(1)) if silver_match else None,
            "pt": float(pt_match.group(1)) if pt_match else None,
            "pd": float(pd_match.group(1)) if pd_match else None
        }
    except:
        return None

# 备用预留位：后续可添加金十、天眼、上金所多源平均
def get_backup_avg():
    return {"gold":None,"silver":None,"pt":None,"pd":None}

def fetch_jintou() -> Dict[str, Any]:
    try:
        # 逐级降级抓取
        price = get_dingshun()
        if not price or not price["gold"]:
            price = get_yszb()
            if not price or not price["gold"]:
                price = get_rtj()
                if not price or not price["gold"]:
                    price = get_backup_avg()

        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "updateTime": now_time,
            "gold999": "",
            "k22": "",
            "k18": "",
            "pt999": "",
            "pd990": "",
            "silver999": ""
        }

        # 按固定公式计算回收价
        if price["gold"]:
            data["gold999"] = str(round(price["gold"] - DIFF_GOLD, 1))
            data["k22"]     = str(round((price["gold"] - DIFF_GOLD) * K22_RATIO, 1))
            data["k18"]     = str(round((price["gold"] - DIFF_GOLD) * K18_RATIO, 1))

        if price["pt"]:
            data["pt999"] = str(round(price["pt"] - DIFF_PLATINUM, 1))

        if price["pd"]:
            data["pd990"] = str(round(price["pd"] - DIFF_PALLADIUM, 1))

        if price["silver"]:
            data["silver999"] = str(round(price["silver"] - DIFF_SILVER, 1))

        return data

    except Exception as e:
        print("抓取异常：", e)
        now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "updateTime": now_time,
            "gold999": "",
            "k22": "",
            "k18": "",
            "pt999": "",
            "pd990": "",
            "silver999": ""
        }

def save_to_json(data: Dict[str, Any], filename: str = "price.json"):
    """保存数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    """主函数"""
    print("开始抓取黄金价格...")
    price_data = fetch_jintou()
    save_to_json(price_data, "price.json")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_to_json(price_data, os.path.join(script_dir, "..", "price.json"))
    print("抓取完成！")

if __name__ == "__main__":
    main()