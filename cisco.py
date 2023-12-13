from connection import Net


class IOS_XE_17(Net):
    def __init__(self):
        super().__init__('cisco_ios', '192.168.1.100', 'ciscouser', 'cisco@123')

    # 获取配置
    ## 输出字符串形式的设备配置
    def get_config(self):
        cmd = 'show running-config'
        info = self.device.send_command(cmd)
        data_str = info.split('platform console serial\n!')[1]
        return data_str

    # 获取接口
    ## 输出列表形式的接口数据
    def get_interfaces(self):
        cmd = 'show ip interface brief'
        info = self.device.send_command(cmd)
        data_list = []
        for line in info.split('\n')[1:]:
            line_list = line.split()
            if_name = line_list[0]
            if_ip = line_list[1]
            status = line_list[-1]
            data_list.append({'name': if_name,
                              'ip': if_ip,
                              'status': status})
        return data_list

    # 接口恢复UP  
    def recover_interface(self, if_name):
        self.reconnect()
        cmd_list = [f'interface {if_name}', 'no shutdown']
        self.device.send_config_set(cmd_list)

    # 获取路由表
    ## 输出字符串形式的设备路由表信息
    def get_route(self):
        cmd = 'show ip route'
        info = self.device.send_command(cmd)
        data_str = '\n'.join([line for line in info.split('\n') if '/' in line])
        return data_str

    # 新增路由条目
    def post_route(self, dst_n, mask, next):
        self.reconnect()
        cmd_list = [f'ip route {dst_n} {mask} {next}']
        self.device.send_config_set(cmd_list)

    # 自动化巡检
    ## 输出字典形式的CPU使用率数据
    def monitor(self):
        cpu_cmd = 'show processes cpu'
        cpu_info = self.device.send_command(cpu_cmd)
        line = cpu_info.split('\n')[0].split('five seconds: ')[1]
        cpu_list = line.split('%')
        data_dict = {'cpu1_5s': cpu_list[0][-1:],
                     'cpu2_5s': cpu_list[1][-1:],
                     'cpu1_1m': cpu_list[2][-1:],
                     'cpu1_5m': cpu_list[3][-1:]}
        return data_dict