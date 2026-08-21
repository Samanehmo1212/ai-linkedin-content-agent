import json
import string

def load_company_info():
    with open("company_info.json", "r", encoding="utf-8") as file:
        company_info = json.load(file)

    return company_info


def retrieve_company_info(topic):
    company_info = load_company_info()

    if "raiqu" in topic.lower():
        main_product = company_info["main_product"]

        context = ""

        for key, value in main_product.items():
            context += f"{key}: {value}\n"

        return context
    #topic_words = topic.lower().split()
    stop_words = {
    "what", "is", "the", "a", "an",
    "of", "in", "to", "and", "for",
    "does", "do", "how", "who"
    }

    topic_words = [
        word.strip(string.punctuation)
        for word in topic.lower().split()
        if word not in stop_words
     ]

    clean_topic = " ".join(topic_words)
    results = []

    def search(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                search(value, f"{path} {key}")

        elif isinstance(data, list):
            for item in data:
                search(item, path)

        elif isinstance(data, str):
            text = f"{path} {data}".lower()

            #if any(word in text for word in topic_words):
               # results.append(data)
          
            score = 0

            for word in topic_words:
                if word in text:
                    score += 1

            #if topic.lower() in text:
              #  score += 2
            if clean_topic in text:
                score += 2  

            if score > 0:
                results.append((score, data))

    search(company_info)

    results.sort(reverse=True)
    results = results[:5]

    #context = ""

    #for score, text in results:
     #   context += text + "\n"
    context = ""

    for score, text in results:
        context += f"Score: {score} | {text}\n"
    
    return context


if __name__ == "__main__":
    
    question = input("Ask a question: ")
    context=retrieve_company_info(question)

    print("\nContext:")
    print(context)
    
      
    
    