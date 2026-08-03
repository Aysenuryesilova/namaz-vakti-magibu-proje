---

## 🚀 Live Demo and Operating Links

> 📌 **Important Note:** Due to the free CPU/hardware and quota limitations on Hugging Face Space, a **Google Colab Live Demo** environment has been created in order to test the application without interruption.

- 🟢 **Google Colab Live Demo (Recommended Live Environment):** [Colab Demo Notebook](https://colab.research.google.com/github/Aysenuryesilova/namaz-vakti-magibu-proje/blob/main/src/colab_demo.ipynb)
- 🟡 **Hugging Face Space:** [Aysenur44/ezan-vakti-ai-assistant](https://huggingface.co/spaces/Aysenur44/ezan-vakti-ai-assistant)
- 🔗 **GitHub Source Code Repository:** [Aysenuryesilova/namaz-vakti-magibu-proje](https://github.com/Aysenuryesilova/namaz-vakti-magibu-proje)

---

## 📑 File List and Responsibility Map

|  File Name |  Duties / Responsibilities |  Related Assignment |
|  :------------------------- |  :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |  :-------------------- |
|  **`chat_template.jinja`** |  Jinja2 template with ChatML standard that allows the model to distinguish between system, user, assistant and vehicle messages.                                                         |  **1.  Assignment** |
|  **`test_template.py`** |  Test script to verify whether the Jinja2 template independently produces ChatML output.                                                                             |  **1.  Assignment** |
|  **`database.py`** |  Opens connection to SQLite database (`islamic_assistant.db`), creates/updates tables;  Provides Data Writing (INSERT), Reading (SELECT) and Search (LIKE) functions.     |  **2.  Assignment (DB)** |
|  **`tools.py`** |  Wraps external Aladhan Public REST API call (`get_prayer_times`) and database functions.  Contains the OpenAI/HF compatible `TOOLS_SCHEMA` JSON definition for the model.  |  **2.  Homework (Tools)** |
|  **`agent.py`** |  It is the Agent Engine (`IslamicToolCallingAgent`) that creates the Jinja2 prompt, calls the right tool by analyzing the user's intention and keeps a step-by-step **Trace Log** record.   |  **2.  Homework (Engine)** |
|  **`app.py`** |  Gradio is a compatible web interface.  It offers chat screen, Trace Log viewer, live database panel and client settings.                                                    |  **2.  Assignment (UI)** |
|  **`requirements.txt`** |  List of dependencies needed by the project (`gradio`, `requests`, `jinja2`).                                                                                            |  **Common** |
|  **`islamic_assistant.db`** |  Local SQLite database file (contains the `user_inquiries` table).                                                                                                     |  **2.  Assignment (DB Data)** |

---

## 🧱 Modular Data Flow and Architecture

```text
                                  +------------------------------------+
                                  |     app.py (Gradio) |
                                  +------------------------------------+
                                              |
                                              v
                                  +------------------------------------+
                                  |    agent.py (Agent) |
                                  +------------------------------------+
                                    /\
                                   /\
                                  v v
               +------------------------------------+ +----------------------+
               |  chat_template.jinja |      |     tools.py (Tools) |
               |  (Prompt Formatting) |      +------------------------------------+
               +------------------------------------+/\
                                             /\
                                            v v
                           +------------+ +------------+
                           |   Aladhan Public API |    |   database.py (SQLite) |
                           |  (Prayer Times Service) |    |  (user_inquiries Table) |
                           +------------+ +------------+

```

## Terminal/log ekran görüntüsü:
<img width="1916" height="909" alt="{40C69291-C862-4C2F-B072-42D06E16C490}" src="https://github.com/user-attachments/assets/005f89e1-95ec-400f-b055-310d6e11a898" />

<img width="1919" height="905" alt="{825E0E75-EEE9-4E3E-9E84-FECE6CAB2E30}" src="https://github.com/user-attachments/assets/4a68afaf-2e2e-4f6b-87a6-a5eb56125eef" />

<img width="1913" height="887" alt="{076AFA8F-457C-424E-8372-DD465F769779}" src="https://github.com/user-attachments/assets/e763faeb-6920-47e5-bf38-83929e774e35" />

<img width="1911" height="901" alt="{66707C19-E70C-4F96-B381-8458B295114B}" src="https://github.com/user-attachments/assets/13c06ae8-a115-42e7-85b0-1f7b15a6b002" />




## ⚙️ Background Tool-Call & Trace Log Output (Sample Run)

Raw Trace Log record produced in the background while running the application via test_template.py or agent.py:

=== ASSIGNMENT 1: CUSTOM JINJA2 CHAT TEMPLATE OUTPUT ===
<|im_start|>system
You are a competent, reliable Religious Studies, Prayer Time and Jurisprudence Assistant.  By using available tools, you produce correct answers without hallucinating.

Available Tools:
[
{
"description": "Returns prayer times for the specified city.",
"name": "get_namaz_time",
"parameters": {
"properties": {
"city": {
"description": "City name (Ex: Istanbul)",
"type": "string"
}
},
"required": [
"city"
],
"type": "object"
}
}
]
When you want to call a function, produce the output in the following format: <tool_call>{"name": "function_name", "arguments": {...}}</tool_call><|im_end|>
<|im_start|>user
What time will the evening adhan be recited for Istanbul today?<|im_end|>
<|im_start|>assistant
