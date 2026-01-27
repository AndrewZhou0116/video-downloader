import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) # 允许跨域

@app.route('/api/parse', methods=['POST'])
def parse_instagram():
    # 1. 接收数据
    data = request.get_json()
    raw_content = data.get('url', '')

    if not raw_content:
        return jsonify({'code': 400, 'msg': '请粘贴 Ins 链接'})

    print('-------------------------------------------')
    print(f"⚡️ 收到原始内容: {raw_content}")

    # 2. 【关键步骤】清洗链接
    # Ins 分享的链接通常带一堆后缀 (例如 ?igsh=MzRl...), 必须去掉才能解析
    # 我们用正则提取纯净的 https://www.instagram.com/xxx/xxx/ 部分
    match = re.search(r'(https?://www\.instagram\.com/(?:reel|p)/[\w-]+)', raw_content)
    
    if not match:
        # 备用：万一格式不一样，尝试提取任意 http 链接
        match = re.search(r'(https?://[^\s]+)', raw_content)
    
    if not match:
        return jsonify({'code': 400, 'msg': '无法识别 Ins 链接，请检查复制内容'})
        
    target_url = match.group(1)
    print(f"🎯 清洗后的目标链接: {target_url}")

    # 3. 配置解析器 (针对 Ins 优化)
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # 模拟 iPhone 手机 App，Ins 对手机查得没那么严
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        # 只要 mp4，不要 m3u8 (m3u8不能直接下载)
        'format': 'best[ext=mp4]/best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 开始解析
            info = ydl.extract_info(target_url, download=False)
            
            # 提取数据
            video_url = info.get('url')
            title = info.get('title', '') or info.get('description', 'Instagram Video')
            cover = info.get('thumbnail', '')

            # 这里的 title 有时候是全部文案，太长了，截取前30个字
            if len(title) > 30:
                title = title[:30] + "..."

            if not video_url:
                raise Exception("未找到视频地址")

            result = {
                'title': title,
                'cover': cover,
                'url': video_url
            }

            print(f"✅ 解析成功! 视频地址长度: {len(video_url)}")
            return jsonify({'code': 200, 'msg': '解析成功', 'data': result})

    except Exception as e:
        error_msg = str(e)
        print(f"❌ 失败: {error_msg}")
        
        # 给用户更友好的提示
        if "Login required" in error_msg:
             return jsonify({'code': 500, 'msg': 'Ins 提示需要登录 (可能是私密账号或被风控)'})
        
        return jsonify({'code': 500, 'msg': '解析失败，请确保链接是公开的帖子'})

if __name__ == '__main__':
    print("🚀 Instagram 专用提取服务已启动 (端口 8000)...")
    app.run(host='0.0.0.0', port=8000)