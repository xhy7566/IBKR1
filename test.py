import yfinance as yf
import pandas as pd

# 创建 TSLA 的 Ticker 对象
ticker = yf.Ticker('TSLA')

# 获取最近 7 天的1分钟间隔的历史数据（1分钟数据仅适用于最近7天）
real_time_data = ticker.history(period="7d", interval='1m')

# 将时间索引转换为美国东部时间
real_time_data.index = real_time_data.index.tz_convert('US/Eastern')

# 定义目标时间点（美国东部时间）
target_time = pd.Timestamp('2025-04-26 06:33:00', tz='US/Eastern')

# 筛选出目标日期的数据
target_date_data = real_time_data[real_time_data.index.date == target_time.date()]

# 如果目标日期内有数据，找到最接近目标时间点的数据
if not target_date_data.empty:
    closest_time = target_date_data.index.get_loc(target_time, method='nearest')
    closest_data = target_date_data.iloc[closest_time]
    print(f"最接近的时间点（美国东部时间）: {closest_data.name}")
    print(f"最接近时间点的收盘价: {closest_data['Close']}")
else:
    print(f"目标日期 {target_time.date()} 内没有数据。")