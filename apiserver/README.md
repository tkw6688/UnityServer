之前获取的Json放到data/json文件夹中，同时获取http://xboxunity.net/Resources/Lib/TitleList.php?page=0&count=999&search=&sort=3&direction=1&category=0&filter=4，删掉最后的<br/>
    "Count": xx,<br/>
    "Pages": 1,<br/>
    "Page": 0,<br/>
    "Filter": "4",<br/>
    "Category": "0",<br/>
    "Sort": "3",<br/>
    "Direction": "1"<br/>
重命名为Homebrew.json放入data/json中<br/>
将下载的botart,boxartfront,boxartsm文件夹放进data文件夹<br/>
执行npm install axios cors express xml2js<br/>
修改server.js中第24行的IP地址<br/>