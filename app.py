if st.button("🚀 Start Production Line"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating script (this might take 30 seconds)..."):
            try:
                # 1. SETUP SAFETY SETTINGS
                # This stops the "Generation Failed" error for religious topics
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]

                # 2. GENERATE WITH SAFETY SETTINGS
                prompt = f"Create a short, emotional, and viral Islamic TikTok script about: {topic}. Include a relevant Quran verse and a reminder at the end."
                
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings
                )
                
                # 3. DISPLAY RESULTS
                if response.text:
                    st.success("✅ Script Generated!")
                    st.subheader("Your TikTok Script:")
                    st.write(response.text)
                else:
                    st.error("❌ The AI produced an empty response. Try a different topic.")

            except Exception as e:
                st.error(f"❌ Generation failed: {e}")
                st.info("Tip: Check your logs to see the specific error code.")
