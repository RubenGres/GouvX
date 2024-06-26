chat_history = []
let message_count = 0

const gouvx_api_url = 'https://gouvx-api-h7ruetg7ga-uc.a.run.app';
//const gouvx_api_url = 'https://ominous-cod-777qq6x9q67cr7xx-8080.app.github.dev'

document.addEventListener("DOMContentLoaded", function () {
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");
        
    sendBtn.addEventListener("click", function () {
        const question = userInput.value.trim();
        ask_gouvx(question);
        }
    );

    userInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            sendBtn.click();
        }
    });
});

/* browser */
function set_browser_page(url) {
    // Check if the user is on a mobile device
    if (/Mobi|Android/i.test(navigator.userAgent)) {
        //open url in a new tab 
        window.open(url, '_blank');
        return;
    }

    const browserElement = document.getElementById('browser');
    
    browserElement.offsetHeight;
    browserElement.classList.add('visible');

    // Set iframe source to the first URL in uniqueItems
    const iframeElement = browserElement.querySelector('iframe');

    //clear the iframe before changing src
    iframeElement.src = '';
    iframeElement.src = gouvx_api_url + `/proxy?url=${encodeURIComponent(url)}`;
}

function close_browser() {
    const browserElement = document.getElementById('browser');
    browserElement.classList.remove('visible');
}

function highlight_browser() {
    const browserElement = document.getElementById('browser');
    browserElement.style.position = 'relative';

    const overlay = document.createElement('div');
    overlay.className = 'highlight-overlay';
    browserElement.appendChild(overlay);
}

function unhighlight_browser() {
    const browserElement = document.getElementById('browser');

    const overlay = browserElement.querySelector('.highlight-overlay');
    if (overlay) {
        browserElement.removeChild(overlay);
    }
}


function parse_response_metadata(metadata, message_number) {
    [metada_json, other_text] = metadata.split("\n")

    if (metada_json == "[]" || metada_json == "[null]"){
        return other_text
    }
    
    let lastbotsources = document.getElementById("botsources" + message_number);
    
    const jsonData = JSON.parse(metada_json);

    const uniqueItems = jsonData.filter((item, index, self) =>
        index === self.findIndex((t) => t.url === item.url)
    );

    const result = uniqueItems.map((item, index) => {
        const { title, url } = item;
        return `<span onmouseout="unhighlight_browser()" onmouseenter="highlight_browser()" onclick="set_browser_page('${url}')"><b>[${index + 1}]</b> ${title}</span>
        
        <a href="${url}" target="_blank class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="15" height="15" viewBox="0 0 30 30">
            <path d="M 25.980469 2.9902344 A 1.0001 1.0001 0 0 0 25.869141 3 L 20 3 A 1.0001 1.0001 0 1 0 20 5 L 23.585938 5 L 13.292969 15.292969 A 1.0001 1.0001 0 1 0 14.707031 16.707031 L 25 6.4140625 L 25 10 A 1.0001 1.0001 0 1 0 27 10 L 27 4.1269531 A 1.0001 1.0001 0 0 0 25.980469 2.9902344 z M 6 7 C 4.9069372 7 4 7.9069372 4 9 L 4 24 C 4 25.093063 4.9069372 26 6 26 L 21 26 C 22.093063 26 23 25.093063 23 24 L 23 14 L 23 11.421875 L 21 13.421875 L 21 16 L 21 24 L 6 24 L 6 9 L 14 9 L 16 9 L 16.578125 9 L 18.578125 7 L 16 7 L 14 7 L 6 7 z"></path>
            </svg>
        </a>
        `;
    });

    sources = result.join('<br>');
    lastbotsources.innerHTML = sources
    
    //only set the browser page if we are not on mobile
    if (!(/Mobi|Android/i.test(navigator.userAgent)))
        set_browser_page(uniqueItems[0].url);
    
    return other_text
}

function getCheckedCheckboxNames(parentDivId) {
    var checkedBoxes = document.querySelectorAll('#' + parentDivId + ' input[type="checkbox"]:checked');
    var names = [];
    
    checkedBoxes.forEach(function(checkbox) {
        names.push(checkbox.name);
    });

    return names;
}

function ask_gouvx(question) {
    const chatBox = document.getElementById("chat-box");

    // if div with class suggestions exist, remove it
    let suggestionsDiv = document.querySelector('.suggestions');
    if (suggestionsDiv) {
        suggestionsDiv.remove();
    }

    if (question !== "") {
        message_count += 1;

        const userMessage = document.createElement("div");
        userMessage.className = "message-box user";

        const userContainer = document.createElement("div");
        userContainer.className = "user";

        const profilePic = document.createElement("div");
        profilePic.className = "profile-pic";

        const messageContent = document.createElement("div");
        messageContent.className = "message";
        messageContent.textContent = question;

        userContainer.appendChild(messageContent);
        userContainer.appendChild(profilePic);
        userMessage.appendChild(userContainer);

        const modelSelect = document.getElementById('modelSelect');

        const botMessage = `
            <div class="message-box bot">
                <div class="bot">
                    <div class="profile-pic ${modelSelect.value}"></div>
                    <div class="message" id="botmessage${message_count}">
                        <div class="loading"></div>
                    </div>
                </div>

                <div class="sources" id="botsources${message_count}"></div>
            </div>
        `;

        chatBox.prepend(userMessage);
        chatBox.innerHTML = botMessage + chatBox.innerHTML;

        send_to_api(question, message_count);

        const userInput = document.getElementById("user-input");
        userInput.value = "";
        userInput.style.height = "45px";
    }
}

function send_to_api(question, message_number) {
    const modelSelect = document.getElementById('modelSelect');
    const use_vllm = modelSelect.value == "albert";

    const postData = new URLSearchParams({
        question: question,
        history: JSON.stringify(chat_history),
        sources: getCheckedCheckboxNames("sources"),
        use_vllm: modelSelect.value
    });

    const loader = document.querySelector('.loading')
    loader.classList.add('display')

    fetch(gouvx_api_url + "/ask/", {
        method: 'POST',
        body: postData,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
        .then(response => {
            const reader = response.body.getReader();
            const textDecoder = new TextDecoder();

            let system_reply = ""

            return new ReadableStream({
                async start(controller) {

                    const { done, value } = await reader.read();
                    let metadata = textDecoder.decode(value, { stream: true });

                    remaining_reply = parse_response_metadata(metadata, message_number)

                    //TODO make this a function
                    if (remaining_reply) {                        
                        let lastbotmessage = document.getElementById("botmessage" + message_number);
                        lastbotmessage.innerHTML += remaining_reply
                    }

                    while (true) {
                        const { done, value } = await reader.read();

                        if (done) {
                            controller.close();
                            break;
                        }

                        // Convert the chunk to a string and print it
                        let chunkText = textDecoder.decode(value, { stream: true });
                        system_reply += chunkText
                        chunkTextHTML = chunkText.replace("\n", "<br><br>")

                        let lastbotmessage = document.getElementById("botmessage" + message_number);
                        lastbotmessage.innerHTML += chunkTextHTML

                        controller.enqueue(value);
                    }
            
                    chat_history.push({
                        "role": "user",
                        "content": question
                    })
        
                    chat_history.push({
                        "role": "assistant",
                        "content": system_reply
                    })
                }
            });
        })
        .then(() => loader.remove())
        .then(stream => new Response(stream))
        .then(response => response.text())
        .then(data => {
            return data
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
