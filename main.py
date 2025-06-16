from Spider import XyfwApi;from Analysis import PowerData, PowerPlot;
# from Notify import Bark
import config;import pandas as pd ;import Notify

if __name__ == "__main__":
    try:
        Api = XyfwApi()
        if Api.SessionManager.Expired():
            print("会话丢失或不存在，正在使你重新登录")
            if not Api.Login(config.username, config.password):
                print("Login failed.")
            else:
                print("登录成功")
        else:
            print("使用保存的会话")
            Api.SessionManager.Load()
        getData=Api.FetchElecData()
        if getData is not None:
            print("数据抓取成功")
            df = pd.read_csv('ElecData.csv', parse_dates=['日期'])
            analyzer = PowerData(df)
            analyzer.Calc7DayAvg();analyzer.FindAnomaly();analyzer.CalcDayDiff();
            analyzer.SaveToCSV()
            plotter = PowerPlot(analyzer.DataFrame)
            plotter.PlotUsageTrend()
            plotter.PlotWeekDayPie(analyzer.AvgByWeekDay())
            plotter.PlotMonthSum(analyzer.MonthTotal())
            plotter.PlotDayDiff()
            next_pay = None
            if '缴费余额（元）' in df.columns:
                balanceDf = df[['日期', '缴费余额（元）']].dropna()
                payDates, next_pay = analyzer.PredictPayDate(balanceDf)
                plotter.PlotPayPrediction(payDates, next_pay)
            yesday_row = analyzer.DataFrame.iloc[-1]
            yestoday_date = yesday_row['日期'].strftime('%m%d')
            yestoday_usage = yesday_row['用量（度/吨）']

            title = "📊电量提醒"
            message = f"{getData}\n昨日用电：{yestoday_date} {yestoday_usage:.2f}度\n"
            # message=message
            if next_pay:
                message += f"预计缴费：{next_pay}\n"
            Notify.Bark(title, message, config.bark_url)
            Notify.SelfWCPush(title, message, config.openid)
        else:
            print("抓取失败")
    except Exception as e:
        print("程序丢出异常:", e)
