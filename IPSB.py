import requests

def IPSB(ip):
    url = "https://api.ip.sb/geoip/" + ip
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"}

    try:
        response = requests.get(url, headers=headers, timeout=2)
        response.raise_for_status()
        data = response.json()

        country = data.get("country")
        province = data.get("region")
        city = data.get("city")
        isp = data.get("isp")

        location_info = ", ".join(filter(None, [country, province, city, district, isp]))

        return location_info
    except requests.exceptions.RequestException as e:
        return {"error": "api.ip.sb 请求超时(2s)，请切换其他API使用"}
    except Exception as e:
        return {"error": str(e)}