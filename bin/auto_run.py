#!/usr/bin/env python3
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from xuexitong_cli.agent_runner import XuexitongAutoPilot

if __name__ == "__main__":
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    autopilot = XuexitongAutoPilot(api_key=api_key)
    try:
        autopilot.run_all()
    except Exception as e:
        print(f"❌ 运行中断: {e}")
