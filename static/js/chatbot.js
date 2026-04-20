document.addEventListener("DOMContentLoaded", function(){

const input = document.getElementById("chatInput");
const chatbox = document.getElementById("chatbox");
const fileInput = document.getElementById("chatImages");
const toggleBtn = document.getElementById("chatbot-toggle");
const chatbotContainer = document.getElementById("chatbot-container");
const minimizeBtn = document.getElementById("chatbot-minimize");

if(toggleBtn){
    toggleBtn.onclick = () => {
        chatbotContainer.classList.add("open");

        // 🔥 HIDE ICON
        toggleBtn.style.display = "none";
    };
}

if(minimizeBtn){
    minimizeBtn.onclick = () => {
        chatbotContainer.classList.remove("open");

        // 🔥 SHOW ICON AGAIN
        toggleBtn.style.display = "flex";
    };
}
toggleBtn.onclick = () => {
    chatbotContainer.classList.add("open");
    toggleBtn.classList.add("hidden");
};

minimizeBtn.onclick = () => {
    chatbotContainer.classList.remove("open");
    toggleBtn.classList.remove("hidden");
};

if(!input || !chatbox) return;

// ================= GLOBAL STATE =================
let chatbotData = {};
let currentField = null;

// ================= UI =================
function appendMessage(text){
    chatbox.innerHTML += "<div>" + text + "</div>";
    chatbox.scrollTop = chatbox.scrollHeight;
}

// ================= BUTTON CLICK =================
window.handleOptionClick = function(btn, value){

    document.querySelectorAll(".chat-option").forEach(b=> b.disabled = true);

    // 🔥 FIXED INSPECTION TYPE (MATCHES MODEL)
    if(currentField === "inspection_type"){
        let val = value.toLowerCase();

        if(val.includes("home") || val.includes("visit")){
            chatbotData["inspection_type"] = "visit";   // ✅ We visit you
        } 
        else if(val.includes("showroom") || val.includes("bring")){
            chatbotData["inspection_type"] = "bring";   // ✅ Bring to showroom
        }
    } 
    else if(currentField){
        chatbotData[currentField] = value;
    }

    console.log("DATA:", chatbotData);

    sendMessage(value);
};

// ================= SEND MESSAGE =================
function sendMessage(msg){

    input.disabled = true;

    if(msg !== ""){
        appendMessage("<b>You:</b> " + msg);
    }

    let formData = new FormData();
    formData.append("message", msg);

    // attach chatbot data
    for(let key in chatbotData){
        formData.append(key, chatbotData[key]);
    }

    // 🔥 ONLY send images when uploading
    if(msg === "upload_images" && fileInput && fileInput.files.length > 0){
        for(let i=0; i<fileInput.files.length; i++){
            formData.append("images", fileInput.files[i]);
        }
    }
    // 🔥 SHOW PROCESSING MESSAGE
    appendMessage("<b>Bot:</b> Processing your request... Please wait.");
    fetch("/chatbot/api/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {

        console.log("BOT RESPONSE:", data);

        appendMessage("<b>Bot:</b> " + (data.reply || "⚠️ No response"));

        // ================= FIELD DETECTION =================
        if(data.reply){
            let r = data.reply.toLowerCase();

            if(r.includes("your name")) currentField = "owner_name";
            else if(r.includes("phone")) currentField = "phone";
            else if(r.includes("car_brand") || r.includes("car brand")) currentField = "car_brand";
            else if(r.includes("car_model") || r.includes("car model")) currentField = "car_model";
            else if(r.includes("year")) currentField = "year";
            else if(r.includes("mileage")) currentField = "mileage";
            else if(r.includes("inspection")) currentField = "inspection_type";
            else if(r.includes("preferred_date")) currentField = "preferred_date";
            else currentField = null;
        }

        // ================= OPTIONS =================
        if(data.options){
            data.options.forEach(opt=>{
                chatbox.innerHTML += `
                <button class="chat-option" onclick="handleOptionClick(this,'${opt}')">
                    ${opt}
                </button>`;
            });
        }

        // ================= CAR RESULTS =================
        if(data.cars){
            data.cars.forEach(c=>{
                chatbox.innerHTML += `
                <div style="border-top:1px solid #333;padding-top:5px;">
                    🚗 ${c.brand} ${c.model}<br>
                    📅 ${c.year}<br>
                    💰 NPR ${c.price}
                </div>`;
            });
        }

        // ================= IMAGE STEP =================
        if(data.reply && data.reply.includes("Upload car images")){

            fileInput.style.display = "block";

            fileInput.click();

            fileInput.onchange = function(){
                sendMessage("upload_images");
                fileInput.onchange = null; // prevent loop
            };

        } else {
            fileInput.style.display = "none";
        }

        // ================= RESET AFTER SELL =================
        if(data.reply && data.reply.includes("Sell request submitted")){

            chatbotData = {};
            currentField = null;

            if(fileInput){
                fileInput.value = "";
                fileInput.onchange = null;
            }

            setTimeout(()=>{
                sendMessage("");
            }, 500);
        }

        input.disabled = false;

        // 🔥 AUTO FOCUS
        setTimeout(() => {
            input.focus();
        }, 50);
    })
    .catch(err => {
        console.error(err);
        appendMessage("<b>Bot:</b> ⚠️ Error occurred");
        input.disabled = false;
    });
}

// ================= TEXT INPUT =================
input.addEventListener("keypress", e=>{
    if(e.key === "Enter"){

        if(currentField){

            if(currentField === "inspection_type"){
                let val = input.value.toLowerCase();

                if(val.includes("home") || val.includes("visit")){
                    chatbotData["inspection_type"] = "visit";
                } 
                else if(val.includes("showroom") || val.includes("bring")){
                    chatbotData["inspection_type"] = "bring";
                }
            } 
            else {
                chatbotData[currentField] = input.value;
            }
        }

        let value = input.value;

        sendMessage(value);

        input.value = "";

        // 🔥 keep focus immediately
        input.focus();
    }
});

// ================= INITIAL LOAD =================
setTimeout(()=>{
    sendMessage("");
}, 300);

});