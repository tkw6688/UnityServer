from dnslib import *
from dnslib.server import DNSServer, DNSHandler, BaseResolver
import argparse

class HijackResolver(BaseResolver):
    def __init__(self, hijack_map, upstream_dns="119.29.29.29"):
        """
        初始化解析器
        hijack_map: 域名到IP的映射字典
        upstream_dns: 上游DNS服务器
        """
        self.hijack_map = hijack_map
        self.upstream_dns = upstream_dns

    def resolve(self, request, handler):
        """处理DNS请求"""
        reply = request.reply()
        qname = str(request.q.qname)
        processed_qname = qname.rstrip('.')

        print(f"原始 qname: {qname}")
        print(f"处理后 qname: {processed_qname}")
        print(f"hijack_map: {self.hijack_map}")

        # 检查是否是需要劫持的域名
        if processed_qname in self.hijack_map:
            print(f"域名 {processed_qname} 在 hijack_map 中，将被劫持")
            # 如果是需要劫持的域名，返回指定IP
            hijacked_ip = self.hijack_map[processed_qname]
            reply.add_answer(RR(
                rname=request.q.qname,
                rtype=QTYPE.A,
                rclass=1,
                ttl=60,
                rdata=A(hijacked_ip)
            ))
            print(f"返回劫持 IP: {hijacked_ip}")
        else:
            print(f"域名 {processed_qname} 不在 hijack_map 中，将转发到上游 DNS")
            # 如果不是需要劫持的域名，转发到上游DNS服务器
            try:
                upstream_reply = DNSRecord.parse(
                    DNSRecord.question(qname).send(self.upstream_dns, 53, timeout=3)
                )
                reply.add_answer(*upstream_reply.rr)
                print(f"上游 DNS 响应: {upstream_reply}")
            except Exception as e:
                print(f"解析错误: {e}")
                # 当上游解析错误时，返回 SERVFAIL 响应
                reply.header.rcode = RCODE.SERVFAIL
                return reply # 确保返回 reply 对象，而不是 None

        return reply

def main():
    parser = argparse.ArgumentParser(description='DNS劫持工具')
    parser.add_argument('--port', type=int, default=53, help='监听端口 (默认: 53)')
    parser.add_argument('--upstream', default='119.29.29.29', help='上游DNS服务器 (默认: 119.29.29.29)')
    args = parser.parse_args()

    # 配置需要劫持的域名和对应IP
    hijack_map = {
        "catalog.xboxlive.com": "your ip",  # 你的服务器IP
        "xboxunity.net": "your ip"
        # 可以添加更多域名
    }

    # 创建DNS服务器
    resolver = HijackResolver(hijack_map, args.upstream)
    server = DNSServer(resolver, port=args.port,address="0.0.0.0")

    print(f"DNS劫持服务器已启动在端口 {args.port}")
    print("劫持映射:")
    for domain, ip in hijack_map.items():
        print(f"{domain} -> {ip}")
    print(f"其他域名将转发到 {args.upstream}")

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.stop()

if __name__ == '__main__':
    main()