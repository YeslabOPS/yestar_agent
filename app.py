import datetime
from cisco import IOS_XE_17

# 使用设备名称、告警类型、告警描述四个字段得到一个HTML版本的邮件主体
def create_mail_body(device_name, alert_type, alert_description):
    now_time = str(datetime.datetime.now()).split('.')[0]
    with open('template/head.html', encoding='utf-8') as f:
        text_head = f.read()
    with open('template/body.html', encoding='utf-8') as f:
        text_body = f.read()
    body = text_head + "\n" + text_body.format(device_name, alert_type, alert_description, now_time)
    return body


def cisco_runner():
    device_name = 'CiscoIOSXE'
    ios_xe = IOS_XE_17()

    # Task1. 获取信息生成JSON数据
    cisco_data = {}
    cisco_data['config'] = ios_xe.get_config()
    cisco_data['interfaces'] = ios_xe.get_interfaces()
    cisco_data['routeTable'] = ios_xe.get_route()
    cisco_data['monitor'] = {'cpu': ios_xe.monitor()}

    # Task2. 接口恢复与检查
    for interface in cisco_data['interfaces']:
        if interface['status'] != 'up':
            # 制作邮件主体并发送告警
            alert_des = f'{device_name} 的接口 {interface['name']} 被关闭了'
            body = create_mail_body(device_name, 'Error', alert_des)
            ios_xe.send_mail(subject='设备接口故障', body=body)

            # 开始接口恢复
            ios_xe.recover_interface(interface['name'])
            cisco_data['interfaces'] = ios_xe.get_interfaces()
            print("接口已恢复")

    # Task3. 配置新路由
    dst = '172.16.10.0'
    mask = '255.255.255.0'
    next = '10.1.1.100'
    if dst not in cisco_data['routeTable']:
        ios_xe.post_route(dst, mask, next)
        cisco_data['routeTable'] = ios_xe.get_route()
        print(f'新增了一条路由指向 {dst}，数据已更新')

    # Task4. 生成JSON
    ios_xe.to_json(cisco_data, 'data/cisco.json')

    ios_xe.device.disconnect()