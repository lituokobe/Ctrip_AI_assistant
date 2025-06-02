import sys, os
from loguru import logger

# get the absolute path of current project
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir, "logs")  # the absolute path to store the project log

if not os.path.exists(log_dir):  # create one if the log directory doesn't exist
    os.mkdir(log_dir)



class MyLogger:
    def __init__(self):
        # log_file_path = os.path.join(log_dir, LOG_FILE)
        self.logger = logger  # object for log
        # clear all configuration
        self.logger.remove()
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout, level='DEBUG',
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  
                               "{process.name} | "  
                               "{thread.name} | "  
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>" 
                               ":<cyan>{line}</cyan> | " 
                               "<level>{level}</level>: "  
                               "<level>{message}</level>",
                        )

    def get_logger(self):
        return self.logger


log = MyLogger().get_logger()

if __name__ == '__main__':
    print('str.pdf'['str.pdf'.rindex('.'):])
    def test():
        try:
            print(3/0)
        except ZeroDivisionError as e:
            log.exception(e)  # 以后常用
    test()
