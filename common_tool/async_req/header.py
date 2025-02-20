from fake_useragent import UserAgent

ua = UserAgent()

AntiHeader = {
    "User-Agent": ua.chrome,
    # "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    # "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # "Accept-Encoding": "gzip, deflate, br",
    # "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    # "Sec-Ch-Ua-Mobile": "?0",
    # "Sec-Ch-Ua-Platform": '"Linux"',
    # "Upgrade-Insecure-Requests": '1',
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    # "Cache-Control": "no-cache",
    # "Pragma": "no-cache",
    # "Sec-Fetch-Dest": "document",
    # "Sec-Fetch-Mode": "navigate",
    # "Sec-Fetch-Site": "none",
    # "Sec-Fetch-User": '?1',
}
