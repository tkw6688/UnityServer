之前获取的Json放到data/json文件夹中，同时获取http://xboxunity.net/Resources/Lib/TitleList.php?page=0&count=999&search=&sort=3&direction=1&category=0&filter=4，删掉最后的
    "Count": xx,
    "Pages": 1,
    "Page": 0,
    "Filter": "4",
    "Category": "0",
    "Sort": "3",
    "Direction": "1"
重命名为Homebrew.json放入data/json中
将下载的botart,boxartfront,boxartsm文件夹放进data文件夹
执行npm install axios cors express xml2js
修改server.js中第24行的IP地址