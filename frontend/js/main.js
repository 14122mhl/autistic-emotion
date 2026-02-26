// 全局变量
let currentRequestId = "";

// 页面加载完成后绑定事件
document.addEventListener("DOMContentLoaded", function() {
    const uploadBtn = document.getElementById("uploadBtn");
    const queryBtn = document.getElementById("queryBtn");
    const imageInput = document.getElementById("imageInput");
    const resultArea = document.getElementById("resultArea");
    const msgArea = document.getElementById("msgArea");

    // 上传并识别按钮点击事件
    uploadBtn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        const file = imageInput.files[0];
        if (!file) {
            msgArea.textContent = "请选择要上传的图片";
            msgArea.style.color = "#e17055";
            return;
        }

        // 显示加载状态
        msgArea.textContent = "正在上传和识别...";
        msgArea.style.color = "#6a11cb";
        uploadBtn.disabled = true;

        // 构建FormData
        const formData = new FormData();
        formData.append("image", file);

        // 发送请求
        fetch("http://192.168.50.49:5000/api/emotion/detect", {
            method: "POST",
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            uploadBtn.disabled = false;
            
            if (data.request_id) {
                // 显示结果
                resultArea.style.display = "block";
                document.getElementById("requestId").textContent = data.request_id;
                document.getElementById("emotion").textContent = data.emotion;
                document.getElementById("confidence").textContent = data.confidence;
                document.getElementById("detectTime").textContent = data.detect_time;

                currentRequestId = data.request_id;
                msgArea.textContent = "识别成功";
                msgArea.style.color = "#00b894";
                
                // 滚动到底部
                resultArea.scrollIntoView({ behavior: 'smooth' });
            } else {
                msgArea.textContent = data.error || "识别失败";
                msgArea.style.color = "#e17055";
            }
        })
        .catch(error => {
            uploadBtn.disabled = false;
            msgArea.textContent = "请求失败：" + error.message;
            msgArea.style.color = "#e17055";
            console.error("Error:", error);
        });
    });

    // 重新查询结果按钮点击事件
    queryBtn.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!currentRequestId) {
            msgArea.textContent = "暂无请求ID";
            msgArea.style.color = "#e17055";
            return;
        }

        // 显示加载状态
        msgArea.textContent = "正在查询结果...";
        msgArea.style.color = "#6a11cb";
        queryBtn.disabled = true;

        fetch(`http://192.168.50.49:5000/api/emotion/query/${currentRequestId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            queryBtn.disabled = false;
            
            if (data.request_id) {
                document.getElementById("emotion").textContent = data.emotion;
                document.getElementById("confidence").textContent = data.confidence;
                document.getElementById("detectTime").textContent = data.detect_time;
                msgArea.textContent = "查询成功";
                msgArea.style.color = "#00b894";
            } else {
                msgArea.textContent = data.error || "查询失败";
                msgArea.style.color = "#e17055";
            }
        })
        .catch(error => {
            queryBtn.disabled = false;
            msgArea.textContent = "查询失败：" + error.message;
            msgArea.style.color = "#e17055";
            console.error("Error:", error);
        });
    });
});
