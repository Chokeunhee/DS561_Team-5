const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(bodyParser.json());

// 정적 파일 제공 (캐시 방지)
app.use('/images', (req, res, next) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    next();
}, express.static(path.join(__dirname)));

// Python 프로세스 생성
const python = spawn('python3', ['main.py']);

// Python stderr 로그 처리
python.stderr.on('data', (data) => {
    console.error(`[Python Log]: ${data.toString().trim()}`);
});

// API Endpoint
app.post('/chat', (req, res) => {
    const userMessage = req.body.message;

    if (!userMessage) {
        return res.status(400).json({ error: 'Message is required' });
    }

    // Python에 메시지 전달
    python.stdin.write(`${userMessage}\n`);

    // Python stdout 응답 처리
    python.stdout.once('data', (data) => {
        try {
            const response = JSON.parse(data.toString().trim());
            console.log('Python Response:', response); // 응답 로그 확인

            const imagePath = path.join(__dirname, 'tmap_route.png');

            let formattedReply = response.response;

            // === 경로 N === 앞뒤 줄바꿈 추가
            formattedReply = formattedReply.replace(/(=== 경로 \d+ ===)/g, "\n$1\n");

            // 번호 목록 앞에 줄바꿈 추가
            formattedReply = formattedReply.replace(/(\d+)\./g, "\n$1.");

            // ** 제거
            formattedReply = formattedReply.replace(/\*\*/g, '');

            // 괄호 안에서 줄바꿈 제거
            formattedReply = formattedReply.replace(/\(\s+/g, '(').replace(/\s+\)/g, ')');

            // HTML 줄바꿈으로 변환
            formattedReply = formattedReply.replace(/\n/g, '<br>');

            if (response.type === 'route') {
                const timestamp = Date.now();
                res.json({
                    reply: formattedReply,
                    image: fs.existsSync(imagePath) ? `/images/tmap_route.png?${timestamp}` : null
                });
            } else {
                if (fs.existsSync(imagePath)) {
                    fs.unlinkSync(imagePath);
                    console.log('Previous Tmap image deleted.');
                }
                res.json({ reply: formattedReply });
            }
        } catch (error) {
            console.error('Error parsing Python response:', error);
            res.status(500).json({ error: 'Failed to parse Python response.' });
        }
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// Python 프로세스 종료 처리
process.on('SIGINT', () => {
    python.kill();
    console.log('Python process terminated.');
    process.exit();
});