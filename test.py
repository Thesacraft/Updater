import requests
response = requests.get("https://drive.google.com/file/d/1sn8o60FuUpcilnWXpaf-VqcfeuB8vM7-/view?usp=sharing")
# response.encoding = "utf-8"
hehe = response.text
print(hehe)