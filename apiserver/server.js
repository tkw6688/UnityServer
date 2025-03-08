const express = require('express');
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const xml2js = require('xml2js');
const cors = require('cors');

const app = express();
const port = 80;

// 图片类型路径映射
const imagePathMap = {
    'boxart': 'data/boxart',
    'boxartfront': 'data/boxartfront',
    'boxartsm': 'data/boxartsm'
};

// 允许跨域请求 (CORS)
app.use(cors());

// 解析JSON请求体
app.use(express.json());

const REPLACE_TEXT = "127.0.0.1"; // 你的服务器IP地址

// Json路由
app.get('/api/v2/Covers/:tid(*)', async (req, res) => {
    try {
        const tid = decodeURIComponent(req.params.tid.split('/')[0]); // 提取并解码tid，忽略tid后的数据
        // 修改文件路径解析部分
        const dataPath = path.join(process.cwd(), 'data/json');
        const filePath = path.join(dataPath, `${tid}.json`);

        let rawData;
        try {
            await fs.access(filePath, fs.constants.F_OK | fs.constants.R_OK);
            rawData = await fs.readFile(filePath, 'utf-8');
        } catch (err) {
            const homebrewPath = path.resolve(__dirname, 'data/json', 'Homebrew.json');
            try {
                const homebrewData = await fs.readFile(homebrewPath, 'utf-8');
                let homebrewJson = JSON.parse(homebrewData);

                // 获取数组结构
                if (typeof homebrewJson === 'object' && !Array.isArray(homebrewJson)) {
                    const possibleArrays = Object.values(homebrewJson);
                    homebrewJson = possibleArrays.find(item => Array.isArray(item)) || [];
                }

                // 仅检查 HBTitleID
                const found = homebrewJson.find(item =>
                    item?.HBTitleID?.toLowerCase() === tid.toLowerCase()
                );

                if (!found) {
                    return res.status(404).json({
                        error: 'HBTitleID not found',
                        searchedId: tid
                    });
                }

                // 尝试读取对应 TitleID 的文件
                const titleIdPath = path.resolve(__dirname, 'data/json', `${found.TitleID}.json`);
                try {
                    rawData = await fs.readFile(titleIdPath, 'utf-8');
                } catch (titleErr) {
                    // 如果找不到对应文件，返回 Homebrew 中的数据
                    rawData = JSON.stringify(found);
                }
            } catch (homebrewErr) {
                return res.status(500).json({
                    error: 'Failed to process Homebrew.json',
                    details: homebrewErr.message
                });
            }
        }

        // 替换所有 XboxUnity 为指定文本
        rawData = rawData.replace(/XboxUnity.net/g, REPLACE_TEXT);

        try {
            const jsonData = JSON.parse(rawData);
            res.status(200).json(jsonData);
        } catch (err) {
            return res.status(500).json({ error: 'parse failed' });
        }
    } catch (error) {
        res.status(500).json({ error: 'unexpected error' });
    }
});

// 图片路由处理器
app.get('/api/:type(boxart|boxartfront|boxartsm)/:id([0-9]+)', async (req, res) => {
    try {
        const { type, id } = req.params;
        const basePath = imagePathMap[type];
        const filePath = path.join(process.cwd(), basePath, `${id}.png`);

        try {
            await fs.access(filePath, fs.constants.F_OK | fs.constants.R_OK);
        } catch (err) {
            return res.status(404).json({ error: 'not found' });
        }

        res.sendFile(filePath);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'internal server error' });
    }
});

// Proxy路由处理器
app.get('*', async (req, res) => {
    try {
        // 构建目标URL，只替换域名部分
        const targetUrl = `http://catalog.xboxlive.com${req.url}`;
        console.log('Forwarding to:', targetUrl);

        // 发送请求到 Xbox Live
        const response = await axios.get(targetUrl);

        // 解析 XML
        const parser = new xml2js.Parser();
        const result = await parser.parseStringPromise(response.data);

        function removeNameField(obj) {
            // 检查传入的参数是否为对象
            if (typeof obj !== 'object' || obj === null) return;

            // 如果对象中有 entry 数组，则遍历该数组并删除每个元素中的 title 字段
            if (Array.isArray(obj.entry)) {
                obj.entry.forEach(item => {
                    delete item.title;
                });
            }
            if (Array.isArray(obj['live:media'])) {
                obj['live:media'].forEach(item => {
                    delete item['live:reducedTitle'];
                });
            }
            if (Array.isArray(obj['live:media'])) {
                obj['live:media'].forEach(item => {
                    delete item['live:gameReducedTitle'];
                });
            }
            if (Array.isArray(obj['live:media'])) {
                obj['live:media'].forEach(item => {
                    delete item['live:fullTitle'];
                });
            }
            // 遍历对象的所有值
            Object.values(obj).forEach(value => {
                // 如果值是一个数组，则遍历数组中的每个元素并递归调用 removeNameField
                if (Array.isArray(value)) {
                    value.forEach(item => removeNameField(item));
                }
                // 如果值是一个对象，则递归调用 removeNameField
                else if (typeof value === 'object') {
                    removeNameField(value);
                }
            });
        }

        removeNameField(result);

        // 转回 XML
        const builder = new xml2js.Builder();
        const modifiedXml = builder.buildObject(result);

        res.header('Content-Type', 'application/xml');
        res.send(modifiedXml);

    } catch (error) {
        console.error('Title Block Error');
        res.status(500).send('Internal Server Error');
    }
});

// 启动服务器，监听所有接口
app.listen(port, '0.0.0.0', () => {
    console.log("Author:Homebrew Channel");
    console.log("GitHub:https://github.com/tkw6688");
    console.log("Bilibili:https://space.bilibili.com/618370810");
    console.log(`Server running at http://0.0.0.0:${port}`);
});