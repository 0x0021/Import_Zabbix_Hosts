# !/usr/bin/env python
# coding:utf-8
import json
import urllib2
from urllib2 import URLError
import xlrd


class zabbixtools:
    def __init__(self):
        self.url = "http://zabbix.jd-eit.com//api_jsonrpc.php"
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": "YouZabbixUserName",
                        "password": "YouZabbixPassword"
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print u"验证失败，检查你的账号和密码:",e.code
        else:
            response = json.loads(result.read())
            result.close()
            authID = response['result']
            return authID

    def get_data(self,data,hostip=""):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, '代码'):
                print 'The server could not fulfill the request.'
                print u'错误代码: ', e.code
            return 0
        else:
            response = json.loads(result.read())
            result.close()
            return response

    def host_get(self,hostip):
        # hostip = raw_input("\033[1;35;40m%s\033[0m" % 'Enter Your Check Host:Host_ip :')
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": ["hostid", "name", "status", "host"],
                    "filter": {"host": [hostip]}
                },
                "auth": self.authID,
                "id": 1
            })
        res = self.get_data(data)['result']
        if (res != 0) and (len(res) != 0):
            # for host in res:
            print type(res)
            host = res[0]
            return host['name']
        else:
            return ""

    def hostgroup_get(self,hostgroupName):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "output": "extend",
                    "filter": {"name": [hostgroupName]}
                },
                "auth": self.authID,
                "id": 1
            })
        res = self.get_data(data)['result']
        if (res != 0) and (len(res) != 0):
            # for host in res:
            print type(res)
            host = res[0]
            return host['groupid']
        else:
            return ""

    def template_get(self, templateName):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "host": [
                        templateName,
                    ]
                }
            },
            "auth": self.authID,
            "id": 1,
        })
        res = self.get_data(data)['result']
        if (res != 0) and (len(res) != 0):
            # for host in res:
            print type(res)
            host = res[0]
            return host['templateid']
        else:
            return ""

    def host_create(self, hostName, visibleName, hostIp, dnsName, proxyName, hostgroupName, templateName1,templateName2):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostName,
                "name": visibleName,
                # "proxy_hostid": self.proxy_get(proxyName),
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostIp,
                        "dns": dnsName,
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": self.hostgroup_get(hostgroupName)
                    }
                ],
                "templates": [
                    {
                        "templateid": self.template_get(templateName1)
                    }
                ],
            },
            "auth": self.authID,
            "id": 1
        })
        res = self.get_data(data)['result']

        if (res != 0) and (len(res) != 0):
            # for host in res:
            print type(res)
            # print res['hostids'][0]
            return res['hostids'][0]
        else:
            return ""

if __name__ == "__main__":
    Fuck = zabbixtools()
    workbook = xlrd.open_workbook("/Users/master/PycharmProjects/ZabbixTools/hostlist.xls")
    for row in xrange(workbook.sheets()[0].nrows):
        hostname = workbook.sheets()[0].cell(row, 0).value
        visible = workbook.sheets()[0].cell(row, 1).value
        hostip = workbook.sheets()[0].cell(row, 0).value
        dnsname = workbook.sheets()[0].cell(row, 2).value
        proxy = workbook.sheets()[0].cell(row, 3).value
        hostgroup = workbook.sheets()[0].cell(row, 4).value
        hosttemp = workbook.sheets()[0].cell(row, 5).value
        hosttemp1 = workbook.sheets()[0].cell(row, 6).value
        hostgroup = hostgroup.strip()
        hostnameGet = Fuck.host_get(hostname)
        if hostnameGet.strip() == '':
            Fuck.host_create(hostname, visible, hostip, dnsname, proxy, hostgroup, hosttemp, hosttemp1)
        else:
            print u"%s 已存在! 无法创建!\n" % hostnameGet
