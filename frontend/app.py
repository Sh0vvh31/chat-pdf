import streamlit as st
import api_client
import tempfile
import os

st.set_page_config(page_title="ChatPDF - XAI Supported", layout="wide")

# セッションステート初期化
if "user_token" not in st.session_state:
    st.session_state.user_token = None
    st.session_state.user_id = None
    st.session_state.username = None

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None
    st.session_state.current_document_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "language" not in st.session_state:
    st.session_state.language = "ja"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemma:2b"

def show_login_page():
    st.title("ChatPDF Login")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                res = api_client.login(login_user, login_pass)
                st.session_state.user_token = res["access_token"]
                st.session_state.user_id = res["user_id"]
                st.session_state.username = res["username"]
                st.success("Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
                
    with col2:
        st.subheader("Register")
        reg_user = st.text_input("Username", key="reg_user")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            try:
                res = api_client.register(reg_user, reg_pass)
                st.success(f"Registered user: {res['username']}! Please login.")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

def handle_file_upload():
    st.sidebar.subheader("Document Upload")
    uploaded_file = st.sidebar.file_uploader("Drag and drop PDF here", type=["pdf"])
    if uploaded_file is not None and st.sidebar.button("Upload and Process"):
        with st.spinner('Uploading and processing document...'):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
                
            try:
                res = api_client.upload_document(
                    user_id=st.session_state.user_id,
                    file_path=tmp_path,
                    filename=uploaded_file.name
                )
                st.session_state.current_document_id = res["document_id"]
                
                # 新しいスレッドの作成
                thread_res = api_client.create_thread(
                    user_id=st.session_state.user_id,
                    document_id=res["document_id"],
                    title=f"Chat on {uploaded_file.name}"
                )
                st.session_state.current_thread_id = thread_res["thread_id"]
                st.session_state.messages = [] # Reset UI messages
                st.sidebar.success("Ready to chat!")
            except Exception as e:
                st.sidebar.error(f"Upload failed: {str(e)}")
            finally:
                os.unlink(tmp_path)

def show_chat_page():
    # サイドバー: 言語設定・モデル選択・PDFアップロード
    st.sidebar.title(f"Settings ({st.session_state.username})")
    
    # 精度 vs スピード（モデル選択）
    st.sidebar.subheader("AI Model Selection")
    model_options = {
        "Fast (gemma:2b)": "gemma:2b",
        "Accurate (llama3)": "llama3",
        "Accurate (gemma:7b)": "gemma:7b",
        "Accurate (mistral)": "mistral"
    }
    selected_label = st.sidebar.selectbox(
        "Choose Engine", 
        list(model_options.keys())
    )
    st.session_state.selected_model = model_options[selected_label]
    
    st.session_state.language = st.sidebar.selectbox(
        "Language", 
        ["ja", "en"], 
        index=0 if st.session_state.language == "ja" else 1
    )
    
    if st.sidebar.button("Logout"):
        st.session_state.user_token = None
        st.session_state.user_id = None
        st.rerun()
        
    st.sidebar.markdown("---")
    handle_file_upload()
    
    # メインページ
    st.title("ChatPDF - RAG with Explainable AI")
    
    if not st.session_state.current_thread_id:
        st.info("Please upload a PDF document from the sidebar to start a new chat.")
        return
        
    # メッセージの描画
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # XAI ソースデータの表示（ある場合）
            if msg.get("sources") and "retrieved_chunks" in msg["sources"]:
                with st.expander("Show AI Reasoning Database Sources (XAI)"):
                    st.write(f"Model Used: {msg['sources'].get('model_used')}")
                    for i, chunk in enumerate(msg["sources"]["retrieved_chunks"]):
                        st.markdown(f"**Source {i+1} (Distance: {chunk.get('distance', 'N/A')}):**")
                        st.text(chunk.get("content", ""))
                        st.json(chunk.get("metadata", {}))
                            
    # 入力フォーム
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # UIに即時反映
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt, "sources": None})
        
        with st.spinner("AI is reasoning..."):
            try:
                res = api_client.send_chat_message(
                    user_id=st.session_state.user_id,
                    thread_id=st.session_state.current_thread_id,
                    question=prompt,
                    document_id=st.session_state.current_document_id,
                    model_name=st.session_state.selected_model
                )
                
                # UIにアシスタント応答を反映
                answer = res["answer"]
                sources = {"retrieved_chunks": res["sources"], "model_used": res["model_used"]}
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    with st.expander("Show AI Reasoning Database Sources (XAI)"):
                        st.write(f"Model Used: {sources['model_used']}")
                        for i, chunk in enumerate(sources["retrieved_chunks"]):
                            st.markdown(f"**Source {i+1} (Distance: {chunk.get('distance', 'N/A')}):**")
                            st.text(chunk.get("content", ""))
                            st.json(chunk.get("metadata", {}))
                            
                st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
                
            except Exception as e:
                st.error(f"Error communicating with AI: {str(e)}")

# ルーティング
if st.session_state.user_token is None:
    show_login_page()
else:
    show_chat_page()
