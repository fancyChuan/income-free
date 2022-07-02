# 导入函数库
from jqdata import *

# 初始化函数，设定基准等等。
def initialize(context):
    # 设定沪深300作为基准 todo:在默认情况下，选定了沪深300指数的每日价格作为判断股票量化交易策略好坏和一系列风险值计算的基准
    # todo：例如，设定50ETF基金指数（510050）为基准，代码为： set_benchmark('510050.XSHG')
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # TODO 设置成交量比例函数:根据实际行情限制每个订单的成交量
    # TODO 对于每一笔订单，如果是市价单，成交量不超过：每日成交量×value；如果是限价单，限价单撮合时设定分价表中每一个价格的成交量的比例
    set_option('order_volume_radio', 0.25)
    # TODO 设置是否开启盘口撮合模式函数，只对模拟盘生效
    set_option('match_with_order_book', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    # todo: 问题，佣金和印花税应该是固定的吧，不能自定义？
    """
        type：指股票（stock）、基金（fund）、金融期货（index_futures）、期货（futures）、债券基金（bond_fund）、
        股票基金（stock_fund）、QDII基金（QDII_fund）、货币基金（money_market_fund）、混合基金（mixture_fund）
    """
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
      # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG')
      # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
      # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')

## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：'+str(context.current_dt.time()))

    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    # send_message('美好的一天~')

    # 要操作的股票：平安银行（g.为全局变量）
    g.security = '000001.XSHE'

## 开盘时运行函数
def market_open(context):
    log.info('函数运行时间(market_open):'+str(context.current_dt.time()))
    security = g.security
    # 获取股票的收盘价
    close_data = get_bars(security, count=5, unit='1d', fields=['close'])
    # 取得过去五天的平均价格
    MA5 = close_data['close'].mean()
    # 取得上一时间点价格
    current_price = close_data['close'][-1]
    # 取得当前的现金
    cash = context.portfolio.available_cash

    # 如果上一时间点价格高出五天平均价1%, 则全仓买入
    if (current_price > 1.01*MA5) and (cash > 0):
        # 记录这次买入
        log.info("价格高于均价 1%%, 买入 %s" % (security))
        # 用所有 cash 买入股票 TODO：order_value是买入函数
        order_value(security, cash)
    # 如果上一时间点价格低于五天平均价, 则空仓卖出
    elif current_price < MA5 and context.portfolio.positions[security].closeable_amount > 0:
        # 记录这次卖出
        log.info("价格低于均价, 卖出 %s" % (security))
        # 卖出所有股票,使这只股票的最终持有量为0
        order_target(security, 0)

## 收盘后运行函数
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):'+str(context.current_dt.time())))
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：'+str(_trade))
    log.info('一天结束')
    log.info('##############################################################')
