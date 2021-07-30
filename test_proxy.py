from proxy_checking import ProxyChecker
import json



with open('proxies.txt') as f:
    proxies = f.read().splitlines()

checker = ProxyChecker()
print(proxies)
for proxy in proxies:
    print(proxy)
    print(checker.check_proxy(proxy))