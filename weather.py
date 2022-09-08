import requests
import json
import redis

redis_host = "127.0.0.1"
redis_port = 6379
redis_password = ""
redis_cache_key = "py::weather::gz"
api_param_key = "自行高德申请"
api_param_city = "440100"
api_param_extensions = "all"
api_param_url_template = "http://restapi.amap.com/v3/weather/weatherInfo?key={}&city={}&extensions={}"

def assembleUrl():
    return api_param_url_template.format(api_param_key,api_param_city,api_param_extensions)

def getWeather(url):
    # 请求高德api
    response = requests.get(url)
    responseObj = json.loads(response.text)
    if "status" in responseObj and responseObj["status"] != '1':
        raise Exception("天气接口请求异常,rawResponse: {}".format(responseObj))
    else:
        return responseObj

def assemble(responseObj):
    # 规整成存储的格式 -> hash field:日期 value: 全部信息
    # 1.获取天气信息 判空
    if "forecasts" not in responseObj:
        raise Exception("天气接口返回预报信息为空,rawResponse: {}".format(responseObj))
    forecastList = responseObj["forecasts"]
    # 2.初始化字典
    toCacheDict = {}
    # 3.遍历forecastList 目前只查广州 里面只有一个元素
    for forecast in forecastList:
        if "casts" not in forecast:
            raise Exception("天气接口返回预报信息为空,rawResponse: {}".format(responseObj))
        castList = forecast["casts"]
        # 4.遍历castList 里面有当日和未来三日共四个元素
        for cast in castList:
            # 5.塞进toCacheDict
            toCacheDict[cast["date"]] = str(cast)
    # 6.return
    print(toCacheDict)
    return toCacheDict

def cacheToRedis(toCacheDict):
    # 连接redis
    redisCli = redis.Redis(host=redis_host,port=redis_port,password=redis_password,decode_responses=True)
    # hset
    for key, value in toCacheDict.items():
        redisCli.hset(redis_cache_key, key, value)

if __name__ == "__main__":
    try:
        cacheToRedis(assemble(getWeather(assembleUrl())))
    except Exception as ex:
        print("cache weather fail,err: {}".format(ex))