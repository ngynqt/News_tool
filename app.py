#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask Application for Cafef Article Scraper with Gemini UI
"""

import os
import json
import logging
from flask import Flask, jsonify, request, render_template_string
from cafef_scraper import scrape_cafef_article, load_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cafef_app")

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def save_config(config_data: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False


# HTML Template with premium CSS and Javascript built in
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="page-title">Cafef Scraper & AI Facebook Summarizer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 25, 40, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-color: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.35);
            --success-color: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Plus Jakarta Sans', sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        body {
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 10% 10%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 90% 90%, rgba(168, 85, 247, 0.15) 0px, transparent 50%),
                radial-gradient(at 50% 50%, rgba(20, 24, 33, 1) 0px, transparent 100%);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: var(--font-body);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2.5rem 1.5rem;
        }

        /* Header design */
        header {
            text-align: center;
            margin-bottom: 3rem;
            animation: fadeInDown 0.8s ease;
        }

        h1 {
            font-family: var(--font-display);
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 1.1rem;
            font-weight: 400;
        }

        /* Glassmorphism Cards */
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(16px) saturate(180%);
            -webkit-backdrop-filter: blur(16px) saturate(180%);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            margin-bottom: 2rem;
        }

        /* Config Card styling */
        .config-toggle {
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-weight: 600;
            color: var(--text-main);
            font-size: 0.95rem;
            background: rgba(255, 255, 255, 0.03);
            padding: 0.8rem 1.5rem;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            margin-bottom: 1.5rem;
            user-select: none;
        }

        .config-toggle:hover {
            background: rgba(99, 102, 241, 0.08);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .config-content {
            display: none;
            padding-top: 1rem;
            animation: slideDown 0.3s ease;
        }

        .config-content.show {
            display: block;
        }

        /* Inputs & Labels */
        .form-group {
            margin-bottom: 1.5rem;
            position: relative;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }

        .input-wrapper {
            display: flex;
            gap: 0.8rem;
        }

        input[type="text"], input[type="password"], select {
            flex: 1;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            color: var(--text-main);
            font-family: var(--font-body);
            font-size: 1rem;
            outline: none;
        }

        select option {
            background-color: var(--bg-color);
            color: var(--text-main);
        }

        input[type="text"]:focus, input[type="password"]:focus, select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 15px var(--accent-glow);
        }

        /* Buttons styling */
        .btn {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            border: none;
            border-radius: 12px;
            color: white;
            cursor: pointer;
            font-family: var(--font-display);
            font-size: 1rem;
            font-weight: 600;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            box-shadow: none;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: none;
        }

        /* Loader & spinner */
        .loading-container {
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            text-align: center;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(99, 102, 241, 0.1);
            border-top: 4px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1.5rem;
        }

        /* Results view grid layout */
        .results-container {
            display: none;
            grid-template-columns: 1.4fr 1fr;
            gap: 2rem;
            animation: fadeInUp 0.6s ease;
        }

        @media (max-width: 900px) {
            .results-container {
                grid-template-columns: 1fr;
            }
        }

        /* Text content section */
        .content-card h2 {
            font-family: var(--font-display);
            font-size: 1.8rem;
            font-weight: 700;
            line-height: 1.3;
            margin-bottom: 1.2rem;
        }

        .metadata {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1rem;
        }

        .metadata span {
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .sapo-box {
            background: rgba(99, 102, 241, 0.08);
            border-left: 4px solid var(--accent-color);
            padding: 1.2rem;
            border-radius: 0 12px 12px 0;
            margin-bottom: 1.8rem;
            font-weight: 500;
            color: #e5e7eb;
        }

        .body-text p {
            margin-bottom: 1.2rem;
            color: #d1d5db;
            font-size: 1.05rem;
        }

        /* FB Summary Card (Right pane) */
        .summary-card {
            border: 1.5px solid rgba(99, 102, 241, 0.2);
            position: sticky;
            top: 2rem;
        }

        .summary-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.2rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 0.8rem;
        }

        .summary-card-title {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 700;
            color: #a78bfa;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .summary-textarea {
            width: 100%;
            min-height: 380px;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.2rem;
            color: #e5e7eb;
            font-family: inherit;
            font-size: 0.95rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
        }

        .summary-textarea:focus {
            border-color: var(--accent-color);
        }

        /* Image gallery grid */
        .image-gallery-title {
            font-family: var(--font-display);
            font-size: 1.25rem;
            font-weight: 700;
            margin: 2rem 0 1rem;
            color: var(--text-main);
        }

        .image-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        .image-card {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
        }

        .image-card img {
            width: 100%;
            height: auto;
            max-height: 300px;
            object-fit: cover;
            display: block;
        }

        .image-caption {
            padding: 0.8rem 1rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            border-top: 1px solid var(--card-border);
            font-style: italic;
        }

        /* Success alerts */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--success-color);
            color: white;
            padding: 1rem 1.8rem;
            border-radius: 12px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transform: translateY(150%);
            z-index: 1000;
        }

        .toast.show {
            transform: translateY(0);
        }

        /* Animations */
        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Web Tóm Tắt Báo ( TRUSTFIN )</h1>
            <p class="subtitle">Nhập link bài báo và copy tóm tắt từ AI </p>
        </header>

        <!-- API Config Accordion -->
        <div class="card" style="padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem;">
            <div class="config-toggle" onclick="toggleConfig()">
                <span>⚙️ Cấu hình API Gemini & Model</span>
                <span id="toggle-icon">▼</span>
            </div>
            <div class="config-content" id="config-panel">
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label for="api-key-input">Gemini API Key</label>
                    <input type="password" id="api-key-input" placeholder="Nhập Gemini API Key của bạn..." style="width: 100%;">
                </div>

                <div class="form-group" style="margin-bottom: 1rem;">
                    <label for="model-select">Mô hình Gemini (Model)</label>
                    <select id="model-select" onchange="handleModelChange()" style="width: 100%;">
                        <optgroup label="⭐ Mới nhất &mdash; Gemini 3.x">
                            <option value="gemini-3.5-flash">Gemini 3.5 Flash (Mới nhất &amp; Nhanh)</option>
                            <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite (Nhẹ, tiết kiệm quota)</option>
                            <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro (Chất lượng cao)</option>
                            <option value="gemini-3-flash-preview">Gemini 3 Flash (Preview)</option>
                        </optgroup>
                        <optgroup label="✅ Gemini 2.5 &mdash; Ổn định, Khuyên dùng">
                            <option value="gemini-2.5-flash" selected>Gemini 2.5 Flash ⭐ Khuyên dùng</option>
                            <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite (Nhanh &amp; Tiết kiệm)</option>
                            <option value="gemini-2.5-pro">Gemini 2.5 Pro (Chất lượng tốt nhất)</option>
                        </optgroup>
                        <optgroup label="Gemini 2.0">
                            <option value="gemini-2.0-flash">Gemini 2 Flash</option>
                            <option value="gemini-2.0-flash-lite">Gemini 2 Flash Lite</option>
                        </optgroup>
                        <optgroup label="Tùy chỉnh">
                            <option value="custom">Nhập tên model khác...</option>
                        </optgroup>
                    </select>
                </div>

                <div class="form-group" id="custom-model-wrapper" style="display: none; margin-bottom: 1.5rem;">
                    <label for="custom-model-input">Tên Model Tùy Chỉnh</label>
                    <input type="text" id="custom-model-input" placeholder="Ví dụ: gemini-2.0-pro-exp" style="width: 100%;">
                </div>

                <button class="btn btn-secondary" onclick="saveConfig()">Lưu cấu hình</button>
            </div>
        </div>

        <!-- Input Box -->
        <div class="card">
            <div class="form-group" style="margin-bottom: 0;">
                <label for="url-input">Đường dẫn (URL) bài viết Cafef</label>
                <div class="input-wrapper">
                    <input type="text" id="url-input" placeholder="Ví dụ: https://cafef.vn/ba-dieu-anh-chi-gan-tram-ty-dong-om-15-co-phan-mot-doanh-nghiep-xay-dung-188260706234810936.chn">
                    <button class="btn" id="submit-btn" onclick="startScraping()">
                        <span></span> Phân tích và tóm tắt
                    </button>
                </div>
            </div>
        </div>

        <!-- Loader -->
        <div class="card loading-container" id="loader">
            <div class="spinner"></div>
            <h3 style="font-family: var(--font-display); font-size: 1.3rem; margin-bottom: 0.5rem;">Đang xử lý dữ liệu...</h3>
            <p class="subtitle" style="font-size: 0.95rem;">Đang phân tích và tóm tắt bài viết ...</p>
        </div>

        <!-- Results Grid -->
        <div class="results-container" id="results">
            <!-- Left Pane: Content -->
            <div class="card content-card">
                <h2 id="art-title">Tiêu đề bài viết</h2>
                <div class="metadata">
                    <span>📅 <b id="art-date">01/01/2026</b></span>
                    <span>🔗 <a href="#" id="art-link" target="_blank" style="color: var(--accent-color); text-decoration: none;">Xem bài viết gốc</a></span>
                </div>
                <div class="sapo-box" id="art-sapo">
                    Đây là phần tóm tắt ngắn (sapo) của bài viết.
                </div>
                <div class="body-text" id="art-body">
                    <!-- Paragraphs here -->
                </div>
            </div>

            <!-- Right Pane: FB Summary & Images -->
            <div>
                <!-- FB Summary -->
                <div class="card summary-card" id="fb-summary-card">
                    <div class="summary-card-header">
                        <span class="summary-card-title">📱 Bản tóm tắt Facebook</span>
                        <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.85rem;" onclick="copySummary()" id="copy-btn">
                            📄 Sao chép
                        </button>
                    </div>
                    <textarea class="summary-textarea" id="art-fb-summary" readonly></textarea>
                </div>

                <!-- Images Gallery -->
                <div id="art-images-section">
                    <h3 class="image-gallery-title">🖼️ Hình ảnh trong bài viết</h3>
                    <div class="image-grid" id="art-images-grid">
                        <!-- Image cards here -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Success Toast -->
    <div class="toast" id="toast">
        <span>✅</span> <span id="toast-text">Đã lưu cấu hình thành công!</span>
    </div>

    <script>
        // Toggle Config Section
        function toggleConfig() {
            const panel = document.getElementById('config-panel');
            const icon = document.getElementById('toggle-icon');
            panel.classList.toggle('show');
            if (panel.classList.contains('show')) {
                icon.textContent = '▲';
            } else {
                icon.textContent = '▼';
            }
        }

        // Handle model selection change
        function handleModelChange() {
            const select = document.getElementById('model-select');
            const customWrapper = document.getElementById('custom-model-wrapper');
            if (select.value === 'custom') {
                customWrapper.style.display = 'block';
            } else {
                customWrapper.style.display = 'none';
            }
        }

        // Fetch current Config
        async function fetchConfig() {
            try {
                const response = await fetch('/api/config');
                const config = await response.json();
                if (config.gemini_api_key) {
                    document.getElementById('api-key-input').value = config.gemini_api_key;
                }
                if (config.gemini_model) {
                    const select = document.getElementById('model-select');
                    const options = Array.from(select.options).map(opt => opt.value);
                    if (options.includes(config.gemini_model)) {
                        select.value = config.gemini_model;
                    } else {
                        select.value = 'custom';
                        document.getElementById('custom-model-input').value = config.gemini_model;
                    }
                    handleModelChange();
                }
            } catch (err) {
                console.error("Không thể lấy cấu hình:", err);
            }
        }

        // Save Config
        async function saveConfig() {
            const key = document.getElementById('api-key-input').value.trim();
            const select = document.getElementById('model-select');
            let model = select.value;
            if (model === 'custom') {
                model = document.getElementById('custom-model-input').value.trim();
            }
            if (!model) {
                showToast("Vui lòng chọn hoặc nhập mô hình!");
                return;
            }
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ gemini_api_key: key, gemini_model: model })
                });
                const result = await response.json();
                if (result.success) {
                    showToast("Đã lưu cấu hình thành công!");
                } else {
                    showToast("Lỗi lưu cấu hình!");
                }
            } catch (err) {
                showToast("Lỗi kết nối máy chủ!");
            }
        }

        // Toast feedback
        function showToast(text) {
            const toast = document.getElementById('toast');
            document.getElementById('toast-text').textContent = text;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        // Copy FB post draft
        function copySummary() {
            const textarea = document.getElementById('art-fb-summary');
            textarea.select();
            document.execCommand('copy');
            
            const btn = document.getElementById('copy-btn');
            btn.textContent = '✅ Đã chép!';
            btn.style.background = 'var(--success-color)';
            btn.style.color = 'white';
            
            showToast("Đã sao chép bản tóm tắt vào clipboard!");
            
            setTimeout(() => {
                btn.textContent = '📄 Sao chép';
                btn.style.background = 'rgba(255, 255, 255, 0.05)';
                btn.style.color = 'var(--text-main)';
            }, 2500);
        }

        // Scrape Execution
        async function startScraping() {
            const urlInput = document.getElementById('url-input').value.trim();
            if (!urlInput) {
                showToast("Vui lòng nhập đường dẫn bài viết!");
                return;
            }

            // Hide results, show loader
            document.getElementById('results').style.display = 'none';
            document.getElementById('loader').style.display = 'flex';
            document.getElementById('submit-btn').disabled = true;

            try {
                const response = await fetch('/api/scrape', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput })
                });
                
                const data = await response.json();
                
                if (data.title) {
                    // Populate data
                    document.getElementById('art-title').textContent = data.title;
                    document.getElementById('art-date').textContent = data.publish_time || "Không rõ ngày đăng";
                    document.getElementById('art-link').href = data.url;
                    
                    if (data.sapo) {
                        document.getElementById('art-sapo').textContent = data.sapo;
                        document.getElementById('art-sapo').style.display = 'block';
                    } else {
                        document.getElementById('art-sapo').style.display = 'none';
                    }

                    // Render content paragraphs
                    const bodyContainer = document.getElementById('art-body');
                    bodyContainer.innerHTML = '';
                    if (data.content) {
                        const paras = data.content.split('\\n\\n');
                        paras.forEach(p => {
                            if (p.trim()) {
                                const pTag = document.createElement('p');
                                pTag.textContent = p.trim();
                                bodyContainer.appendChild(pTag);
                            }
                        });
                    } else {
                        bodyContainer.innerHTML = '<p style="color: var(--text-muted); font-style: italic;">Không tìm thấy nội dung chi tiết dạng chữ.</p>';
                    }

                    // Render FB summary
                    const summaryCard = document.getElementById('fb-summary-card');
                    if (data.facebook_summary) {
                        document.getElementById('art-fb-summary').value = data.facebook_summary;
                        document.getElementById('copy-btn').style.display = 'block';
                        summaryCard.style.display = 'block';
                    } else {
                        document.getElementById('art-fb-summary').value = "Chưa cấu hình Gemini API Key hoặc xảy ra lỗi khi tạo tóm tắt. Bạn hãy kiểm tra lại cấu hình API Key ở phía trên.";
                        document.getElementById('copy-btn').style.display = 'none';
                        summaryCard.style.display = 'block';
                    }

                    // Render Images Gallery
                    const imgGrid = document.getElementById('art-images-grid');
                    const imgSection = document.getElementById('art-images-section');
                    imgGrid.innerHTML = '';
                    
                    if (data.images && data.images.length > 0) {
                        imgSection.style.display = 'block';
                        data.images.forEach(img => {
                            const card = document.createElement('div');
                            card.className = 'image-card';
                            
                            const imgEl = document.createElement('img');
                            imgEl.src = img.url;
                            imgEl.alt = img.caption || 'Ảnh bài viết';
                            card.appendChild(imgEl);
                            
                            if (img.caption) {
                                const cap = document.createElement('div');
                                cap.className = 'image-caption';
                                cap.textContent = img.caption;
                                card.appendChild(cap);
                            }
                            imgGrid.appendChild(card);
                        });
                    } else {
                        imgSection.style.display = 'none';
                    }

                    // Transition to show results
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('results').style.display = 'grid';
                } else {
                    showToast("Cào bài viết thất bại! Hãy thử lại.");
                    document.getElementById('loader').style.display = 'none';
                }
            } catch (err) {
                console.error("Lỗi khi cào dữ liệu:", err);
                showToast("Lỗi máy chủ hoặc mất kết nối mạng!");
                document.getElementById('loader').style.display = 'none';
            } finally {
                document.getElementById('submit-btn').disabled = false;
            }
        }

        // Initialize Page
        window.onload = function() {
            fetchConfig();
        };
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.json or {}
        key = data.get("gemini_api_key", "").strip()
        model = data.get("gemini_model", "gemini-2.5-flash").strip()
        config = load_config()
        config["gemini_api_key"] = key
        config["gemini_model"] = model
        
        success = save_config(config)
        return jsonify({"success": success})
    else:
        config = load_config()
        return jsonify({
            "gemini_api_key": config.get("gemini_api_key", ""),
            "gemini_model": config.get("gemini_model", "gemini-2.5-flash")
        })


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing URL"}), 400
        
    config = load_config()
    api_key = os.environ.get("GEMINI_API_KEY") or config.get("gemini_api_key")
    model_name = config.get("gemini_model", "gemini-2.5-flash")
    
    logger.info(f"API request to scrape: {url} using model: {model_name}")
    result = scrape_cafef_article(url, api_key=api_key, model_name=model_name)
    return jsonify(result)


if __name__ == "__main__":
    logger.info(f"Starting server on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
