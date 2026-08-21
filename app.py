import streamlit as st
from content_agent import generate_linkedin_post
from retrieval import retrieve_company_info

st.set_page_config(
    page_title="AI LinkedIn Content Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("AI LinkedIn Content Agent")
st.caption(
    "Generate company-specific LinkedIn content using structured knowledge and AI."
)

st.divider()
topic = st.text_input("Post topic")

post_type = st.selectbox(
    "Post type",
    [
        "Product post",
        "Educational post",
        "Industry insight",
        "Technical post"
    ]
)
language = st.selectbox(
    "Language",
    [
        "English",
        "Finnish"
    ]
)

tone = st.selectbox(
    "Tone",
    [
        "Professional",
        "Clear and educational",
        "Friendly",
        "Thought leadership"
    ]
)

post_length = st.selectbox(
    "Post length",
    [
        "Short",
        "Medium",
        "Long"
    ]
)

if st.button("Generate Post"):

    if not topic.strip():
        st.warning("Please enter a post topic.")

    else:
        try:
            with st.spinner("Generating LinkedIn post..."):
                post = generate_linkedin_post(
                    topic,
                    post_type,
                    language,
                    tone,
                    post_length
                )

            st.success("Post generated successfully!")

            st.subheader("Hook")
            st.write(post.get("hook", "No hook generated."))

            st.subheader("Post")
            st.write(post.get("post", "No post content generated."))

            st.subheader("CTA")
            st.write(post.get("cta", "No CTA generated."))

            st.subheader("Hashtags")

            hashtags = post.get("hashtags", [])

            if hashtags:
                st.write(" ".join(hashtags))
            else:
                st.write("No hashtags generated.")

        except Exception as error:
            st.error("Something went wrong while generating the post.")
            st.write(error)