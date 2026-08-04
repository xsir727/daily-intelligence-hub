/* ============================================
   Daily Intelligence Hub - 星空粒子 + 数据渲染
   ============================================ */

(function () {
    'use strict';

    // ==================== Canvas 星空粒子 ====================
    const canvas = document.getElementById('starfield');
    const ctx = canvas.getContext('2d');
    const stars = [];
    const STAR_COUNT = 320;
    const MAX_DEPTH = 30;

    let mouseX = -1000;
    let mouseY = -1000;
    let width, height;

    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // 追踪鼠标
    canvas.style.pointerEvents = 'none';
    document.addEventListener('mousemove', function (e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    document.addEventListener('mouseleave', function () {
        mouseX = -1000;
        mouseY = -1000;
    });

    // 初始化星星
    for (let i = 0; i < STAR_COUNT; i++) {
        stars.push({
            x: Math.random() * width,
            y: Math.random() * height,
            z: Math.random() * MAX_DEPTH,
            radius: 0.5 + Math.random() * 1.8,
            opacity: 0.3 + Math.random() * 0.7,
            twinkleSpeed: 0.005 + Math.random() * 0.02,
            twinklePhase: Math.random() * Math.PI * 2,
            hue: 200 + Math.random() * 40  // 蓝白色调星星
        });
    }

    function drawStars() {
        ctx.clearRect(0, 0, width, height);

        const now = Date.now() / 1000;

        stars.forEach(function (star) {
            // 缓慢向下漂移
            star.y += 0.15 + star.z * 0.01;
            if (star.y > height + 10) {
                star.y = -10;
                star.x = Math.random() * width;
            }

            // 闪烁
            const twinkle = 0.5 + 0.5 * Math.sin(now * star.twinkleSpeed * 60 + star.twinklePhase);
            const alpha = star.opacity * twinkle;

            // 鼠标交互 - 吸引附近星星
            const dx = mouseX - star.x;
            const dy = mouseY - star.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            let offsetX = 0, offsetY = 0;
            if (dist < 120) {
                const force = (120 - dist) / 120;
                offsetX = dx * force * 0.03;
                offsetY = dy * force * 0.03;
            }

            const sx = star.x + offsetX;
            const sy = star.y + offsetY;

            // 绘制星星
            ctx.beginPath();
            ctx.arc(sx, sy, star.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'hsla(' + star.hue + ', 60%, 80%, ' + alpha + ')';
            ctx.fill();

            // 亮星加辉光
            if (star.radius > 1.2 && alpha > 0.6) {
                ctx.beginPath();
                ctx.arc(sx, sy, star.radius * 2.5, 0, Math.PI * 2);
                ctx.fillStyle = 'hsla(' + star.hue + ', 70%, 70%, ' + (alpha * 0.15) + ')';
                ctx.fill();
            }
        });
    }

    // 鼠标交互粒子
    const particles = [];
    const MAX_PARTICLES = 60;

    document.addEventListener('mousemove', function (e) {
        if (particles.length < MAX_PARTICLES) {
            particles.push({
                x: e.clientX,
                y: e.clientY,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                life: 1.0,
                decay: 0.012 + Math.random() * 0.025,
                radius: 0.8 + Math.random() * 1.5
            });
        }
    });

    function drawParticles() {
        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;

            if (p.life <= 0) {
                particles.splice(i, 1);
                continue;
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'hsla(210, 80%, 70%, ' + (p.life * 0.6) + ')';
            ctx.fill();
        }
    }

    function animate() {
        drawStars();
        drawParticles();
        requestAnimationFrame(animate);
    }
    animate();

    // ==================== 导航阴影 ====================
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 10) {
            navbar.classList.add('shadow');
        } else {
            navbar.classList.remove('shadow');
        }
    });

    // ==================== 平滑滚动（已由 CSS scroll-behavior 处理，此处处理锚点偏移） ====================

    // ==================== 数据加载与渲染 ====================
    const DATA_MAP = {
        'content-natural-resources': 'data/natural-resources.json',
        'content-marine-land': 'data/marine-land.json',
        'content-ai': 'data/ai.json',
        'content-social-science': 'data/social-science.json'
    };

    function renderCards(container, items) {
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="empty-msg">暂无数据</div>';
            return;
        }

        let html = '';
        items.forEach(function (item) {
            const title = escapeHtml(item.title || '无标题');
            const summary = escapeHtml(item.summary || '');
            const source = escapeHtml(item.source || '');
            const date = escapeHtml(item.date || '');
            const url = escapeHtml(item.url || '#');

            html += '<div class="info-card">';
            html += '  <div class="card-title">' + title + '</div>';
            if (summary) {
                html += '  <div class="card-summary">' + summary + '</div>';
            }
            html += '  <div class="card-meta">';
            if (date) {
                html += '    <span class="date">' + date + '</span>';
            }
            if (source) {
                html += '    <span class="source">' + source + '</span>';
            }
            html += '    <a href="' + url + '" target="_blank" rel="noopener">原文链接</a>';
            html += '  </div>';
            html += '</div>';
        });

        container.innerHTML = html;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function loadData(containerId, jsonPath) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '<div class="loading-msg">数据加载中，请稍候...</div>';

        fetch(jsonPath)
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status);
                }
                return response.json();
            })
            .then(function (data) {
                renderCards(container, data.items);
            })
            .catch(function (err) {
                console.warn('加载 ' + jsonPath + ' 失败:', err);
                container.innerHTML = '<div class="empty-msg">数据加载中，请稍候...</div>';
            });
    }

    // 启动所有数据加载
    Object.keys(DATA_MAP).forEach(function (containerId) {
        loadData(containerId, DATA_MAP[containerId]);
    });

    // ==================== 电子宠物 - 龙猫 ====================
    (function() {
        var pet = document.getElementById('desktop-pet');
        var pupilLeft = document.getElementById('pupil-left');
        var pupilRight = document.getElementById('pupil-right');
        var totoroBody = document.getElementById('totoro-body-group');
        var telescopeGroup = document.getElementById('telescope-group');

        if (!pet || !pupilLeft || !pupilRight) return;

        var petCenterX = 0, petCenterY = 0;
        var lastMouseX = 0, lastMouseY = 0;
        var idleTimer = null;
        var IDLE_THRESHOLD = 1500;

        function updatePetCenter() {
            var rect = pet.getBoundingClientRect();
            petCenterX = rect.left + rect.width / 2;
            petCenterY = rect.top + rect.height / 2;
        }

        var pupilBase = { lx: 63, ly: 82, rx: 97, ry: 82 };

        function updatePupils(dx, dy) {
            var dist = Math.sqrt(dx * dx + dy * dy) || 1;
            var factor = Math.min(dist / 400, 1);
            var px = (dx / dist) * 3 * factor;
            var py = (dy / dist) * 3 * factor;
            pupilLeft.setAttribute('cx', pupilBase.lx + px);
            pupilLeft.setAttribute('cy', pupilBase.ly + py);
            pupilRight.setAttribute('cx', pupilBase.rx + px);
            pupilRight.setAttribute('cy', pupilBase.ry + py);
        }

        function updateHeadTilt(dx, dy) {
            var angleY = Math.max(-15, Math.min(15, (dy / (window.innerHeight / 2)) * -15));
            totoroBody.style.transform = 'rotate(' + angleY + 'deg)';
            totoroBody.style.transformOrigin = '80px 135px';
        }

        function updateTelescope(dx, dy) {
            var angle = Math.atan2(dy, dx) * (180 / Math.PI);
            telescopeGroup.setAttribute('transform', 'rotate(' + (angle - 5) + ', 80, 85)');
        }

        function onMouseMove(e) {
            updatePetCenter();
            lastMouseX = e.clientX;
            lastMouseY = e.clientY;
            var dx = e.clientX - petCenterX;
            var dy = e.clientY - petCenterY;
            updatePupils(dx, dy);
            updateHeadTilt(dx, dy);

            if (document.body.classList.contains('pet-observing')) {
                document.body.classList.remove('pet-observing');
                telescopeGroup.setAttribute('opacity', '0');
            }

            clearTimeout(idleTimer);
            idleTimer = setTimeout(function () {
                document.body.classList.add('pet-observing');
                telescopeGroup.setAttribute('opacity', '1');
                updateTelescope(lastMouseX - petCenterX, lastMouseY - petCenterY);
            }, IDLE_THRESHOLD);
        }

        function randomBlink() {
            if (document.body.classList.contains('pet-observing')) return;
            pet.classList.add('blink');
            setTimeout(function () { pet.classList.remove('blink'); }, 200);
            setTimeout(randomBlink, 2000 + Math.random() * 5000);
        }

        updatePetCenter();
        document.addEventListener('mousemove', onMouseMove, { passive: true });
        window.addEventListener('resize', updatePetCenter);
        setTimeout(randomBlink, 3000 + Math.random() * 4000);
    })();

})();
