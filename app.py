import os
import json

import streamlit as st

from semantic_retrieval import rebuild_company_embeddings

from content_agent import (
    generate_linkedin_post,
    revise_linkedin_post,
    load_company_rules,
    suggest_linkedin_topics
)

from company_knowledge import (
    structure_company_information,
    save_company_knowledge,
    load_company_knowledge,
    update_company_knowledge,
    get_available_companies
)

from post_history import (
    save_approved_post,
    check_topic_similarity,
    check_post_similarity
)

if "post" not in st.session_state:
    st.session_state["post"] = None
if "approved" not in st.session_state:
    st.session_state["approved"] = False    
if "company_data" not in st.session_state:
    st.session_state["company_data"] = None

if "updated_company_data" not in st.session_state:
    st.session_state["updated_company_data"] = None

st.set_page_config(
    page_title="AI LinkedIn Content Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("AI LinkedIn Content Agent")
tab1, tab2, tab3 = st.tabs([
    "🏢 Company Knowledge",
    "📋 Company Rules",
    "✍️ Content Studio"
])


with tab1:
    st.subheader("Company Knowledge")

    company_text = st.text_area(
        "Add company information",
        placeholder=(
            "Paste any company information here...\n\n"
            "You can include company description, products, services, "
            "technologies, target customers, brand tone, restrictions, etc."
        ),
        height=300
    )

    process_company_info = st.button("🤖 Process Company Information")

    if process_company_info:

        if not company_text.strip():
            st.warning("Please add some company information first.")

        else:
            try:
                with st.spinner("Processing company information..."):
                    structured_company_data = structure_company_information(
                        company_text
                    )

                st.session_state["company_data"] = structured_company_data

                st.success("Company information processed successfully!")

            except Exception as error:
                st.error(
                    "Something went wrong while processing company information."
                )
                st.write(error)


    # Display the processed company information
    if st.session_state["company_data"] is not None:

        st.subheader("Structured Company Knowledge")
        st.json(st.session_state["company_data"])

        save_company_info = st.button("💾 Save Company Knowledge") 

        if save_company_info:
            try:
                file_path = save_company_knowledge(
                    st.session_state["company_data"]
                )
                rebuild_company_embeddings(file_path)

                st.success(
                    f"Company knowledge saved successfully: {file_path}"
                )

            except Exception as error:
                st.error("Could not save company knowledge.")
                st.write(error)


    st.divider()
    st.subheader("Update Existing Company")

    companies = get_available_companies()

    if companies:

        company_names = [
            company["name"]
            for company in companies
        ]

        selected_company_name = st.selectbox(
            "Select company",
            company_names
        )
        selected_company = next(
        company
        for company in companies
        if company["name"] == selected_company_name
        )

        new_information = st.text_area(
            "Add new information",
            placeholder="Example: We now also provide AI consulting services.",
            height=150
        )

        process_update = st.button("🤖 Process Update")

        if process_update:

            if not new_information.strip():
                st.warning("Please add new company information.")

            else:
                try:
                    with st.spinner("Updating company knowledge..."):

                        existing_data = load_company_knowledge(
                            selected_company["file_path"]
                        )

                        updated_data = update_company_knowledge(
                            existing_data,
                            new_information
                        )

                    #st.session_state["company_data"] = updated_data
                    st.session_state["updated_company_data"] = updated_data
                    st.success("Company knowledge update processed successfully!")

                except Exception as error:
                    st.error("Something went wrong while updating company knowledge.")
                    st.write(error)

        if st.session_state["updated_company_data"] is not None:

            st.subheader("Updated Company Knowledge")

            st.json(
                st.session_state["updated_company_data"]
            )

            confirm_update = st.button("💾 Confirm Update")

            if confirm_update:

                try:
                    file_path = save_company_knowledge(
                        st.session_state["updated_company_data"]
                    )
                    rebuild_company_embeddings(file_path)

                    st.success(
                        f"Company knowledge updated successfully: {file_path}"
                    )

                    st.session_state["updated_company_data"] = None

                    #st.rerun()

                except Exception as error:
                    st.error("Could not save the updated company knowledge.")
                    st.write(error)

with tab2:
    st.subheader("📋 Company Rules")

    companies = get_available_companies()

    if not companies:
        st.warning("No companies found. Please add company knowledge first.")
    else:
        company_names = [
            company["name"]
            for company in companies
        ]

        selected_rules_company_name = st.selectbox(
            "Select company",
            company_names,
            key="rules_company_selector"
        )

        selected_rules_company = next(
            company
            for company in companies
            if company["name"] == selected_rules_company_name
        )

        company_rules = load_company_rules(
            selected_rules_company["file_path"]
        )
        existing_post_rules = []

        if company_rules:
            existing_post_rules = company_rules.get(
                "post_rules",
                []
            )

        existing_rules_text = "\n".join(
            existing_post_rules
        )

        if company_rules:
            st.success("Company rules are saved.")
        else:
            st.info("No company-specific rules added yet.")

        edit_rules = st.button(
            "✏️ View / Edit Rules",
            key="edit_company_rules"
        )

        if edit_rules:
            st.session_state["show_company_rules"] = True

        if st.session_state.get("show_company_rules", False):
            st.write("Rules that should apply to all posts:")

            
            rules_text = st.text_area(
            "Company rules",
            value=existing_rules_text,
            height=250,
            key=f"company_rules_editor_{selected_rules_company_name}"
            )

            save_rules = st.button(
                "💾 Save Changes",
                key="save_company_rules"
            )
            if save_rules:

                new_rules = [
                    rule.strip()
                    for rule in rules_text.splitlines()
                    if rule.strip()
                ]

                if company_rules is None:
                    company_rules = {}

                company_rules["post_rules"] = new_rules

                company_folder = os.path.dirname(
                    selected_rules_company["file_path"]
                )

                rules_file = os.path.join(
                    company_folder,
                    "rules.json"
                )

                with open(rules_file, "w", encoding="utf-8") as file:
                    json.dump(
                        company_rules,
                        file,
                        ensure_ascii=False,
                        indent=2
                    )

                st.success("Rules saved successfully.")
with tab3:
  
    st.subheader("✍️ Content Studio")

    if st.session_state.pop("post_saved_successfully", False):
        st.success("✅ Post approved and saved to history.")

    companies = get_available_companies()

    company_names = [
        company["name"]
        for company in companies
    ]

    selected_content_company_name = st.selectbox(
        "Select company",
        company_names,
        key="content_company_selector"
    )

    selected_content_company = next(
        company
        for company in companies
        if company["name"] == selected_content_company_name
    )


    if "last_content_company" not in st.session_state:
        st.session_state["last_content_company"] = selected_content_company_name

    elif st.session_state["last_content_company"] != selected_content_company_name:

        keys_to_clear = [
            "suggested_topics",
            "selected_suggested_topic",
            "post",
            "selected_topic",
            "selected_angle",
            "approved",
            "post_feedback"
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.session_state["last_content_company"] = selected_content_company_name


    language = st.selectbox(
        "Language",
        ["English", "Finnish"],
        key="content_language"
    )

    if "last_content_language" not in st.session_state:
        st.session_state["last_content_language"] = language

    elif st.session_state["last_content_language"] != language:

        keys_to_clear = [
            "suggested_topics",
            "selected_suggested_topic",
            "post",
            "selected_topic",
            "selected_angle",
            "approved",
            "post_feedback"
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.session_state["last_content_language"] = language


    if "suggested_topics" not in st.session_state:
        st.session_state["suggested_topics"] = None

    suggest_topics = st.button(
        "💡 Suggest New Topics",
        key="suggest_topics"
    )
  

    if suggest_topics:

        st.session_state.pop("post", None)
        st.session_state.pop("selected_topic", None)
        st.session_state.pop("selected_angle", None)
        st.session_state.pop("approved", None)
        st.session_state.pop("post_feedback", None)

        result = suggest_linkedin_topics(
            selected_content_company["file_path"],
            language
        )

        checked_topics = []

        for item in result["topics"]:

            similarity_result = check_topic_similarity(
                selected_content_company["file_path"],
                item["topic"],
                item["angle"]
            )

            item["similarity"] = similarity_result["similarity"]

            if similarity_result["similarity"] < 0.75:
                checked_topics.append(item)

        st.session_state["suggested_topics"] = checked_topics

    if st.session_state["suggested_topics"]:

        st.subheader("Suggested Topics")

        topic_options = []

        
        for item in st.session_state["suggested_topics"]:

            similarity = item.get("similarity", 0.0)

            if similarity >= 0.75:
                status = "⚠️ Similar to previous content"
            else:
                status = "✅ New"

            option = (
                f'{item["topic"]} — {item["angle"]} '
                f'| {status} '
                f'({similarity:.2f})'
            )

            topic_options.append(option)

            
        selected_topic_option = st.radio(
            "Choose a topic",
            topic_options,
            key="selected_suggested_topic"
        )

        use_custom_topic = st.checkbox(
            "✍️ Use my own topic instead",
            key="use_custom_topic"
        )

        custom_topic = ""
        custom_angle = ""

        if use_custom_topic:

            custom_topic = st.text_input(
                "Your topic",
                key="custom_topic"
            )

            custom_angle = st.text_input(
                "Optional angle",
                key="custom_angle"
            )

       
        if use_custom_topic and custom_topic.strip():

            selected_topic = custom_topic.strip()

            selected_angle = (
                custom_angle.strip()
                if custom_angle.strip()
                else "User-defined topic"
            )

        else:

            selected_index = topic_options.index(
                selected_topic_option
            )

            selected_topic_data = st.session_state["suggested_topics"][
                selected_index
            ]

            selected_topic = selected_topic_data["topic"]
            selected_angle = selected_topic_data["angle"]


        custom_topic_similarity = None

        if use_custom_topic and custom_topic.strip():

            similarity_result = check_topic_similarity(
                selected_content_company["file_path"],
                selected_topic,
                selected_angle
            )

            custom_topic_similarity = similarity_result["similarity"]

            if custom_topic_similarity >= 0.75:
                st.warning(
                    f"⚠️ This topic is similar to previous content "
                    f"(similarity: {custom_topic_similarity:.2f})"
                )
            else:
                st.success(
                    f"✅ This topic appears new "
                    f"(similarity: {custom_topic_similarity:.2f})"
                )
        generate_post = st.button(
            "✨ Generate Post",
            key="generate_selected_topic"
        )

        if generate_post:

            post = generate_linkedin_post(
                selected_topic,
                language,
                selected_content_company["file_path"]
            )
            
            st.session_state["post"] = post
            st.session_state["approved"] = False
            st.session_state["selected_topic"] = selected_topic
            st.session_state["selected_angle"] = selected_angle

            post_similarity_result = check_post_similarity(
                selected_content_company["file_path"],
                post
            )

            st.session_state["post_similarity"] = (
                post_similarity_result["similarity"]
            )

        if st.session_state.get("post"):

            st.subheader("Post Preview")

            similarity = st.session_state.get(
                "post_similarity",
                0.0
            )

            st.caption(
                f"Similarity to previous approved posts: {similarity:.2f}"
            )

            if similarity >= 0.80:
                st.warning(
                    "⚠️ This draft is very similar to a previous approved post."
                )
            else:
                st.success(
                    "✅ This draft appears sufficiently different from previous posts."
                )

            post = st.session_state["post"]

            st.markdown("### Hook")
            st.write(post.get("hook", ""))

            st.markdown("### Post")
            st.write(post.get("post", ""))

            st.markdown("### CTA")
            st.write(post.get("cta", ""))

            st.markdown("### Hashtags")

            hashtags = post.get("hashtags", [])

            if hashtags:
                st.write(" ".join(hashtags))   



            feedback = st.text_area(
                "Feedback",
                placeholder="Example: Make the post shorter and more practical.",
                key="post_feedback"
            )

            revise_post = st.button(
                "🔄 Revise Post",
                key="revise_generated_post"
            )

            if revise_post:

                if not feedback.strip():
                    st.warning("Please enter feedback first.")

                else:
                    revised_post = revise_linkedin_post(
                        st.session_state["post"],
                        feedback,
                        selected_content_company["file_path"]
                    )

                    st.session_state["post"] = revised_post
                    st.session_state["approved"] = False

                    post_similarity_result = check_post_similarity(
                        selected_content_company["file_path"],
                        revised_post
                    )

                    st.session_state["post_similarity"] = (
                        post_similarity_result["similarity"]
                    )

                    st.rerun()     

            approve_post = st.button(
                "✅ Approve Post",
                key="approve_generated_post"
            )


            if approve_post:

                if not st.session_state.get("approved", False):

                    save_approved_post(
                        selected_content_company["file_path"],
                        st.session_state["selected_topic"],
                        st.session_state["selected_angle"],
                        st.session_state["post"]
                    )

                    st.session_state["post_saved_successfully"] = True

                    # Clear the current content workflow
                    keys_to_clear = [
                        "post",
                        "selected_topic",
                        "selected_angle",
                        "suggested_topics",
                        "selected_suggested_topic",
                        "post_feedback",
                        "post_similarity",
                        "approved",
                        "use_custom_topic",
                        "custom_topic",
                        "custom_angle"
                    ]

                    for key in keys_to_clear:
                        st.session_state.pop(key, None)

                    st.rerun()

                else:
                    st.info("This post is already approved.")
            
            
