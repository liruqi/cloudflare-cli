import tldextract

def get_second_level_domain(url):
    extracted = tldextract.extract(url)
    # 重新组合二级域名和顶级域名
    second_level_domain = "{}.{}".format(extracted.domain, extracted.suffix)
    return second_level_domain

# 示例
print(get_second_level_domain("http://openai.com"))          # openai.com
print(get_second_level_domain("http://chat.openai.com"))     # openai.com
print(get_second_level_domain("http://chat.openai.co.th"))   # openai.co.th
print(get_second_level_domain("http://chat.openai.gov.cn"))  # openai.gov.cn

