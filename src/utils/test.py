import requests

url = "https://api.zibal.ir/v1/facility/nationalCardOcr"
files = {
    "nationalCardBack": open("2.jpg", "rb"),
    "nationalCardFront": open("1.jpg", "rb"),
}
res = requests.post(
    headers={
        "Content-Type": "multipart/form-data",
        "Authorization": "Bearer ...",
    },
    url=url,
    files=files,
)

print(res.text)
