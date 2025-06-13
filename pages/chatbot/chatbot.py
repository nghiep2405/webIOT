import streamlit.components.v1 as components
import streamlit as st
# 
st.title("🤖 Chatbot"
         , help="Chat with our AI assistant to get answers to your questions or help with tasks.")

components.html(
        """
        <style>
        </style>
        <div id="chatbase-container"></div>
        <script>
        (function(){
            if(!window.chatbase || window.chatbase("getState") !== "initialized") {
                window.chatbase = (...arguments) => {
                    if (!window.chatbase.q) window.chatbase.q = [];
                    window.chatbase.q.push(arguments);
                };
                window.chatbase = new Proxy(window.chatbase, {
                    get(target, prop) {
                        if (prop === "q") return target.q;
                        return (...args) => target(prop, ...args);
                    }
                });
            }

            const onLoad = function() {
                const script = document.createElement("script");
                script.src = "https://www.chatbase.co/embed.min.js";
                script.id = "4GdZAgF-QDxeZqrOkYhSb";
                script.domain = "www.chatbase.co";
                document.body.appendChild(script);
            };

            if (document.readyState === "complete") {
                onLoad();
            } else {
                window.addEventListener("load", onLoad);
            }
        })();
        </script>
        """,
        height=670,
        width=600
    )