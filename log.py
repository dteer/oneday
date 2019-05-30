import logging
import os


class Logger():
    def __init__(self, namelog):
        self.namelog = namelog


        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s  - %(message)s')

        # 创建一个logger（dbug）
        self.logger_dbug = logging.getLogger('dbuglogger')
        self.logger_dbug.setLevel(logging.DEBUG)
        # 创建一个logger(err)
        self.logger_err = logging.getLogger('errlogger')
        self.logger_err.setLevel(logging.DEBUG)


        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        name_log = self.namelog + ".log"

        #判断是否存在文件夹log
        base_path = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_path,'log')
        judge = os.path.exists(log_dir)
        if not judge:
            os.mkdir(log_dir)
        log_path = os.path.join(log_dir,name_log)
        self.fh = logging.FileHandler(log_path)
        self.fh.setLevel(logging.DEBUG)



        ##设置输出格式
        ch.setFormatter(formatter)
        self.fh.setFormatter(formatter)


        # 给logger添加handler
        self.logger_dbug.addHandler(ch)
        self.logger_err.addHandler(self.fh)

    def dbuglog(self, manage):
        # 记录一条日志
        self.logger_dbug.info(manage)


    def errlog(self, manage):
        # 记录一条日志
        self.logger_err.error(manage)
        # 关闭打开的文件
        self.fh.close()

    def skiplog(self,manage):
        # 记录一条日志
        self.logger_err.info(manage)
        # 关闭打开的文件
        self.fh.close()


if __name__ == '__main__':

    log = Logger('log')

    i = 0
    log.dbuglog(i)
    j = 1
    try:
        o = j / i
    except Exception as e:
        log.errlog(e)
