import hashlib
import time

def calculate_enc(clazz_id, jobid, object_id, playing_time, duration, clip_time="0"):
    """
    计算超星学习通视频心跳的关键 enc 签名。
    标准逆向算法规则：
    enc = md5("[clazzId][jobid][objectId][playingTime*1000][d_yHJ!#$][duration*1000][clipTime_duration]")
    其中部分参数以毫秒计，clipTime 格式通常为 0_{duration}
    """
    playing_time_ms = int(playing_time * 1000)
    duration_ms = int(duration * 1000)
    clip_str = f"0_{int(duration)}" if clip_time == "0" else str(clip_time)
    
    raw = f"[{clazz_id}][{jobid}][{object_id}][{playing_time_ms}][d_yHJ!#$][duration_ms][{clip_str}]"
    # 超星常规盐值模板替换
    raw_real = f"[{clazz_id}][{jobid}][{object_id}][{playing_time_ms}][d_yHJ!#$][{duration_ms}][{clip_str}]"
    return hashlib.md5(raw_real.encode('utf-8')).hexdigest()

def get_timestamp_ms():
    return int(time.time() * 1000)
