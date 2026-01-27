<template>
	<view class="content">
		<view class="header">
			<text class="title">Instagram 视频下载神器</text>
			<text class="subtitle">支持 Reels 短视频 / Post 帖子</text>
		</view>

		<view class="input-box">
			<input class="link-input" type="text" v-model="url" placeholder="请粘贴 Ins 分享链接..." />
			<view v-if="url" class="clear-btn" @click="url = ''">×</view>
		</view>

		<button class="main-btn" @click="parseVideo" :loading="loading" :disabled="loading">
			{{ loading ? '正在解析中...' : '一键提取视频' }}
		</button>

		<view v-if="videoData.url" class="result-card">
			<view class="video-container">
				<video id="myVideo" :src="videoData.url" controls autoplay class="video-player"></video>
			</view>
			
			<view class="info-box">
				<text class="video-title">{{ videoData.title }}</text>
			</view>

			<button class="save-btn" @click="saveVideo">
				⬇️ 保存到相册
			</button>
		</view>

		<view class="footer">
			<text>Powered by Python & UniApp</text>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				url: '',
				loading: false,
				videoData: {
					title: '',
					cover: '',
					url: ''
				}
			}
		},
		methods: {
			// 1. 调用后端解析
			parseVideo() {
				if (!this.url) {
					uni.showToast({ title: '请先粘贴链接', icon: 'none' });
					return;
				}

				this.loading = true;
				this.videoData = { title: '', cover: '', url: '' }; // 清空旧数据

				// 发送请求给你的 Python 后端
				// 注意：如果你在手机上测试，localhost 需要改成你电脑的 IP 地址
				uni.request({
					url: 'http://127.0.0.1:8000/api/parse', 
					method: 'POST',
					data: {
						url: this.url
					},
					success: (res) => {
						console.log('后端返回:', res.data);
						if (res.data.code === 200) {
							this.videoData = res.data.data;
							uni.showToast({ title: '解析成功', icon: 'success' });
						} else {
							uni.showModal({
								title: '解析失败',
								content: res.data.msg || '未知错误',
								showCancel: false
							});
						}
					},
					fail: (err) => {
						console.error(err);
						uni.showModal({
							title: '连接失败',
							content: '无法连接到后端，请检查 main.py 是否在运行',
							showCancel: false
						});
					},
					complete: () => {
						this.loading = false;
					}
				});
			},

			// 2. 下载并保存视频 (核心功能)
			saveVideo() {
				if (!this.videoData.url) return;

				uni.showLoading({ title: '正在下载...' });

				// A. 如果是 H5 (浏览器环境)
				// #ifdef H5
				window.open(this.videoData.url); // 直接打开新标签下载
				uni.hideLoading();
				uni.showToast({ title: '已开始下载', icon: 'none' });
				// #endif

				// B. 如果是 App (手机环境)
				// #ifndef H5
				uni.downloadFile({
					url: this.videoData.url,
					success: (res) => {
						if (res.statusCode === 200) {
							// 下载成功后，保存到相册
							uni.saveVideoToPhotosAlbum({
								filePath: res.tempFilePath,
								success: () => {
									uni.hideLoading();
									uni.showModal({
										title: '保存成功',
										content: '视频已保存到手机相册 📷',
										showCancel: false
									});
								},
								fail: (err) => {
									uni.hideLoading();
									uni.showToast({ title: '保存失败，请开启相册权限', icon: 'none' });
								}
							});
						} else {
							uni.hideLoading();
							uni.showToast({ title: '下载失败', icon: 'none' });
						}
					},
					fail: () => {
						uni.hideLoading();
						uni.showToast({ title: '网络错误，无法下载', icon: 'none' });
					}
				});
				// #endif
			}
		}
	}
</script>

<style>
	/* 页面整体背景 */
	page {
		background-color: #f5f6fa;
	}
	
	.content {
		padding: 30px 20px;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.header {
		margin-bottom: 30px;
		text-align: center;
	}

	.title {
		font-size: 24px;
		font-weight: bold;
		color: #333;
		display: block;
	}

	.subtitle {
		font-size: 14px;
		color: #888;
		margin-top: 5px;
		display: block;
	}

	/* 输入框区域 */
	.input-box {
		width: 100%;
		background: #fff;
		border-radius: 12px;
		padding: 5px 15px;
		display: flex;
		align-items: center;
		box-shadow: 0 4px 10px rgba(0,0,0,0.05);
		margin-bottom: 20px;
	}

	.link-input {
		flex: 1;
		height: 40px;
		font-size: 14px;
	}

	.clear-btn {
		color: #999;
		font-size: 20px;
		padding: 0 10px;
	}

	/* 主按钮 */
	.main-btn {
		width: 100%;
		background: linear-gradient(45deg, #007AFF, #0056b3);
		color: white;
		border-radius: 25px;
		font-size: 16px;
		font-weight: bold;
		margin-bottom: 20px;
		box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
	}

	.main-btn:active {
		opacity: 0.8;
	}

	/* 结果卡片 */
	.result-card {
		width: 100%;
		background: #fff;
		border-radius: 16px;
		overflow: hidden;
		box-shadow: 0 8px 20px rgba(0,0,0,0.08);
		animation: slideUp 0.3s ease-out;
	}

	.video-container {
		width: 100%;
		height: 300px; /* 竖屏视频高度 */
		background: #000;
	}

	.video-player {
		width: 100%;
		height: 100%;
	}

	.info-box {
		padding: 15px;
	}

	.video-title {
		font-size: 14px;
		color: #333;
		line-height: 1.4;
		font-weight: bold;
	}

	/* 保存按钮 */
	.save-btn {
		margin: 10px 15px 20px 15px;
		background-color: #34c759; /* 绿色代表下载 */
		color: white;
		border-radius: 10px;
		font-size: 15px;
	}

	.footer {
		margin-top: 50px;
		color: #ccc;
		font-size: 12px;
	}

	@keyframes slideUp {
		from { transform: translateY(20px); opacity: 0; }
		to { transform: translateY(0); opacity: 1; }
	}
</style>