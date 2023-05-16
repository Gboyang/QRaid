import os
import base64
import redfish
import argparse
from concurrent.futures import ThreadPoolExecutor


class RedfishInterface(object):

    def __init__(self, login_host, login_account, login_password):
        '''
         Create REDFISH Object
        :param login_host: Host ip Address
        :param login_account: BMC ACCOUNT
        :param login_password: BMC Password
        '''
        self.REDFISH_OBJ = redfish.redfish_client(
            base_url="https://{}".format(login_host),
            username=login_account,
            password=login_password,
            default_prefix='/redfish/v1',
            timeout='10'
        )
        self.REDFISH_OBJ.login(auth="session")

    def get_interface_method(self, path, args=None, headers=None):
        '''
        Perform a GET request
        :param path: path: the URL path.
        :param args: the arguments to get.
        :param headers: dict of headers to be appended.
        :return: returns a rest request with method 'Get'
        '''
        response = self.REDFISH_OBJ.get(path, args=args, headers=headers)
        return response

    def post_interface_method(self, path, args=None, body=None, headers=None):
        '''Perform a POST request
        :param path: the URL path.
        :param args: the arguments to post.
        :param body: the body to the sent.
        :param headers: dict of headers to be appended.
        :return: returns a rest request with method 'Post'
        '''
        response = self.REDFISH_OBJ.post(path, args=args, body=body, headers=headers)
        return response

    def patch_interface_method(self, path, args=None, body=None, headers=None):
        '''
        Perform a PUT request
        :param path: the URL path.
        :param args: the arguments to patch.
        :param body: the body to the sent.
        :param headers: dict of headers to be appended.
        :return: returns a rest request with method 'Patch'
        '''
        response = self.REDFISH_OBJ.patch(path, args=args, body=body, headers=headers)
        return response

    def delete_interface_method(self, path, args=None, headers=None):
        """Perform a DELETE request

        :param path: the URL path.
        :type path: str.
        :param args: the arguments to delete.
        :type args: dict.
        :param headers: dict of headers to be appended.
        :type headers: dict.
        :returns: returns a rest request with method 'Delete'
        """
        response = self.REDFISH_OBJ.delete(path, args=args, headers=headers)
        return response

    def __exit__(self):
        '''
        :return:
        '''
        self.REDFISH_OBJ.logout()


class Main(object):

    def __init__(self):

        self.pool = ThreadPoolExecutor(50)

        self.parser = argparse.ArgumentParser(
            prog='QcRaid',
            usage="%(prog)s [options] [arguments]",
            description='FitServer R2280 Server RAID Tools <----> Developer: hyang107@fiberhome.com',
            allow_abbrev=True,
        )
        self.parser.add_argument('-C', '--Controller', type=int, metavar='', required=True, help='RAID Controller, 0/1')
        self.parser.add_argument('-H', '--host', metavar='', default='192.168.123.123',
                                 help='LAN interface Address [Default 192.168.123.123]')
        self.parser.add_argument('-f', '--files', metavar='', help='Read the IP address from the file')
        self.parser.add_argument('-U', '--user', metavar='', default='admin',
                                 help='Remote Host Account [Default "admin"]')
        self.parser.add_argument('-P', '--pwd', metavar='', default='admin',
                                 help='Remote Host password [Default "admin"]')
        self.parser.add_argument('-n', '--name', metavar='', help='Volume Name [Default: Same as the level parameter]')
        self.parser.add_argument('-l', '--level', metavar='', required=True, help='Volume Raid Level')
        self.parser.add_argument('-d', '--drives', metavar='', required=True, help='Drives [0, 1]')
        self.parser.add_argument('-i', '--init', metavar='', default='QuickInit',
                                 help='InitializationMode, UnInit/QuickInit/FullInit [Default:QuickInit]')
        self.parser.add_argument('-v', '--version', action="version", version="%(prog)s 1.1.1",
                                 help='Show version information')

        self.parser.add_argument('-sd', '--spanDepth', type=int, metavar='', default=1, help='spanDepth [Default: 1]')
        self.parser.add_argument('-sn', '--SpanNumber', type=int, metavar='', required=True, help='SpanNumber')
        self.parser.add_argument('--Bytes', metavar='', type=int, default=262144,
                                 help='OptimumIOSizeBytes [Default: 262144]')

        self.parser.add_argument('--DiskCache', metavar='', default='Disabled',
                                 help='DriveCachePolicy, Disabled/Enabled [Default Disabled]')
        self.parser.add_argument('--ReadPolicy', metavar='', default='ReadAhead',
                                 help='Read Policy, ReadAhead/NoReadAhead [Default ReadAhead]')
        self.parser.add_argument('--WritePolicy', metavar='', default='WriteBack',
                                 help='Write Policy, WriteThrough/WriteBack/WriteBackWithBBU [Default WriteBack]')
        self.parser.add_argument('--CachePolicy', metavar='', default='DirectIO',
                                 help='Default Cache Policy, DirectIO/CachedIO [Default DirectIO]')
        self.parser.add_argument('--AccessPolicy', metavar='', default='ReadWrite',
                                 help='Access Policy, ReadWrite/ReadOnly/Blocked [Default ReadWrite]')
        self.args_info = self.parser.parse_args()

    def __ip_address_info(self):
        '''
        GET HOST IP ADDRESS
        :return:
        '''
        self.ip_li = []
        if os.path.exists(self.args_info.files):
            with open(self.args_info.files, mode='r', encoding='utf-8') as f1:
                for ip in f1:
                    self.ip_li.append(ip.strip())
        return self.ip_li

    def __base64_jiami(self, str1=''):
        '''
        :param str1: jia mi
        :return:
        '''
        user = str1.encode(encoding='utf-8')
        state = base64.b64encode(user)
        return state.decode()

    def __is_disk(self):
        '''
        :return: Check if the value is correct
        '''
        try:
            disk_num = self.args_info.drives.split(',')
            Physical_disk = []
            for s in disk_num:
                b = int(s)
                Physical_disk.append(b)
            return Physical_disk
        except Exception as err:
            print('\n ERROR: %s' % err)
            exit()

    def __is_level(self):
        '''
        :return: Checking RAID levels
        '''
        level = ['RAID0', 'RAID1', 'RAID5', 'RAID10']
        if self.args_info.level in level:
            return self.args_info.level
        else:
            print('\n ERROR: -l parameter error')
            exit()

    def __headers(self):
        '''
        :return: Encapsulate header information
        '''
        authority = self.__base64_jiami("{}:{}".format(self.args_info.user, self.args_info.pwd))
        headers = {
            'Authorization': 'Basic {}'.format(authority),
            'Content-Type': 'application/json'
        }
        return headers

    def __url(self):
        '''
        :return: Handling url information
        '''
        url = '/redfish/v1/Systems/1/Storages/RAIDStorage%s/Volumes' % self.args_info.Controller
        return url

    def __body_content(self):
        '''
        :return: Wrapping body information
        '''
        if self.args_info.name is None:
            VolumeName = self.args_info.level
        else:
            VolumeName = self.args_info.name

        body_content = {
            "Oem": {
                "Public": {
                    "OptimumIOSizeBytes": self.args_info.Bytes,
                    "VolumeName": VolumeName,
                    "VolumeRaidLevel":  self.__is_level(),
                    "InitializationMode": self.args_info.init,
                    "DriveCachePolicy": self.args_info.DiskCache,
                    "DefaultReadPolicy": self.args_info.ReadPolicy,
                    "DefaultWritePolicy": self.args_info.WritePolicy,
                    "DefaultCachePolicy": self.args_info.CachePolicy,
                    "AccessPolicy": self.args_info.AccessPolicy,
                    "spanDepth": self.args_info.spanDepth,
                    "SpanNumber": self.args_info.SpanNumber,
                    "Drives": self.__is_disk()
                }
            }
        }
        return body_content

    def start(self):
        '''
        -----------------------------------------------------------------
        Author: hbyang
        blogs: https://www.cnblogs.com/hbyang
        ENV: R2280
        Description: This tool is developed for the R2280 device,
                     and realizes the configuration of RIAD by calling the device interface
        -----------------------------------------------------------------
        '''
        if self.args_info.files is not None:
            ip_info = self.__ip_address_info()
        else:
            ip_info = self.args_info.host.split()

        for ip in ip_info:
            def task(ipaddr, user, pwd):
                try:
                    redfish_obj = RedfishInterface(ipaddr, user, pwd)
                    result_code = redfish_obj.post_interface_method(self.__url(), headers=self.__headers(), body=self.__body_content()).status
                    if int(result_code) == 200:
                        print('Successful: return {}'.format(result_code))
                    else:
                        print('Full: return {}'.format(result_code))
                except:
                    print('\n ERROR: {} Connection Fail. Please check the network or user account'.format(ipaddr))

            self.pool.submit(task, ip, self.args_info.user, self.args_info.pwd)


if __name__ == '__main__':
    class_object = Main()
    class_object.start()