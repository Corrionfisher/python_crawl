import urllib.request as req

#抓取一個頁面的標題
def getData(url):

    #建立request物件，附加headers資訊
    request=req.Request(url, headers={
        "Cookie":"over18=1",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    })
    #抓取原始碼
    with req.urlopen(request) as response:
        data = response.read().decode("utf-8")


    #導入beautifulsoup
    import bs4
    #讓bs認知到原始碼是html格式，並命名原始碼為root
    root = bs4.BeautifulSoup(data, "html.parser")

    #印出網頁的名稱
    print(root.title.string)#print(要印出的部分.標籤.string) 告訴python title是string

    #找文章名稱
    titles = root.find_all("div", class_ = "title") #尋找所有符合class="title"的div標籤，find_all("標籤名稱", 篩選條件)

    for title in titles:
        if title.a != None:
            print(title.a.string)

    #抓第二頁
    nextlink = root.find("a", string = "‹ 上頁") #找到內文是"‹ 上頁"的a標籤
    return nextlink["href"]

#主程序:抓取多個頁面的標題
Pageurl = "https://www.ptt.cc/bbs/Gossiping/index.html"
count = 0
while count < 10: #要印的頁數
    Pageurl = "https://www.ptt.cc" + getData(Pageurl)
    count += 1
